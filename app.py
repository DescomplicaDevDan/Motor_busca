from flask import Flask, render_template, request

import indexador


app = Flask(__name__)
indexador.inicializar_indices()


@app.route("/buscar", methods=["POST"])
def buscar_resultados():
    termo_buscado = request.form.get("consulta", "").strip()
    resultados = []
    for doc_id, pontuacao in indexador.calcular_tf_idf(termo_buscado):
        trecho = indexador.obter_trecho(doc_id, termo_buscado)
        resultados.append(
            {
                "documento": doc_id,
                "pontuacao": pontuacao,
                "partes_trecho": indexador.dividir_trecho_para_destaque(trecho, termo_buscado),
            }
        )
    return render_template("busca.html", resultados=resultados, termo_buscado=termo_buscado)


@app.route("/")
def pagina_inicial():
    return render_template("busca.html")


if __name__ == "__main__":
    app.run(debug=True)
