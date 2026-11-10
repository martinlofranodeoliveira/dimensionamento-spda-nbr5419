from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import spda_nbr5419


class TestPackaging(unittest.TestCase):
    def test_versao_pacote(self) -> None:
        self.assertEqual(spda_nbr5419.__version__, "1.0.0")

    def test_simbolos_exportados(self) -> None:
        simbolos = spda_nbr5419.__all__
        self.assertIn("Estrutura", simbolos)
        self.assertIn("dimensionar_spda", simbolos)
        self.assertIn("calcular_area_exposicao_equivalente", simbolos)
        self.assertIn("avaliar_gerenciamento_risco", simbolos)
        self.assertIn("dimensionar_captacao", simbolos)
        self.assertIn("dimensionar_descidas", simbolos)
        self.assertIn("dimensionar_aterramento", simbolos)
        self.assertIn("gerar_painel_svg", simbolos)
        self.assertIn("gerar_relatorio_texto", simbolos)
        self.assertIn("gerar_csv_sanitizado", simbolos)
        self.assertIn("gerar_pacote_zip_deterministico", simbolos)
        self.assertIn("carregar_entrada_json", simbolos)
        self.assertIn("exportar_resultado_json", simbolos)

        for s in simbolos:
            self.assertTrue(hasattr(spda_nbr5419, s), f"Símbolo {s} não encontrado no módulo.")


if __name__ == "__main__":
    unittest.main()
