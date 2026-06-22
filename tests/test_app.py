import unittest

try:
    import flask  # noqa: F401 - confirma que a dependência está disponível
except ModuleNotFoundError:
    FLASK_DISPONIVEL = False
else:
    FLASK_DISPONIVEL = True
    from app import app


@unittest.skipUnless(FLASK_DISPONIVEL, "Flask não está instalado neste ambiente")
class TestRotasFlask(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_pagina_inicial_responde_com_sucesso(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Motor de Busca", resposta.data)

    def test_busca_renderiza_resultados(self):
        resposta = self.client.post("/buscar", data={"consulta": "raposa", "modo": "qualquer"})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"doc1.txt", resposta.data)

    def test_autocomplete_retorna_json(self):
        resposta = self.client.get("/api/autocomplete?q=ra")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["sugestoes"][0], "raposa")

    def test_documento_indexado_pode_ser_aberto(self):
        resposta = self.client.get("/documentos/doc1.txt")
        try:
            self.assertEqual(resposta.status_code, 200)
            self.assertIn(b"raposa", resposta.data.lower())
        finally:
            resposta.close()

    def test_documento_fora_do_indice_retorna_404(self):
        resposta = self.client.get("/documentos/segredo.txt")
        self.assertEqual(resposta.status_code, 404)
