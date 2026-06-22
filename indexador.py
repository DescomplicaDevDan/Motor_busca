"""Indexação, busca e persistência do motor de busca."""

import math
import json
import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_INDICE_PADRAO = BASE_DIR / "motor_indice.json"
PASTA_DOCUMENTOS_PADRAO = BASE_DIR / "documentos"
VERSAO_INDICE = 4

# Palavras muito frequentes que pouco ajudam a diferenciar documentos.
STOPWORDS_PT = {
    "a", "as", "ao", "aos", "à", "às", "com", "como", "da", "das", "de", "do", "dos",
    "e", "é", "em", "na", "nas", "no", "nos", "o", "os", "ou", "para", "por", "que", "um", "uma",
}
MODOS_BUSCA = {"qualquer", "todos"}

INDICE_INVERTIDO = {}
DOCUMENTOS_IDS = []
TAMANHOS_DOCUMENTOS = {}


class NoTrie:
    def __init__(self):
        self.filhos = {}
        self.fim_de_palavra = False


RAIZ_TRIE = NoTrie()


def inserir_na_trie(palavra):
    no_atual = RAIZ_TRIE
    for char in palavra:
        if char not in no_atual.filhos:
            no_atual.filhos[char] = NoTrie()
        no_atual = no_atual.filhos[char]
    no_atual.fim_de_palavra = True


def reconstruir_trie():
    """Reconstrói a Trie usando as palavras já existentes no índice invertido."""
    global RAIZ_TRIE
    RAIZ_TRIE = NoTrie()
    for palavra in INDICE_INVERTIDO:
        inserir_na_trie(palavra)


def _coletar_palavras_descendentes(no, prefixo_atual, lista_resultados):
    if no.fim_de_palavra:
        lista_resultados.append(prefixo_atual)
    for char, filho in no.filhos.items():
        _coletar_palavras_descendentes(filho, prefixo_atual + char, lista_resultados)


def buscar_prefixo(prefixo):
    no_atual = RAIZ_TRIE
    for char in prefixo:
        if char not in no_atual.filhos:
            return []
        no_atual = no_atual.filhos[char]

    palavras_com_prefixo = []
    _coletar_palavras_descendentes(no_atual, prefixo, palavras_com_prefixo)
    return palavras_com_prefixo


def pre_processar_texto(texto, remover_stopwords=True):
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9áéíóúâêîôûãõç\s]", "", texto)
    palavras = [palavra for palavra in texto.split() if palavra]
    if remover_stopwords:
        return [palavra for palavra in palavras if palavra not in STOPWORDS_PT]
    return palavras


def buscar(query, modo="todos"):
    """Busca booleana: retorna documentos que contêm todas as palavras."""
    query_palavras = pre_processar_texto(query)
    if not query_palavras or modo not in MODOS_BUSCA:
        return []

    conjuntos_documentos = [set(INDICE_INVERTIDO.get(palavra, {})) for palavra in query_palavras]
    if modo == "todos":
        documentos_encontrados = set.intersection(*conjuntos_documentos)
    else:
        documentos_encontrados = set.union(*conjuntos_documentos)
    return sorted(documentos_encontrados)


def salvar_indice(indice_file=ARQUIVO_INDICE_PADRAO):
    """Salva somente dados simples em JSON; a Trie é reconstruída na leitura."""
    indice_file = Path(indice_file)
    arquivo_temporario = indice_file.with_suffix(indice_file.suffix + ".tmp")
    dados_a_salvar = {
        "versao": VERSAO_INDICE,
        "indice_invertido": INDICE_INVERTIDO,
        "documentos_ids": DOCUMENTOS_IDS,
        "tamanhos_documentos": TAMANHOS_DOCUMENTOS,
    }
    try:
        with arquivo_temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(dados_a_salvar, arquivo, ensure_ascii=False, indent=2, sort_keys=True)
        arquivo_temporario.replace(indice_file)
        print(f"Índice salvo em {indice_file}.")
        return True
    except (OSError, TypeError) as erro:
        print(f"ERRO ao salvar o índice: {erro}")
        return False


