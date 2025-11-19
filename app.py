from flask import Flask, render_template, request
import indexador

class NoTrie:
    def __init__(self):
        self.filhos = {} 
        self.fim_de_palavra = False

app = Flask(__name__)

try:
    
    indice_carregado = indexador.carregar_indice() 

    if not indice_carregado:
        print("AVISO: O arquivo motor_indice.pkl não foi encontrado. Execute o indexador.py para construir o índice primeiro.")

    global INDICE_INVERTIDO, DOCUMENTOS_IDS
    INDICE_INVERTIDO = indexador.INDICE_INVERTIDO
    DOCUMENTOS_IDS = indexador.DOCUMENTOS_IDS

    print("--- Índice Invertido Carregado com Sucesso! ---")

except Exception as e:
    print(f"ERRO ao carregar o índice: {e}")


@app.route('/buscar', methods=['POST'])
def buscar_resultados():
    
    termo_buscado = request.form['consulta']
    
    resultados = indexador.calcular_tf_idf(termo_buscado)
    
    return render_template(
        'busca.html', 
        resultados=resultados, 
        termo_buscado=termo_buscado
    )

@app.route('/')
def pagina_inicial():
   
    return render_template('busca.html')

if __name__ == '__main__':
    app.run(debug=True)
