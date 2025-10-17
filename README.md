# 🔍 Motor de Busca Otimizado: TF-IDF, Trie e Persistência

## Visão Geral do Projeto

Este projeto demonstra a construção do "coração" de um motor de busca utilizando **Estruturas de Dados** e **Algoritmos Avançados** em Python. O motor não apenas encontra documentos, mas os **ranqueia por relevância** e otimiza a performance de inicialização.

## 🛠️ Decisões de Engenharia e Tecnologias

O valor deste projeto está na escolha e implementação de estruturas de dados que resolvem problemas reais de performance e usabilidade:

| Funcionalidade | Estrutura/Algoritmo | Benefício | Habilidade Demonstrada |
| :--- | :--- | :--- | :--- |
| **Busca e Indexação** | **Índice Invertido (Tabela Hash)** | Garante que a localização de documentos seja **quase instantânea** ($O(1)$ em média). | Estruturas de Dados |
| **Ranqueamento de Relevância** | **TF-IDF (Term Frequency)** | Transforma a busca de simples filtro para um **ranqueamento inteligente** de resultados. | Algoritmos de NLP/ML |
| **Sugestão de Palavras** | **Árvore Trie (Prefix Tree)** | Otimiza o **autocomplete**, garantindo buscas de prefixo extremamente rápidas. | Estruturas Avançadas |
| **Performance na Inicialização** | **Persistência (`pickle`)** | Evita a re-indexação demorada de documentos, carregando o índice complexo do disco. | Otimização de Sistemas |

## 🧪 Demonstração dos Resultados (TF-IDF)

---
## 🧪 Demonstração dos Resultados: Filtragem vs. Ranqueamento

A chave deste projeto é a diferença de comportamento entre a **busca booleana (filtro)** e a **busca ranqueada (TF-IDF)**.

### 1. Busca Booleana (Filtro)
*Função:* `buscar()`
*Comportamento:* Apenas retorna os documentos que contêm TODAS as palavras, ordenados alfabeticamente.

| Consulta | Resultado |
| :--- | :--- |
| `"raposa"` | `['doc1.txt', 'doc3.txt']` |
| `"cão preguiçoso"` | `['doc1.txt', 'doc2.txt']` |

### 2. Busca Ranqueada (TF-IDF)

*Função:* `calcular_tf_idf()`
*Comportamento:* Retorna os documentos com pontuações de relevância, ordenados do maior para o menor score.

| Consulta | Resultado (Documento, Pontuação) | Prova de Ranqueamento |
| :--- | :--- | :--- |
| `"raposa"` | `[('doc4.txt', 0.5753), ('doc1.txt', 0.2876), ('doc3.txt', 0.2876)]` | **Doc4** possui o dobro da pontuação de relevância, provando que o TF-IDF identificou a maior frequência do termo, aparecendo em primeiro. |
| `"cão preguiçoso"` | `[('doc1.txt', 0.9808), ('doc2.txt', 0.9808), ('doc3.txt', 0.2876)]` | Os termos têm maior peso e frequência no **Doc1 e Doc2**. O Doc3 contém o termo, mas sua baixa frequência o coloca em último lugar. |
| `"projeto"` | `[('doc3.txt', 0.6931), ('doc4.txt', 0.6931)]` | O score do Doc4 foi afetado pela nova indexação, mas os documentos compartilham relevância semelhante para esta palavra. |

---

### 3. Autocomplete (Árvore Trie)

Demonstração da eficiência da **Árvore Trie** para sugestão instantânea:

| Prefixo | Resultado |
| :--- | :--- |
| `"ra"` | `['raposa']` |
| `"pr"` | `['preguiçoso', 'projeto']` |

---
