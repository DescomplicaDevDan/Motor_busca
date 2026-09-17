# Validação — 17/09/2026

## Testes automatizados

Com Python 3.12 e `requirements.txt` instalado, `python -m unittest discover -s tests -v` executou **19 testes com sucesso, sem testes ignorados**.

- 10 testes do indexador: persistência, reconstrução da Trie, normalização, modos de busca, relevância, trechos, índice inválido e reindexação.
- 9 testes Flask: páginas, busca, reindexação, autocomplete, API, parâmetros inválidos e acesso a documentos.

## Verificação de tela

Página inicial aberta localmente em Chromium, em 1440 × 900 e 390 × 844. Sem transbordamento horizontal nas duas larguras. Capturas inspecionadas:

- [Desktop](evidencias/desktop-busca.png)
- [Celular simulado](evidencias/mobile-busca.png)

Na largura de celular, a navegação quebra linhas e o texto de exemplo da pesquisa aparece parcialmente. Isso não foi tratado como garantia de usabilidade; merece refinamento posterior.

## Limites

A verificação visual cobre a página inicial nessas duas larguras. Não substitui testes em aparelhos físicos, outros navegadores, acessibilidade, carga ou todos os fluxos interativos. Os testes Flask usam cliente de teste, não um navegador.
