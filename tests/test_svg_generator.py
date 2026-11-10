from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from spda_nbr5419.calculator import dimensionar_spda
from spda_nbr5419.models import Estrutura
from spda_nbr5419.svg_generator import gerar_painel_svg


class TestSvgGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.est = Estrutura(
            nome="Condomínio Solar das Palmeiras",
            comprimento_m=Fraction(35, 1),
            largura_m=Fraction(22, 1),
            altura_m=Fraction(36, 1),
            densidade_descargas_ng=Fraction(7, 1),
            localizacao_ambiental="isolada_plano",
            risco_incendio="ordinario",
            combate_incendio="manual",
            pessoas_em_risco=70,
            horas_ocupacao_ano=8760,
            tipo_material="cobre",
        )
        self.resultado = dimensionar_spda(self.est, "PROJ-SPDA-SOLAR")

    def test_gerar_painel_svg_estrutura_xml(self) -> None:
        svg = gerar_painel_svg(self.resultado)
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.strip().endswith("</svg>"))
        self.assertIn("1440", svg)
        self.assertIn("900", svg)
        self.assertIn("ABNT NBR 5419:2015", svg)
        self.assertIn("LOFRANO TECNOLOGIA", svg)
        self.assertIn("Condomínio Solar das Palmeiras", svg)
        self.assertIn("SPDA CONFORME", svg)
        self.assertIn("ESFERA ROLANTE", svg)


if __name__ == "__main__":
    unittest.main()
