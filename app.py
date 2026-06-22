from threading import Lock
from time import perf_counter

from flask import Flask, abort, jsonify, redirect, render_template, request, send_from_directory, url_for

import indexador


app = Flask(__name__)
BLOQUEIO_INDICE = Lock()
with BLOQUEIO_INDICE:
    indexador.inicializar_indices()


def buscar_com_detalhes(consulta, modo_busca):
    """Executa o ranqueamento e acrescenta o trecho de cada resultado."""
    resultados = []
    for doc_id, pontuacao in indexador.calcular_tf_idf(consulta, modo_busca):
        resultados.append(
            {
                "documento": doc_id,
                "pontuacao": pontuacao,
                "trecho": indexador.obter_trecho(doc_id, consulta),
            }
        )
    return resultados


def executar_busca(consulta, modo_busca):
    """Executa uma busca consistente e mede o tempo total em milissegundos."""
    inicio = perf_counter()
    with BLOQUEIO_INDICE:
        resultados = buscar_com_detalhes(consulta, modo_busca)
        estatisticas = indexador.obter_estatisticas()
    tempo_busca_ms = round((perf_counter() - inicio) * 1000, 2)
    return resultados, estatisticas, tempo_busca_ms


def obter_estatisticas():
    with BLOQUEIO_INDICE:
        return indexador.obter_estatisticas()


@app.route("/buscar", methods=["POST"])
def buscar_resultados():
    termo_buscado = request.form.get("consulta", "").strip()
    modo_busca = request.form.get("modo", "qualquer")
    if modo_busca not in indexador.MODOS_BUSCA:
        modo_busca = "qualquer"
    resultados, estatisticas, tempo_busca_ms = executar_busca(termo_buscado, modo_busca)
    for resultado in resultados:
        resultado["partes_trecho"] = indexador.dividir_trecho_para_destaque(resultado["trecho"], termo_buscado)
    return render_template(
        "busca.html",
        resultados=resultados,
        termo_buscado=termo_buscado,
        modo_busca=modo_busca,
        estatisticas=estatisticas,
        tempo_busca_ms=tempo_busca_ms,
    )


@app.get("/api/buscar")
def api_buscar():
    """Expõe a busca ranqueada em JSON para outros clientes consumirem."""
    consulta = request.args.get("q", "").strip()
    modo_busca = request.args.get("modo", "qualquer")

    if not consulta:
        return jsonify({"erro": "Informe o parâmetro de consulta 'q'."}), 400
    if modo_busca not in indexador.MODOS_BUSCA:
        return jsonify({"erro": "Modo inválido.", "modos_aceitos": sorted(indexador.MODOS_BUSCA)}), 400

    resultados, estatisticas, tempo_busca_ms = executar_busca(consulta, modo_busca)
    return jsonify(
        {
            "consulta": consulta,
            "modo": modo_busca,
            "total": len(resultados),
            "tempo_busca_ms": tempo_busca_ms,
            "estatisticas": estatisticas,
            "resultados": [
                {
                    "documento": resultado["documento"],
                    "relevancia": round(resultado["pontuacao"], 6),
                    "trecho": resultado["trecho"],
                    "url": url_for("abrir_documento", nome_arquivo=resultado["documento"]),
                }
                for resultado in resultados
            ],
        }
    )


@app.get("/api/autocomplete")
def autocomplete():
    """Retorna sugestões para a última palavra que está sendo digitada."""
    consulta = request.args.get("q", "")
    ultima_palavra = consulta.rsplit(maxsplit=1)[-1] if consulta and not consulta[-1].isspace() else ""
    termos = indexador.pre_processar_texto(ultima_palavra)
    prefixo = termos[0] if termos else ""

    with BLOQUEIO_INDICE:
        sugestoes = indexador.buscar_prefixo(prefixo)[:8] if prefixo else []
    return jsonify({"sugestoes": sugestoes})


@app.get("/documentos/<nome_arquivo>")
def abrir_documento(nome_arquivo):
    """Abre somente documentos que fazem parte do índice atual."""
    with BLOQUEIO_INDICE:
        if nome_arquivo not in indexador.DOCUMENTOS_IDS:
            abort(404)
    return send_from_directory(indexador.PASTA_DOCUMENTOS_PADRAO, nome_arquivo, mimetype="text/plain")


@app.post("/reindexar")
def reindexar_documentos():
    """Reconstrói o índice a partir da pasta de documentos e retorna à busca."""
    with BLOQUEIO_INDICE:
        indexador.reindexar()
    return redirect(url_for("pagina_inicial", reindexado="1"))


@app.route("/")
def pagina_inicial():
    return render_template(
        "busca.html",
        modo_busca="qualquer",
        estatisticas=obter_estatisticas(),
        reindexado=request.args.get("reindexado") == "1",
    )


@app.get("/sobre")
def pagina_sobre():
    return render_template("sobre.html")


if __name__ == "__main__":
    app.run(debug=True)
