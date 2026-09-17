# Motor de busca com TF-IDF e Trie

Projeto didático em Python e Flask que indexa os arquivos em `documentos/`,
permite buscas e ordena os resultados por relevância.

[Ver demonstração](https://motor-busca.vercel.app/)

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
git clone https://github.com/DescomplicaDevDan/Motor_busca.git
cd Motor_busca
```

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

O primeiro comando mostra exemplos de busca e autocomplete. O segundo executa 19 testes de indexação, persistência, busca, trechos, rotas e validação da API. Instale as dependências antes: sem Flask, os 9 testes de rotas são ignorados.

Validação local em 17/09/2026: **19 testes passaram, sem testes ignorados**, com Python 3.12 e as dependências de `requirements.txt`.

> Embora JSON não execute código ao ser lido, o projeto ainda valida a versão
> e a estrutura do índice antes de usá-lo.

Consulte também o [registro de validação e capturas de tela](docs/VALIDACAO.md).

## Limitações e escopo

- Projeto didático sobre os arquivos locais em `documentos/`; não rastreia a web.
- O índice é mantido em memória e persistido em JSON; não há avaliação de escala ou comparação com motores de produção.
- O endpoint de reindexação não tem autenticação; o projeto não deve ser tratado como serviço de produção multiusuário sem controles adicionais.
- Os testes automatizados verificam comportamentos específicos, não cobertura completa ou compatibilidade com todos os navegadores.

## Autor

[Danilo Texeira](https://github.com/DescomplicaDevDan)
