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

    def test_pagina_sobre_exibe_arquitetura_do_projeto(self):
        resposta = self.client.get("/sobre")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"Decis", resposta.data)
        self.assertIn(b"TF-IDF", resposta.data)

    def test_busca_renderiza_resultados(self):
        resposta = self.client.post("/buscar", data={"consulta": "raposa", "modo": "qualquer"})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn(b"doc1.txt", resposta.data)

    def test_autocomplete_retorna_json(self):
        resposta = self.client.get("/api/autocomplete?q=ra")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("raposa", resposta.json["sugestoes"])

    def test_api_buscar_retorna_resultados_ranqueados(self):
        resposta = self.client.get("/api/buscar?q=raposa&modo=qualquer")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["consulta"], "raposa")
        self.assertGreater(resposta.json["total"], 0)
        self.assertIn("relevancia", resposta.json["resultados"][0])
        self.assertIn("url", resposta.json["resultados"][0])

    def test_api_buscar_rejeita_consulta_ou_modo_invalidos(self):
        sem_consulta = self.client.get("/api/buscar")
        modo_invalido = self.client.get("/api/buscar?q=raposa&modo=invalido")
        self.assertEqual(sem_consulta.status_code, 400)
        self.assertEqual(modo_invalido.status_code, 400)
        self.assertIn("modos_aceitos", modo_invalido.json)

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
