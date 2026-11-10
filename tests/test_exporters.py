from fractions import Fraction
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from spda_nbr5419.calculator import dimensionar_spda
from spda_nbr5419.exporters import (
    TIMESTAMP_DETERMINISTICO,
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)
from spda_nbr5419.models import Estrutura


class TestExporters(unittest.TestCase):
    def setUp(self) -> None:
        self.est = Estrutura(
            nome="Edifício Teste",
            comprimento_m=Fraction(30, 1),
            largura_m=Fraction(20, 1),
            altura_m=Fraction(40, 1),
            densidade_descargas_ng=Fraction(8, 1),
            localizacao_ambiental="isolada_plano",
            risco_incendio="ordinario",
            combate_incendio="manual",
            pessoas_em_risco=60,
            horas_ocupacao_ano=8760,
            tipo_material="cobre",
        )
        self.resultado = dimensionar_spda(self.est)

    def test_sanitizacao_csv(self) -> None:
        self.assertEqual(sanitizar_campo_csv("=1+2"), "'=1+2")
        self.assertEqual(sanitizar_campo_csv("+123"), "'+123")
        self.assertEqual(sanitizar_campo_csv("-123"), "'-123")
        self.assertEqual(sanitizar_campo_csv("@cmd"), "'@cmd")
        self.assertEqual(sanitizar_campo_csv("\ttab"), "'\ttab")
        self.assertEqual(sanitizar_campo_csv("Texto Seguro"), "Texto Seguro")

    def test_relatorio_texto(self) -> None:
        txt = gerar_relatorio_texto(self.resultado)
        self.assertIn("LAUDO TÉCNICO DE DIMENSIONAMENTO DE SPDA", txt)
        self.assertIn("ABNT NBR 5419:2015", txt)
        self.assertIn("SUBSISTEMA DE CAPTAÇÃO", txt)
        self.assertIn("SUBSISTEMA DE DESCIDAS", txt)
        self.assertIn("SUBSISTEMA DE ATERRAMENTO", txt)

    def test_gerar_csv_sanitizado(self) -> None:
        csv_str = gerar_csv_sanitizado(self.resultado)
        self.assertIn("Item,Parametro,Valor,Unidade,Norma_Referencia", csv_str)
        self.assertIn("Edificacao,Nome da Obra", csv_str)
        self.assertIn("Risco,Risco R1 Sem SPDA", csv_str)

    def test_gerar_pacote_zip_deterministico(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "pacote_spda.zip"
            gerar_pacote_zip_deterministico(self.resultado, zip_path)
            self.assertTrue(zip_path.exists())

            with zipfile.ZipFile(zip_path, "r") as zf:
                nomes = zf.namelist()
                self.assertIn("relatorio_spda.txt", nomes)
                self.assertIn("dados_dimensionamento.csv", nomes)
                self.assertIn("resultado_spda.json", nomes)

                for info in zf.infolist():
                    self.assertEqual(info.date_time, TIMESTAMP_DETERMINISTICO)

            # Teste de proteção contra sobrescrita com FileExistsError
            with self.assertRaises(FileExistsError):
                gerar_pacote_zip_deterministico(self.resultado, zip_path)


if __name__ == "__main__":
    unittest.main()
