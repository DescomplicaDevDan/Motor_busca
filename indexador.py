import os
import re
import pickle
import math


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
    texto = re.sub(r'[^a-z0-9áéíóúâêîôûãõç\s]', '', texto) 
    return [palavra for palavra in texto.split() if palavra]
       
def construir_indice_a_partir_de_arquivos(pasta_documentos='documentos'):
    
    print(f"Iniciando indexação na pasta: {pasta_documentos}...")
    
    if not os.path.exists(pasta_documentos):
        print(f"ERRO: A pasta '{pasta_documentos}' não foi encontrada.")
        return

    for nome_arquivo in os.listdir(pasta_documentos):
        caminho_completo = os.path.join(pasta_documentos, nome_arquivo)
        
        if not nome_arquivo.endswith('.txt') or os.path.isdir(caminho_completo):
            continue
            
        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            doc_id = nome_arquivo
            indexar_documento(doc_id, conteudo)
            print(f" -> Documento indexado: {doc_id}")
            
        except Exception as e:
            print(f"Erro ao processar {nome_arquivo}: {e}")

def buscar(query):

    query_palavras = pre_processar_texto(query)
    
    if not query_palavras:
        return []

    primeira_palavra = query_palavras[0]
    documentos_encontrados = set(INDICE_INVERTIDO.get(primeira_palavra, {}).keys())
    
    if not documentos_encontrados:
        return []
    
    for i in range(1, len(query_palavras)):
        palavra = query_palavras[i]
        proximos_resultados = set(INDICE_INVERTIDO.get(palavra, {}).keys())
        
        documentos_encontrados = documentos_encontrados.intersection(proximos_resultados) 
        
        if not documentos_encontrados:
            return []
    
    return sorted(list(documentos_encontrados))

def salvar_indice(indice_file='motor_indice.pkl'):

    print(f"\nSalvando índices em {indice_file}...")
    
    dados_a_salvar = {
        'indice_invertido': INDICE_INVERTIDO,
        'raiz_trie': RAIZ_TRIE,
        'documentos_ids': DOCUMENTOS_IDS
    }
    
    try:
        with open(indice_file, 'wb') as f:
            pickle.dump(dados_a_salvar, f)
        print("Índices salvos com sucesso!")
        return True
    except Exception as e:
        print(f"ERRO ao salvar o índice: {e}")
        return False
    
def carregar_indice(indice_file='motor_indice.pkl'):

    global INDICE_INVERTIDO, RAIZ_TRIE, DOCUMENTOS_IDS

    if not os.path.exists(indice_file):
        print(f"Arquivo de índice '{indice_file}' não encontrado. Iniciando re-indexação...")
        return False

    print(f"\nArquivo de índice '{indice_file}' encontrado. Carregando...")
    try:
        with open(indice_file, 'rb') as f:
            dados_carregados = pickle.load(f)

        INDICE_INVERTIDO.clear()
        INDICE_INVERTIDO.update(dados_carregados.get('indice_invertido', {}))

        RAIZ_TRIE = dados_carregados.get('raiz_trie', NoTrie())
        DOCUMENTOS_IDS.extend(dados_carregados.get('documentos_ids', []))
        
        print("Índices carregados com sucesso! Indexação pulada.")
        return True
    except Exception as e:
        print(f"ERRO ao carregar o índice: {e}. Reconstruindo índice.")
        return False
    
def indexar_documento(doc_id, texto):
    
    global INDICE_INVERTIDO
    palavras = pre_processar_texto(texto)
    
    frequencia_local = {}
    for palavra in palavras:
        frequencia_local[palavra] = frequencia_local.get(palavra, 0) + 1
        inserir_na_trie(palavra)
    
    for palavra, freq in frequencia_local.items():
        if palavra not in INDICE_INVERTIDO:
            INDICE_INVERTIDO[palavra] = {doc_id: freq}
        else:
            INDICE_INVERTIDO[palavra][doc_id] = freq

def construir_indice_a_partir_de_arquivos(pasta_documentos='documentos'):
    
    global DOCUMENTOS_IDS
    DOCUMENTOS_IDS.clear()
    
    print(f"Iniciando indexação na pasta: {pasta_documentos}...")   

    if not os.path.exists(pasta_documentos):
        print(f"ERRO: A pasta '{pasta_documentos}' não foi encontrada.")
        return

    for nome_arquivo in os.listdir(pasta_documentos):
        caminho_completo = os.path.join(pasta_documentos, nome_arquivo)

        if not nome_arquivo.endswith('.txt') or os.path.isdir(caminho_completo):
            continue

        try:
            with open(caminho_completo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            doc_id = nome_arquivo
            indexar_documento(doc_id, conteudo)
            DOCUMENTOS_IDS.append(doc_id)
            print(f" -> Documento indexado: {doc_id}")

        except Exception as e:
            print(f"Erro ao processar {nome_arquivo}: {e}")

def calcular_tf_idf(query):
    query_palavras = pre_processar_texto(query)

    if not query_palavras or not DOCUMENTOS_IDS:
        return []
    
    N = len(DOCUMENTOS_IDS)

    pontuacoes = {doc_id: 0.0 for doc_id in DOCUMENTOS_IDS}

    for palavra in query_palavras: # O loop começa aqui
        docs_com_termo = INDICE_INVERTIDO.get(palavra, {})
        
        # CORREÇÃO: Este IF precisa estar indentado (dentro do loop)
        if not docs_com_termo:
            continue

        num_docs_com_termo = len(docs_com_termo)
        idf = math.log(N / num_docs_com_termo)

        for doc_id, freq_termo in docs_com_termo.items():
            tf = freq_termo
            tf_idf = tf * idf
            pontuacoes[doc_id] += tf_idf

        resultados_ordenados = [
            (doc_id, pontuacao) 
            for doc_id, pontuacao in pontuacoes.items() 
            if pontuacao > 0
        ]
        resultados_ordenados.sort(key=lambda item: item[1], reverse=True)
    return resultados_ordenados

   
if __name__ == "__main__":

    indice_carregado = carregar_indice()

    if not indice_carregado:
        construir_indice_a_partir_de_arquivos()
        print("\n--- Índice Invertido e Trie Construídos ---")
        salvar_indice()
    
    print("\n--- Índices Prontos para Uso ---")

    print("\n--- TESTANDO BUSCAS (Índice Invertido) ---")

    consulta1 = "raposa"
    print(f"BUSCA BOLEANA '{consulta1}': {buscar(consulta1)}")
    print(f"BUSCA TF-IDF '{consulta1}': {calcular_tf_idf(consulta1)}")

    consulta2 = "cão preguiçoso"
    print(f"BUSCA BOLEANA '{consulta2}': {buscar(consulta2)}")
    print(f"BUSCA TF-IDF '{consulta2}': {calcular_tf_idf(consulta2)}")
    
    consulta3 = "projeto"
    print(f"BUSCA TF-IDF '{consulta3}': {calcular_tf_idf(consulta3)}")

    print("\n--- TESTANDO AUTOCOMPLETE (Trie) ---")
    print(f"AutoComplete 'ra': {buscar_prefixo('ra')}")
    print(f"AutoComplete 'pr': {buscar_prefixo('pr')}")
    print(f"AutoComplete 'xy': {buscar_prefixo('xy')}")

 