def carregar_indice(indice_file=ARQUIVO_INDICE_PADRAO):
    """Carrega o índice e recria em memória a Trie derivada dele."""
    indice_file = Path(indice_file)
    if not indice_file.exists():
        print(f"Índice não encontrado: {indice_file}.")
        return False

    try:
        with indice_file.open("r", encoding="utf-8") as arquivo:
            dados_carregados = json.load(arquivo)

        if dados_carregados.get("versao") != VERSAO_INDICE:
            raise ValueError("versão de índice antiga ou desconhecida")
        indice = dados_carregados["indice_invertido"]
        documentos = dados_carregados["documentos_ids"]
        tamanhos = dados_carregados["tamanhos_documentos"]
        if not isinstance(indice, dict) or not isinstance(documentos, list) or not isinstance(tamanhos, dict):
            raise ValueError("formato de índice inválido")

        INDICE_INVERTIDO.clear()
        INDICE_INVERTIDO.update(indice)
        DOCUMENTOS_IDS.clear()
        DOCUMENTOS_IDS.extend(documentos)
        TAMANHOS_DOCUMENTOS.clear()
        TAMANHOS_DOCUMENTOS.update(tamanhos)
        reconstruir_trie()
        print("Índice carregado com sucesso.")
        return True
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, AttributeError, KeyError, TypeError, ValueError) as erro:
        print(f"Não foi possível carregar o índice ({erro}). Ele será recriado.")
        return False


def indexar_documento(doc_id, texto):
    palavras = pre_processar_texto(texto)
    TAMANHOS_DOCUMENTOS[doc_id] = len(palavras)
    frequencia_local = {}
    for palavra in palavras:
        frequencia_local[palavra] = frequencia_local.get(palavra, 0) + 1

    for palavra, frequencia in frequencia_local.items():
        INDICE_INVERTIDO.setdefault(palavra, {})[doc_id] = frequencia


def construir_indice_a_partir_de_arquivos(pasta_documentos=PASTA_DOCUMENTOS_PADRAO):
    """Cria um novo índice, descartando integralmente qualquer estado anterior."""
    pasta_documentos = Path(pasta_documentos)
    INDICE_INVERTIDO.clear()
    DOCUMENTOS_IDS.clear()
    TAMANHOS_DOCUMENTOS.clear()

    if not pasta_documentos.exists():
        raise FileNotFoundError(f"Pasta de documentos não encontrada: {pasta_documentos}")

    for caminho in sorted(pasta_documentos.glob("*.txt")):
        conteudo = caminho.read_text(encoding="utf-8")
        indexar_documento(caminho.name, conteudo)
        DOCUMENTOS_IDS.append(caminho.name)
        print(f" -> Documento indexado: {caminho.name}")

    reconstruir_trie()


def inicializar_indices():
    """Garante que o motor tenha um índice válido antes de atender buscas."""
    if not carregar_indice():
        construir_indice_a_partir_de_arquivos()
        if not salvar_indice():
            raise RuntimeError("O índice foi criado, mas não pôde ser salvo.")


def _calcular_idf(palavra):
    """IDF suavizado: termos muito comuns ainda recebem peso mínimo."""
    quantidade_documentos = len(DOCUMENTOS_IDS)
    quantidade_com_termo = len(INDICE_INVERTIDO.get(palavra, {}))
    return math.log((quantidade_documentos + 1) / (quantidade_com_termo + 1)) + 1


def _calcular_normas_documentos():
    """Calcula o tamanho de cada vetor TF-IDF normalizado."""
    normas_quadradas = {doc_id: 0.0 for doc_id in DOCUMENTOS_IDS}
    for palavra, ocorrencias in INDICE_INVERTIDO.items():
        idf = _calcular_idf(palavra)
        for doc_id, frequencia in ocorrencias.items():
            tf_normalizado = frequencia / TAMANHOS_DOCUMENTOS[doc_id]
            normas_quadradas[doc_id] += (tf_normalizado * idf) ** 2
    return {doc_id: math.sqrt(norma) for doc_id, norma in normas_quadradas.items()}


