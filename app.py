from flask import Flask, abort, jsonify, render_template, request, send_from_directory

import indexador


app = Flask(__name__)
indexador.inicializar_indices()


@app.route("/buscar", methods=["POST"])
def buscar_resultados():
    termo_buscado = request.form.get("consulta", "").strip()
    modo_busca = request.form.get("modo", "qualquer")
    if modo_busca not in indexador.MODOS_BUSCA:
        modo_busca = "qualquer"
    resultados = []
    for doc_id, pontuacao in indexador.calcular_tf_idf(termo_buscado, modo_busca):
        trecho = indexador.obter_trecho(doc_id, termo_buscado)
        resultados.append(
            {
                "documento": doc_id,
                "pontuacao": pontuacao,
                "partes_trecho": indexador.dividir_trecho_para_destaque(trecho, termo_buscado),
            }
        )
    return render_template(
        "busca.html", resultados=resultados, termo_buscado=termo_buscado, modo_busca=modo_busca
    )


@app.get("/api/autocomplete")
def autocomplete():
    """Retorna sugestões para a última palavra que está sendo digitada."""
    consulta = request.args.get("q", "")
    ultima_palavra = consulta.rsplit(maxsplit=1)[-1] if consulta and not consulta[-1].isspace() else ""
    termos = indexador.pre_processar_texto(ultima_palavra)
    prefixo = termos[0] if termos else ""

    sugestoes = indexador.buscar_prefixo(prefixo)[:8] if prefixo else []
    return jsonify({"sugestoes": sugestoes})


@app.get("/documentos/<nome_arquivo>")
def abrir_documento(nome_arquivo):
    """Abre somente documentos que fazem parte do índice atual."""
    if nome_arquivo not in indexador.DOCUMENTOS_IDS:
        abort(404)
    return send_from_directory(indexador.PASTA_DOCUMENTOS_PADRAO, nome_arquivo, mimetype="text/plain")


@app.route("/")
def pagina_inicial():
    return render_template("busca.html", modo_busca="qualquer")


if __name__ == "__main__":
    app.run(debug=True)
