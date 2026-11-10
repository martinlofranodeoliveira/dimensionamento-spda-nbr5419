from fractions import Fraction
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from spda_nbr5419.calculator import (
    avaliar_gerenciamento_risco,
    calcular_area_exposicao_equivalente,
    dimensionar_aterramento,
    dimensionar_captacao,
    dimensionar_descidas,
    dimensionar_spda,
)
from spda_nbr5419.constants import PI_RACIONAL, RISCO_TOLERAVEL_R1
from spda_nbr5419.models import Estrutura


class TestCalculadora(unittest.TestCase):
    def setUp(self) -> None:
        self.estrutura_predio = Estrutura(
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

    def test_calcular_area_exposicao_equivalente(self) -> None:
        area = calcular_area_exposicao_equivalente(self.estrutura_predio)
        # L=30, W=20, H=40 -> 3H = 120
        # Cobertura = 30 * 20 = 600
        # Perimetro = 2 * (30 + 20) = 100
        # Lateral = 2 * 120 * 50 = 12000
        # Cantos = PI * 120^2 = 14400 * 355 / 113
        self.assertEqual(area.area_cobertura_m2, Fraction(600, 1))
        self.assertEqual(area.perimetro_m, Fraction(100, 1))
        self.assertEqual(area.largura_faixa_protecao_m, Fraction(120, 1))
        self.assertEqual(area.area_lateral_m2, Fraction(12000, 1))
        self.assertEqual(area.area_cantos_m2, PI_RACIONAL * 14400)
        esperado_total = Fraction(12600, 1) + (PI_RACIONAL * 14400)
        self.assertEqual(area.area_total_ad_m2, esperado_total)

    def test_avaliar_gerenciamento_risco_necessario(self) -> None:
        area = calcular_area_exposicao_equivalente(self.estrutura_predio)
        risco = avaliar_gerenciamento_risco(self.estrutura_predio, area)
        self.assertTrue(risco.necessidade_spda)
        self.assertGreater(risco.risco_r1_sem_spda, RISCO_TOLERAVEL_R1)
        self.assertIn(risco.nivel_protecao_adotado, ("NP_I", "NP_II", "NP_III", "NP_IV"))
        self.assertGreater(risco.reducao_risco_percentual, 0)

    def test_avaliar_gerenciamento_risco_sem_pessoas(self) -> None:
        est_sem_pessoas = Estrutura(
            nome="Depósito Vazio",
            comprimento_m=Fraction(10, 1),
            largura_m=Fraction(10, 1),
            altura_m=Fraction(5, 1),
            densidade_descargas_ng=Fraction(1, 1),
            localizacao_ambiental="cercada_mais_altas",
            risco_incendio="baixo",
            combate_incendio="sprinklers",
            pessoas_em_risco=0,
            horas_ocupacao_ano=0,
            tipo_material="aco_galvanizado",
        )
        area = calcular_area_exposicao_equivalente(est_sem_pessoas)
        risco = avaliar_gerenciamento_risco(est_sem_pessoas, area)
        self.assertEqual(risco.risco_r1_sem_spda, Fraction(0, 1))
        self.assertFalse(risco.necessidade_spda)

    def test_dimensionar_captacao_np3(self) -> None:
        captacao = dimensionar_captacao(self.estrutura_predio, "NP_III")
        # NP III: malha 15m x 15m, esfera R=45m
        # L=30 -> 30/15 = 2 modulos
        # W=20 -> ceil(20/15) = 2 modulos
        self.assertEqual(captacao.nivel_protecao, "NP_III")
        self.assertEqual(captacao.raio_esfera_m, 45)
        self.assertEqual(captacao.malha_maxima_comprimento_m, 15)
        self.assertEqual(captacao.malha_maxima_largura_m, 15)
        self.assertEqual(captacao.quantidade_modulos_comprimento, 2)
        self.assertEqual(captacao.quantidade_modulos_largura, 2)
        self.assertEqual(captacao.total_modulos_malha, 4)
        # Linhas long: (2 + 1) * 30 = 90
        # Linhas trans: (2 + 1) * 20 = 60
        # Total = 150
        self.assertEqual(captacao.comprimento_cabos_captor_m, Fraction(150, 1))
        self.assertEqual(captacao.secao_minima_captor_mm2, 35)

    def test_dimensionar_descidas_np3(self) -> None:
        descidas = dimensionar_descidas(self.estrutura_predio, "NP_III")
        # P = 2 * (30 + 20) = 100m, espacamento max = 15m
        # Descidas = ceil(100 / 15) = 7
        self.assertEqual(descidas.numero_descidas_adotado, 7)
        self.assertEqual(descidas.espacamento_real_descidas_m, Fraction(100, 7))
        # H=40m, aneis a cada 20m -> 40 // 20 = 2 aneis
        self.assertEqual(descidas.quantidade_aneis_cintamento, 2)
        self.assertEqual(descidas.alturas_aneis_cintamento_m, (Fraction(20, 1), Fraction(40, 1)))
        # Total cabos = 7 * 40 + 2 * 100 = 280 + 200 = 480
        self.assertEqual(descidas.comprimento_cabos_descida_m, Fraction(480, 1))

    def test_dimensionar_aterramento(self) -> None:
        aterr = dimensionar_aterramento(self.estrutura_predio, "NP_III", numero_descidas=7)
        # Perimetro anel a 1m de distancia: 2 * (32 + 22) = 108m
        self.assertEqual(aterr.perimetro_anel_m, Fraction(108, 1))
        self.assertEqual(aterr.numero_hastes_inspecao, 7)
        # Comp total = 108 + 7 * (12/5) = 108 + 84/5 = 624/5 = 124.8
        self.assertEqual(aterr.comprimento_total_eletrodo_m, Fraction(108, 1) + Fraction(84, 5))
        self.assertEqual(aterr.secao_minima_aterramento_mm2, 50)

    def test_dimensionar_captacao_np1(self) -> None:
        captacao = dimensionar_captacao(self.estrutura_predio, "NP_I")
        self.assertEqual(captacao.nivel_protecao, "NP_I")
        self.assertEqual(captacao.raio_esfera_m, 20)
        self.assertEqual(captacao.malha_maxima_comprimento_m, 5)
        self.assertEqual(captacao.malha_maxima_largura_m, 5)
        self.assertEqual(captacao.quantidade_modulos_comprimento, 6)
        self.assertEqual(captacao.quantidade_modulos_largura, 4)
        self.assertEqual(captacao.total_modulos_malha, 24)

    def test_dimensionar_captacao_np2(self) -> None:
        captacao = dimensionar_captacao(self.estrutura_predio, "NP_II")
        self.assertEqual(captacao.nivel_protecao, "NP_II")
        self.assertEqual(captacao.raio_esfera_m, 30)
        self.assertEqual(captacao.malha_maxima_comprimento_m, 10)
        self.assertEqual(captacao.malha_maxima_largura_m, 10)

    def test_dimensionar_captacao_np4(self) -> None:
        captacao = dimensionar_captacao(self.estrutura_predio, "NP_IV")
        self.assertEqual(captacao.nivel_protecao, "NP_IV")
        self.assertEqual(captacao.raio_esfera_m, 60)
        self.assertEqual(captacao.malha_maxima_comprimento_m, 20)
        self.assertEqual(captacao.malha_maxima_largura_m, 20)

    def test_dimensionar_descidas_materiais(self) -> None:
        est_al = Estrutura(
            nome="Aluminio",
            comprimento_m=Fraction(20, 1),
            largura_m=Fraction(10, 1),
            altura_m=Fraction(15, 1),
            densidade_descargas_ng=Fraction(5, 1),
            localizacao_ambiental="isolada_plano",
            risco_incendio="ordinario",
            combate_incendio="manual",
            pessoas_em_risco=10,
            horas_ocupacao_ano=2000,
            tipo_material="aluminio",
        )
        descidas = dimensionar_descidas(est_al, "NP_III")
        self.assertIn("Alumínio", descidas.material_descida)
        self.assertEqual(descidas.secao_minima_descida_mm2, 70)

    def test_dimensionar_spda_nivel_forcado(self) -> None:
        est_forcado = Estrutura(
            nome="Forcado NP I",
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
            nivel_protecao_forcado="NP_I",
        )
        res = dimensionar_spda(est_forcado)
        self.assertEqual(res.risco.nivel_protecao_adotado, "NP_I")
        self.assertEqual(res.captacao.raio_esfera_m, 20)

    def test_dimensionar_spda_completo_conforme(self) -> None:
        res = dimensionar_spda(self.estrutura_predio, "PROJ-SPDA-TESTE")
        self.assertTrue(res.spda_conforme)
        self.assertEqual(res.identificador_projeto, "PROJ-SPDA-TESTE")
        self.assertGreater(res.comprimento_total_cabos_obra_m, 0)
        self.assertIn("Nível de Proteção Adotado", res.conclusao_tecnica)


if __name__ == "__main__":
    unittest.main()
