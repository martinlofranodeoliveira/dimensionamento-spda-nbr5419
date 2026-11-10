from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from spda_nbr5419.constants import (
    CONDUTORES_NORMATIVOS,
    FATORES_COMBATE_INCENDIO_RP,
    FATORES_LOCALIZACAO_CD,
    FATORES_RISCO_INCENDIO_RF,
    NIVEIS_PROTECAO,
    PI_RACIONAL,
    RISCO_TOLERAVEL_R1,
    TIPOS_ESTRUTURA_PADRAO,
)


class TestConstantes(unittest.TestCase):
    def test_pi_racional(self) -> None:
        self.assertEqual(PI_RACIONAL, Fraction(355, 113))

    def test_risco_toleravel_r1(self) -> None:
        self.assertEqual(RISCO_TOLERAVEL_R1, Fraction(1, 100_000))

    def test_niveis_protecao_completos(self) -> None:
        for nivel in ("NP_I", "NP_II", "NP_III", "NP_IV"):
            self.assertIn(nivel, NIVEIS_PROTECAO)
            dados = NIVEIS_PROTECAO[nivel]
            self.assertGreater(dados["raio_esfera_rolante_m"], 0)
            self.assertGreater(dados["malha_comprimento_m"], 0)
            self.assertGreater(dados["espacamento_descidas_m"], 0)
            self.assertIsInstance(dados["eficiencia_minima"], Fraction)
            self.assertIsInstance(dados["probabilidade_dano_pb"], Fraction)

    def test_fatores_localizacao_cd(self) -> None:
        for chave in ("isolada_colina", "isolada_plano", "cercada_mesma_altura", "cercada_mais_altas"):
            self.assertIn(chave, FATORES_LOCALIZACAO_CD)
            self.assertGreater(FATORES_LOCALIZACAO_CD[chave]["fator"], 0)

    def test_fatores_risco_incendio_rf(self) -> None:
        for chave in ("explosivo", "ordinario", "baixo", "nenhum"):
            self.assertIn(chave, FATORES_RISCO_INCENDIO_RF)
            self.assertGreaterEqual(FATORES_RISCO_INCENDIO_RF[chave]["fator"], 0)

    def test_fatores_combate_incendio_rp(self) -> None:
        for chave in ("nenhuma", "manual", "alarme_brigada", "sprinklers"):
            self.assertIn(chave, FATORES_COMBATE_INCENDIO_RP)
            self.assertGreater(FATORES_COMBATE_INCENDIO_RP[chave]["fator"], 0)

    def test_condutores_normativos(self) -> None:
        for chave, c in CONDUTORES_NORMATIVOS.items():
            self.assertIn("material", c)
            self.assertIn("uso", c)
            self.assertGreater(c["secao_minima_mm2"], 0)

    def test_tipos_estrutura_padrao(self) -> None:
        self.assertIn("predio_residencial", TIPOS_ESTRUTURA_PADRAO)
        self.assertIn("escola_hospital", TIPOS_ESTRUTURA_PADRAO)
        self.assertIn("galpao_industrial", TIPOS_ESTRUTURA_PADRAO)


if __name__ == "__main__":
    unittest.main()
