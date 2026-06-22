import pickle
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
        self.arquivo_indice = self.pasta / "indice.pkl"

    def test_indice_persistido_reconstroi_a_trie(self):
        indexador.construir_indice_a_partir_de_arquivos(self.pasta)
        self.assertTrue(indexador.salvar_indice(self.arquivo_indice))

        # O conteúdo gravado contém apenas dados simples, nunca uma NoTrie.
        with self.arquivo_indice.open("rb") as arquivo:
            dados = pickle.load(arquivo)
        self.assertEqual(set(dados), {"versao", "indice_invertido", "documentos_ids"})
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


if __name__ == "__main__":
    unittest.main()
