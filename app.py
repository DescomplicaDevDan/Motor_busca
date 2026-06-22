from flask import Flask, render_template, request

import indexador


app = Flask(__name__)
indexador.inicializar_indices()


@app.route("/buscar", methods=["POST"])
def buscar_resultados():
    termo_buscado = request.form.get("consulta", "").strip()
    resultados = indexador.calcular_tf_idf(termo_buscado)
    return render_template("busca.html", resultados=resultados, termo_buscado=termo_buscado)


@app.route("/")
def pagina_inicial():
    return render_template("busca.html")


if __name__ == "__main__":
    app.run(debug=True)
