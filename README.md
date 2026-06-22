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

O arquivo `motor_indice.json` armazena o índice invertido, a lista e os
tamanhos dos documentos como JSON legível. A Trie não é salva: ela é
reconstruída a partir das palavras do índice quando o programa inicia.

JSON evita a dependência de classes Python e não executa código ao ser lido,
ao contrário de `pickle`. Isso torna o formato mais seguro para persistência e
mais fácil de inspecionar no repositório.

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

## API JSON

Além da interface web, o projeto expõe a busca ranqueada em JSON:

```text
GET /api/buscar?q=raposa&modo=qualquer
```

O parâmetro `modo` aceita `qualquer` (padrão) ou `todos`. A resposta informa a
consulta, o total e, para cada resultado, o documento, a relevância, o trecho
e a URL para abrir o arquivo.

## Verificar o motor sem abrir o navegador

```bash
python indexador.py
python -m unittest discover -s tests -v
```

O primeiro comando mostra exemplos de busca e autocomplete. O segundo verifica
que o índice é persistido sem objetos da Trie e pode ser carregado novamente.

> Embora JSON não execute código ao ser lido, o projeto ainda valida a versão
> e a estrutura do índice antes de usá-lo.
