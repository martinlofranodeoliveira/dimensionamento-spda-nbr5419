from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from spda_nbr5419.models import (
    AreaExposicaoEquivalente,
    DimensionamentoAterramento,
    DimensionamentoCaptacao,
    DimensionamentoDescidas,
    Estrutura,
    GerenciamentoRisco,
)


class TestModelos(unittest.TestCase):
    def test_estrutura_valida(self) -> None:
        est = Estrutura(
            nome="Teste",
            comprimento_m=Fraction(20, 1),
            largura_m=Fraction(15, 1),
            altura_m=Fraction(30, 1),
            densidade_descargas_ng=Fraction(5, 1),
            localizacao_ambiental="isolada_plano",
            risco_incendio="ordinario",
            combate_incendio="manual",
            pessoas_em_risco=30,
            horas_ocupacao_ano=8760,
            tipo_material="cobre",
        )
        self.assertEqual(est.nome, "Teste")
        self.assertEqual(est.comprimento_m, Fraction(20, 1))

    def test_estrutura_invalida_dimensao_negativa(self) -> None:
        with self.assertRaises(ValueError):
            Estrutura(
                nome="Invalido",
                comprimento_m=Fraction(-10, 1),
                largura_m=Fraction(15, 1),
                altura_m=Fraction(30, 1),
                densidade_descargas_ng=Fraction(5, 1),
                localizacao_ambiental="isolada_plano",
                risco_incendio="ordinario",
                combate_incendio="manual",
                pessoas_em_risco=30,
                horas_ocupacao_ano=8760,
                tipo_material="cobre",
            )

    def test_estrutura_invalida_horas_ocupacao(self) -> None:
        with self.assertRaises(ValueError):
            Estrutura(
                nome="Invalido",
                comprimento_m=Fraction(20, 1),
                largura_m=Fraction(15, 1),
                altura_m=Fraction(30, 1),
                densidade_descargas_ng=Fraction(5, 1),
                localizacao_ambiental="isolada_plano",
                risco_incendio="ordinario",
                combate_incendio="manual",
                pessoas_em_risco=30,
                horas_ocupacao_ano=9000,
                tipo_material="cobre",
            )

    def test_imutabilidade_estrutura(self) -> None:
        est = Estrutura(
            nome="Teste",
            comprimento_m=Fraction(20, 1),
            largura_m=Fraction(15, 1),
            altura_m=Fraction(30, 1),
            densidade_descargas_ng=Fraction(5, 1),
            localizacao_ambiental="isolada_plano",
            risco_incendio="ordinario",
            combate_incendio="manual",
            pessoas_em_risco=30,
            horas_ocupacao_ano=8760,
            tipo_material="cobre",
        )
        with self.assertRaises(AttributeError):
            est.nome = "Outro"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
