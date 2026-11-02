# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

"""
PTOSS-2 - Funcao 1: Ingredient._derive_serving_size_gram

Ordem de projeto: caixa-preta (classes e limites) -> caixa-branca (MC/DC).
Os identificadores CE1, CE2... sao as classes de equivalencia do relatorio.
"""

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.models import Ingredient


derive = Ingredient._derive_serving_size_gram


class ServingSizeBlackBoxTestCase(SimpleTestCase):
    """
    Tecnica: particionamento de equivalencia e analise de valor limite
    """

    def test_ce1_ce5_volume_units_are_converted(self):
        """CE1+CE5: quantidade positiva e unidade conhecida; uma por fator"""
        self.assertEqual(derive(250, 'ml'), 250)
        self.assertEqual(derive(33, 'cl'), 330)
        self.assertEqual(derive(2, 'dl'), 200)
        self.assertEqual(derive(1.5, 'l'), 1500)

    def test_ce1_ce5_singular_names_and_spellings(self):
        """CE1+CE5: variacoes de grafia sao a mesma classe"""
        self.assertEqual(derive(1, 'litre'), 1000)
        self.assertEqual(derive(1, 'liter'), 1000)
        self.assertEqual(derive(1, 'milliliter'), 1)

    def test_ce6_unit_case_and_spaces_are_ignored(self):
        """CE6: unidade com maiusculas e espacos e normalizada"""
        self.assertEqual(derive(1, ' L '), 1000)

    def test_ce7_unknown_unit_returns_none(self):
        """CE7: unidade fora da tabela nao tem conversao"""
        self.assertIsNone(derive(100, 'kg'))
        self.assertIsNone(derive(100, 'g'))

    def test_ce4_non_numeric_amount_returns_none(self):
        """CE4: texto que nao e numero cai no except ValueError"""
        self.assertIsNone(derive('abc', 'ml'))

    def test_ce1_numeric_text_amount_is_accepted(self):
        """CE1: numero em texto e convertido"""
        self.assertEqual(derive('250', 'ml'), 250)

    def test_limit_smallest_amount_that_rounds_to_one_gram(self):
        """Valor limite: 0.5 ml e 0.6 ml em volta do arredondamento"""
        self.assertEqual(derive(0.6, 'ml'), 1)
        self.assertEqual(derive(0.5, 'ml'), 0)


class ServingSizeWhiteBoxTestCase(SimpleTestCase):
    """
    Tecnica: MC/DC da decisao `not amount or not unit` (A or B)

    | Caso | A (not amount) | B (not unit) | Decisao |
    | T1   | F              | F            | F       |
    | T2   | T              | F            | T       |
    | T3   | F              | T            | T       |

    Par de A: T1-T2. Par de B: T1-T3.
    """

    def test_mcdc_t1_both_present(self):
        self.assertEqual(derive(1, 'ml'), 1)

    def test_mcdc_t2_amount_missing(self):
        self.assertIsNone(derive(0, 'ml'))
        self.assertIsNone(derive(None, 'ml'))

    def test_mcdc_t3_unit_missing(self):
        self.assertIsNone(derive(1, ''))
        self.assertIsNone(derive(1, None))

    def test_branch_type_error_in_conversion(self):
        """Branch do except: um tipo que float() recusa"""
        self.assertIsNone(derive([1], 'ml'))
