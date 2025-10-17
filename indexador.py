import os
import re

# Dicionário principal: nossa Tabela Hash/Índice Invertido
# Mapeia: {'palavra': [ID_Doc1, ID_Doc2, ...]}
INDICE_INVERTIDO = {} 

class NoTrie:
    """Representa um nó na Árvore Trie."""
    def __init__(self):
        self.filhos = {} 
        self.fim_de_palavra = False 

RAIZ_TRIE = NoTrie() 

def inserir_na_trie(palavra):
    """Insere uma palavra na Trie."""
    no_atual = RAIZ_TRIE
    for char in palavra:
        if char not in no_atual.filhos:
            no_atual.filhos[char] = NoTrie()
        no_atual = no_atual.filhos[char]
    no_atual.fim_de_palavra = True

def _coletar_palavras_descendentes(no, prefixo_atual, lista_resultados):
    """Função auxiliar recursiva (DFS) para encontrar todas as palavras."""
    if no.fim_de_palavra:
        lista_resultados.append(prefixo_atual)
    
    for char, filho in no.filhos.items():
        _coletar_palavras_descendentes(filho, prefixo_atual + char, lista_resultados)

def buscar_prefixo(prefixo):
    """Busca e retorna todas as palavras que começam com o prefixo dado."""
    no_atual = RAIZ_TRIE
    for char in prefixo:
        if char not in no_atual.filhos:
            return []  # Prefixo não existe
        no_atual = no_atual.filhos[char]
    
    palavras_com_prefixo = []
    _coletar_palavras_descendentes(no_atual, prefixo, palavras_com_prefixo)
    return palavras_com_prefixo

# ... (O restante do seu código vem aqui, como INDICE_INVERTIDO, pre_processar_texto, etc.)

def pre_processar_texto(texto):
    """
    Limpa o texto para garantir que a indexação seja uniforme.
    1. Converte para minúsculas.
    2. Remove pontuação.
    3. Retorna a lista de palavras (tokens).
    """
    texto = texto.lower()
    # Remove tudo que não for letra, número ou espaço (mantendo apenas o texto relevante)
    texto = re.sub(r'[^a-z0-9áéíóúâêîôûãõç\s]', '', texto) 
    # Divide em palavras e remove entradas vazias
    return [palavra for palavra in texto.split() if palavra]

def indexar_documento(doc_id, texto):
    """
    Processa um único documento e atualiza o INDICE_INVERTIDO.
    """
    global INDICE_INVERTIDO
    palavras = pre_processar_texto(texto)
    
    for palavra in palavras:
        # NOVO: Inserir na Árvore Trie
        inserir_na_trie(palavra)
        
        # Atualização do Índice Invertido (como antes)
        if palavra not in INDICE_INVERTIDO:
            INDICE_INVERTIDO[palavra] = [doc_id]
        elif doc_id not in INDICE_INVERTIDO[palavra]:
            INDICE_INVERTIDO[palavra].append(doc_id)

def construir_indice_a_partir_de_arquivos(pasta_documentos='documentos'):
    """
    Percorre a pasta 'documentos' e indexa cada arquivo.
    """
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
    """
    Busca documentos que contêm TODAS as palavras-chave na consulta (lógica AND).
    """
    query_palavras = pre_processar_texto(query)
    
    if not query_palavras:
        return []

    # Inicia o conjunto de resultados com os documentos da primeira palavra
    primeira_palavra = query_palavras[0]
    documentos_encontrados = set(INDICE_INVERTIDO.get(primeira_palavra, []))
    
    if not documentos_encontrados:
        return []
    
    # Faz a Interseção (lógica AND) com as palavras restantes
    for i in range(1, len(query_palavras)):
        palavra = query_palavras[i]
        proximos_resultados = set(INDICE_INVERTIDO.get(palavra, []))
        
        # Interseção: Mantém apenas os documentos presentes em TODOS os conjuntos
        documentos_encontrados = documentos_encontrados.intersection(proximos_resultados) 
        
        if not documentos_encontrados:
            return []
    
    return sorted(list(documentos_encontrados))

# --- Execução Principal e Testes ---
if __name__ == "__main__":
    
    # Antes de executar, certifique-se que a pasta 'documentos'
    # tem os arquivos doc1.txt, doc2.txt e doc3.txt dentro!

    construir_indice_a_partir_de_arquivos()
    print("\n--- Índice Invertido Construído ---")
    
    # -------------------------------------------------------------------
    # TESTES DE AUTOCOMPLETE (USANDO A TRIE)
    print("\n--- TESTANDO AUTOCOMPLETE (Trie) ---")
    
    # Teste 1: Prefixo "ra" (espera: 'raposa')
    prefixo1 = "ra"
    print(f"AutoComplete '{prefixo1}': {buscar_prefixo(prefixo1)}")

    # Teste 2: Prefixo "pr" (espera: 'projeto', 'preguiçoso')
    prefixo2 = "pr"
    print(f"AutoComplete '{prefixo2}': {buscar_prefixo(prefixo2)}")
    
    # Teste 3: Prefixo que não existe
    prefixo3 = "xy"
    print(f"AutoComplete '{prefixo3}': {buscar_prefixo(prefixo3)}")