def calcular_tf_idf(query, modo="qualquer"):
    """Ranqeia documentos por similaridade do cosseno entre vetores TF-IDF."""
    query_palavras = pre_processar_texto(query)
    if not query_palavras or not DOCUMENTOS_IDS or modo not in MODOS_BUSCA:
        return []

    conjuntos_documentos = [set(INDICE_INVERTIDO.get(palavra, {})) for palavra in query_palavras]
    if modo == "todos":
        documentos_candidatos = set.intersection(*conjuntos_documentos)
    else:
        documentos_candidatos = set.union(*conjuntos_documentos)
    if not documentos_candidatos:
        return []

    frequencias_consulta = Counter(query_palavras)
    tamanho_consulta = len(query_palavras)
    pesos_consulta = {
        palavra: (frequencia / tamanho_consulta) * _calcular_idf(palavra)
        for palavra, frequencia in frequencias_consulta.items()
        if palavra in INDICE_INVERTIDO
    }
    norma_consulta = math.sqrt(sum(peso ** 2 for peso in pesos_consulta.values()))
    if not norma_consulta:
        return []

    normas_documentos = _calcular_normas_documentos()
    produtos_escalares = {doc_id: 0.0 for doc_id in documentos_candidatos}
    for palavra, peso_consulta in pesos_consulta.items():
        for doc_id, frequencia in INDICE_INVERTIDO[palavra].items():
            if doc_id in produtos_escalares:
                tf_normalizado = frequencia / TAMANHOS_DOCUMENTOS[doc_id]
                produtos_escalares[doc_id] += peso_consulta * tf_normalizado * _calcular_idf(palavra)

    resultados = [
        (doc_id, produto / (norma_consulta * normas_documentos[doc_id]))
        for doc_id, produto in produtos_escalares.items()
        if normas_documentos[doc_id] and produto > 0
    ]
    return sorted(resultados, key=lambda item: item[1], reverse=True)


def obter_trecho(doc_id, query, antes=70, depois=110):
    """Retorna uma janela do documento centrada no primeiro termo buscado.

    O índice guarda frequências, não o texto completo. Por isso o trecho é
    lido apenas para os documentos que já foram escolhidos pelo ranqueamento.
    """
    termos = pre_processar_texto(query)
    if not termos:
        return ""

    caminho_documento = PASTA_DOCUMENTOS_PADRAO / doc_id
    try:
        texto = caminho_documento.read_text(encoding="utf-8")
    except OSError:
        return ""

    padrao = r"\b(" + "|".join(re.escape(termo) for termo in termos) + r")\b"
    ocorrencia = re.search(padrao, texto, flags=re.IGNORECASE)
    if not ocorrencia:
        return ""

    inicio = max(0, ocorrencia.start() - antes)
    fim = min(len(texto), ocorrencia.end() + depois)
    trecho = " ".join(texto[inicio:fim].split())

    if inicio > 0:
        trecho = "… " + trecho
    if fim < len(texto):
        trecho += " …"
    return trecho


def dividir_trecho_para_destaque(trecho, query):
    """Separa o trecho e informa quais partes correspondem à consulta.

    A função não gera HTML. Ela devolve texto puro e um sinal booleano para o
    template decidir onde usar a marcação visual, preservando o autoescape do
    Jinja.
    """
    termos = pre_processar_texto(query)
    if not trecho or not termos:
        return [{"texto": trecho, "destacado": False}] if trecho else []

    padrao = re.compile(
        r"\b(" + "|".join(re.escape(termo) for termo in termos) + r")\b",
        flags=re.IGNORECASE,
    )
    return [
        {"texto": parte, "destacado": bool(padrao.fullmatch(parte))}
        for parte in padrao.split(trecho)
        if parte
    ]


if __name__ == "__main__":
    inicializar_indices()
    print("\n--- Índices prontos para uso ---")
    print("Busca booleana 'cão preguiçoso':", buscar("cão preguiçoso"))
    print("Busca TF-IDF 'raposa':", calcular_tf_idf("raposa"))
    print("Autocomplete 'ra':", buscar_prefixo("ra"))
