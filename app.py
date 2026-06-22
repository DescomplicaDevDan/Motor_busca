from flask import Flask, abort, jsonify, render_template, request, send_from_directory, url_for

import indexador


app = Flask(__name__)
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


@app.route("/buscar", methods=["POST"])
def buscar_resultados():
    termo_buscado = request.form.get("consulta", "").strip()
    modo_busca = request.form.get("modo", "qualquer")
    if modo_busca not in indexador.MODOS_BUSCA:
        modo_busca = "qualquer"
    resultados = buscar_com_detalhes(termo_buscado, modo_busca)
    for resultado in resultados:
        resultado["partes_trecho"] = indexador.dividir_trecho_para_destaque(resultado["trecho"], termo_buscado)
    return render_template(
        "busca.html", resultados=resultados, termo_buscado=termo_buscado, modo_busca=modo_busca
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

    resultados = buscar_com_detalhes(consulta, modo_busca)
    return jsonify(
        {
            "consulta": consulta,
            "modo": modo_busca,
            "total": len(resultados),
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


@app.get("/sobre")
def pagina_sobre():
    return render_template("sobre.html")


if __name__ == "__main__":
    app.run(debug=True)
