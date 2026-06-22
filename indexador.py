"""Indexação, busca e persistência do motor de busca."""

import math
import pickle
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_INDICE_PADRAO = BASE_DIR / "motor_indice.pkl"
PASTA_DOCUMENTOS_PADRAO = BASE_DIR / "documentos"
VERSAO_INDICE = 2

INDICE_INVERTIDO = {}
DOCUMENTOS_IDS = []


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


def pre_processar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9áéíóúâêîôûãõç\s]", "", texto)
    return [palavra for palavra in texto.split() if palavra]


def buscar(query):
    """Busca booleana: retorna documentos que contêm todas as palavras."""
    query_palavras = pre_processar_texto(query)
    if not query_palavras:
        return []

    documentos_encontrados = set(INDICE_INVERTIDO.get(query_palavras[0], {}))
    for palavra in query_palavras[1:]:
        documentos_encontrados &= set(INDICE_INVERTIDO.get(palavra, {}))
        if not documentos_encontrados:
            return []
    return sorted(documentos_encontrados)


def salvar_indice(indice_file=ARQUIVO_INDICE_PADRAO):
    """Salva somente tipos simples; a Trie é reconstruída na leitura.

    Não serializar objetos ``NoTrie`` evita que o pickle dependa do nome do
    módulo que estava em execução quando o índice foi criado.
    """
    indice_file = Path(indice_file)
    dados_a_salvar = {
        "versao": VERSAO_INDICE,
        "indice_invertido": INDICE_INVERTIDO,
        "documentos_ids": DOCUMENTOS_IDS,
    }
    try:
        with indice_file.open("wb") as arquivo:
            pickle.dump(dados_a_salvar, arquivo)
        print(f"Índice salvo em {indice_file}.")
        return True
    except OSError as erro:
        print(f"ERRO ao salvar o índice: {erro}")
        return False


def carregar_indice(indice_file=ARQUIVO_INDICE_PADRAO):
    """Carrega o índice e recria em memória a Trie derivada dele."""
    indice_file = Path(indice_file)
    if not indice_file.exists():
        print(f"Índice não encontrado: {indice_file}.")
        return False

    try:
        with indice_file.open("rb") as arquivo:
            dados_carregados = pickle.load(arquivo)

        if dados_carregados.get("versao") != VERSAO_INDICE:
            raise ValueError("versão de índice antiga ou desconhecida")
        indice = dados_carregados["indice_invertido"]
        documentos = dados_carregados["documentos_ids"]
        if not isinstance(indice, dict) or not isinstance(documentos, list):
            raise ValueError("formato de índice inválido")

        INDICE_INVERTIDO.clear()
        INDICE_INVERTIDO.update(indice)
        DOCUMENTOS_IDS.clear()
        DOCUMENTOS_IDS.extend(documentos)
        reconstruir_trie()
        print("Índice carregado com sucesso.")
        return True
    except (OSError, pickle.UnpicklingError, AttributeError, EOFError, KeyError, ValueError) as erro:
        print(f"Não foi possível carregar o índice ({erro}). Ele será recriado.")
        return False


def indexar_documento(doc_id, texto):
    palavras = pre_processar_texto(texto)
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


def calcular_tf_idf(query):
    query_palavras = pre_processar_texto(query)
    if not query_palavras or not DOCUMENTOS_IDS:
        return []

    quantidade_documentos = len(DOCUMENTOS_IDS)
    pontuacoes = {doc_id: 0.0 for doc_id in DOCUMENTOS_IDS}

    for palavra in query_palavras:
        docs_com_termo = INDICE_INVERTIDO.get(palavra, {})
        if not docs_com_termo:
            continue

        idf = math.log(quantidade_documentos / len(docs_com_termo))
        for doc_id, frequencia_termo in docs_com_termo.items():
            pontuacoes[doc_id] += frequencia_termo * idf

    resultados = [(doc_id, pontuacao) for doc_id, pontuacao in pontuacoes.items() if pontuacao > 0]
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
