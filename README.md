# Motor de busca com TF-IDF e Trie

Projeto didático em Python e Flask que indexa os arquivos em `documentos/`,
permite buscas e ordena os resultados por relevância.

## Como o motor funciona

- **Índice invertido:** para cada palavra, guarda os documentos em que ela
  aparece e sua frequência.
- **Busca booleana (`buscar`)**: devolve somente documentos que contêm todas
  as palavras da consulta.
- **TF-IDF (`calcular_tf_idf`)**: soma o peso de cada termo da consulta e
  ordena documentos com pontuação maior primeiro. Nesta versão didática, uma
  consulta com mais de um termo considera documentos que contenham qualquer
  termo para o ranqueamento.
- **Trie (`buscar_prefixo`)**: oferece sugestões a partir de um prefixo.

## Persistência do índice

O arquivo `motor_indice.pkl` armazena apenas o índice invertido e a lista de
documentos, que são dicionários, listas e números. A Trie não é salva: ela é
reconstruída a partir das palavras do índice quando o programa inicia.

Isso é importante porque serializar uma instância da classe `NoTrie` faz o
`pickle` depender do nome do módulo que criou o arquivo. Se o programa for
executado de outra forma — por exemplo, importado pelo Vercel — o índice pode
deixar de abrir. Dados simples evitam essa fragilidade.

Se o índice estiver ausente, antigo ou inválido, o projeto o recria
automaticamente com os arquivos em `documentos/`.

## Executar localmente

Use Python 3.10 ou superior.

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Instale a dependência e execute o servidor:

```bash
python -m pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000` no navegador. Na primeira execução, o índice é
criado automaticamente.

## Verificar o motor sem abrir o navegador

```bash
python indexador.py
python -m unittest discover -s tests -v
```

O primeiro comando mostra exemplos de busca e autocomplete. O segundo verifica
que o índice é persistido sem objetos da Trie e pode ser carregado novamente.

> Não carregue arquivos `.pkl` recebidos de fontes não confiáveis: `pickle`
> não é um formato seguro para dados externos.
