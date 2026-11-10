from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from spda_nbr5419.calculator import dimensionar_spda
from spda_nbr5419.codecs import (
    JSONCodecError,
    carregar_entrada_json,
    exportar_resultado_json,
    fracao_para_dict,
    parsear_fracao_segura,
)
from spda_nbr5419.models import Estrutura


class TestCodecs(unittest.TestCase):
    def test_parsear_fracao_segura(self) -> None:
        self.assertEqual(parsear_fracao_segura(10), Fraction(10, 1))
        self.assertEqual(parsear_fracao_segura("25/4"), Fraction(25, 4))
        self.assertEqual(parsear_fracao_segura({"num": 7, "den": 3}), Fraction(7, 3))
        self.assertEqual(parsear_fracao_segura(Fraction(5, 2)), Fraction(5, 2))

    def test_parsear_fracao_segura_erro_tipo(self) -> None:
        with self.assertRaises(JSONCodecError):
            parsear_fracao_segura([1, 2])

    def test_parsear_fracao_segura_erro_str(self) -> None:
        with self.assertRaises(JSONCodecError):
            parsear_fracao_segura("invalido")

    def test_fracao_para_dict(self) -> None:
        d = fracao_para_dict(Fraction(3, 4))
        self.assertEqual(d["num"], 3)
        self.assertEqual(d["den"], 4)
        self.assertEqual(d["str"], "3/4")

    def test_carregar_entrada_json_valida(self) -> None:
        json_txt = """{
            "nome": "Edifício Alfa",
            "comprimento_m": "40",
            "largura_m": "25",
            "altura_m": "50",
            "densidade_descargas_ng": "10",
            "localizacao_ambiental": "isolada_plano",
            "risco_incendio": "ordinario",
            "combate_incendio": "manual",
            "pessoas_em_risco": 100,
            "horas_ocupacao_ano": 8760,
            "tipo_material": "cobre"
        }"""
        est = carregar_entrada_json(json_txt)
        self.assertEqual(est.nome, "Edifício Alfa")
        self.assertEqual(est.comprimento_m, Fraction(40, 1))
        self.assertEqual(est.largura_m, Fraction(25, 1))

    def test_carregar_entrada_json_sem_campos_obrigatorios(self) -> None:
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json('{"nome": "Incompleto"}')

    def test_carregar_entrada_json_raiz_nao_dict(self) -> None:
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json('["lista", 1, 2]')

    def test_rejeicao_bom_bytes_e_str(self) -> None:
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(b"\xef\xbb\xbf{}")
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json("\ufeff{}")

    def test_rejeicao_ponto_flutuante(self) -> None:
        json_com_float = '{"nome": "Teste", "comprimento_m": 25.5, "largura_m": 10, "altura_m": 20, "densidade_descargas_ng": 5}'
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(json_com_float)

    def test_rejeicao_chaves_duplicadas(self) -> None:
        json_duplicado = '{"nome": "A", "nome": "B", "comprimento_m": 10, "largura_m": 10, "altura_m": 10, "densidade_descargas_ng": 1}'
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(json_duplicado)

    def test_rejeicao_profundidade_excessiva(self) -> None:
        d: dict[str, object] = {"fim": 1}
        for _ in range(40):
            d = {"sub": d}
        with self.assertRaises(JSONCodecError):
            carregar_entrada_json(json.dumps(d))

    def test_exportar_resultado_json(self) -> None:
        est = Estrutura(
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
        res = dimensionar_spda(est)
        json_str = exportar_resultado_json(res)
        self.assertIn("ABNT NBR 5419:2015", json_str)
        self.assertIn("LOFRANO TECNOLOGIA", json_str)
        dados = json.loads(json_str)
        self.assertTrue(dados["conforme"])


if __name__ == "__main__":
    unittest.main()
