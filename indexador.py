import os
import re
import pickle

INDICE_INVERTIDO = {} 

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

def indexar_documento(doc_id, texto):
    
    global INDICE_INVERTIDO
    palavras = pre_processar_texto(texto)
    
    for palavra in palavras:
        inserir_na_trie(palavra)
        
        if palavra not in INDICE_INVERTIDO:
            INDICE_INVERTIDO[palavra] = [doc_id]
        elif doc_id not in INDICE_INVERTIDO[palavra]:
            INDICE_INVERTIDO[palavra].append(doc_id)

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
    documentos_encontrados = set(INDICE_INVERTIDO.get(primeira_palavra, []))
    
    if not documentos_encontrados:
        return []
    
    for i in range(1, len(query_palavras)):
        palavra = query_palavras[i]
        proximos_resultados = set(INDICE_INVERTIDO.get(palavra, []))
        
        documentos_encontrados = documentos_encontrados.intersection(proximos_resultados) 
        
        if not documentos_encontrados:
            return []
    
    return sorted(list(documentos_encontrados))

def salvar_indice(indice_file='motor_indice.pkl'):

    print(f"\nSalvando índices em {indice_file}...")
    
    dados_a_salvar = {
        'indice_invertido': INDICE_INVERTIDO,
        'raiz_trie': RAIZ_TRIE
    }
    
    try:
        with open(indice_file, 'wb') as f:
            pickle.dump(dados_a_salvar, f)
        print("Índices salvos com sucesso!")
        return True
    except Exception as e:
        print(f"ERRO ao salvar o índice: {e}")
        return False
   
if __name__ == "__main__":
    
    construir_indice_a_partir_de_arquivos()
    print("\n--- Índice Invertido Construído ---")
    
    salvar_indice()
    
    print("\n--- TESTANDO AUTOCOMPLETE (Trie) ---")
    
    prefixo1 = "ra"
    print(f"AutoComplete '{prefixo1}': {buscar_prefixo(prefixo1)}")

    prefixo2 = "pr"
    print(f"AutoComplete '{prefixo2}': {buscar_prefixo(prefixo2)}")
    
    prefixo3 = "xy"
    print(f"AutoComplete '{prefixo3}': {buscar_prefixo(prefixo3)}")

    print("\n--- TESTANDO BUSCA ---")
    query_teste = "projeto"
    print(f"Busca por '{query_teste}': Documentos -> {buscar(query_teste)}")