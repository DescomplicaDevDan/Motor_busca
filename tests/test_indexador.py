import json
import tempfile
import unittest
from pathlib import Path

import indexador


class TestIndexador(unittest.TestCase):
    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta_temporaria.cleanup)
        self.pasta_documentos_original = indexador.PASTA_DOCUMENTOS_PADRAO
        self.addCleanup(setattr, indexador, "PASTA_DOCUMENTOS_PADRAO", self.pasta_documentos_original)
        self.pasta = Path(self.pasta_temporaria.name)
        (self.pasta / "primeiro.txt").write_text("Raposa ágil", encoding="utf-8")
        (self.pasta / "segundo.txt").write_text("Raposa preguiçosa", encoding="utf-8")
        self.arquivo_indice = self.pasta / "indice.json"

    def test_indice_persistido_reconstroi_a_trie(self):
        indexador.construir_indice_a_partir_de_arquivos(self.pasta)
        self.assertTrue(indexador.salvar_indice(self.arquivo_indice))

        # O conteúdo gravado é JSON legível e contém somente dados simples.
        with self.arquivo_indice.open(encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        self.assertEqual(set(dados), {"versao", "indice_invertido", "documentos_ids", "tamanhos_documentos"})
        self.assertEqual(dados["versao"], indexador.VERSAO_INDICE)

        indexador.INDICE_INVERTIDO.clear()
        indexador.DOCUMENTOS_IDS.clear()
        self.assertTrue(indexador.carregar_indice(self.arquivo_indice))
        self.assertEqual(indexador.buscar("raposa"), ["primeiro.txt", "segundo.txt"])
        self.assertEqual(indexador.buscar_prefixo("ra"), ["raposa"])

    def test_obter_trecho_mostra_o_contexto_do_termo(self):
        indexador.PASTA_DOCUMENTOS_PADRAO = self.pasta
        trecho = indexador.obter_trecho("primeiro.txt", "raposa")
        self.assertIn("Raposa ágil", trecho)

    def test_dividir_trecho_destaca_termo_sem_alterar_o_texto(self):
        partes = indexador.dividir_trecho_para_destaque("A Raposa ágil.", "raposa")
        self.assertEqual("".join(parte["texto"] for parte in partes), "A Raposa ágil.")
        self.assertEqual([parte["texto"] for parte in partes if parte["destacado"]], ["Raposa"])

    def test_stopwords_nao_entram_na_consulta(self):
        self.assertEqual(indexador.pre_processar_texto("A raposa e o cão para o rio"), ["raposa", "cão", "rio"])

    def test_modo_todos_exige_cada_termo(self):
        indexador.construir_indice_a_partir_de_arquivos(self.pasta)
        self.assertEqual(
            [doc_id for doc_id, _ in indexador.calcular_tf_idf("raposa ágil", modo="todos")], ["primeiro.txt"]
        )
        self.assertEqual(
            {doc_id for doc_id, _ in indexador.calcular_tf_idf("raposa ágil", modo="qualquer")},
            {"primeiro.txt", "segundo.txt"},
        )

    def test_cosseno_prefere_documento_curto_e_preciso(self):
        (self.pasta / "curto.txt").write_text("raposa", encoding="utf-8")
        (self.pasta / "longo.txt").write_text("raposa " + "contexto " * 100, encoding="utf-8")
        indexador.construir_indice_a_partir_de_arquivos(self.pasta)

        resultados = dict(indexador.calcular_tf_idf("raposa"))
        self.assertGreater(resultados["curto.txt"], resultados["longo.txt"])

    def test_busca_booleana_aceita_qualquer_ou_todos_os_termos(self):
        indexador.construir_indice_a_partir_de_arquivos(self.pasta)
        self.assertEqual(indexador.buscar("raposa ágil", modo="todos"), ["primeiro.txt"])
        self.assertEqual(indexador.buscar("raposa ágil", modo="qualquer"), ["primeiro.txt", "segundo.txt"])

    def test_consulta_sem_termos_uteis_nao_retorna_resultados(self):
        indexador.construir_indice_a_partir_de_arquivos(self.pasta)
        self.assertEqual(indexador.calcular_tf_idf("a e o para"), [])
        self.assertEqual(indexador.calcular_tf_idf("raposa", modo="invalido"), [])

    def test_indice_corrompido_e_recusado(self):
        indice_corrompido = self.pasta / "corrompido.json"
        indice_corrompido.write_text("este arquivo não é um JSON", encoding="utf-8")
        self.assertFalse(indexador.carregar_indice(indice_corrompido))


if __name__ == "__main__":
    unittest.main()
