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
PTOSS-2 - Funcao 3: IngredientFilterSet.search_name_fulltext

Ordem de projeto: caixa-preta (tamanhos de barcode) -> caixa-branca (MC/DC).
O ramo exclusivo de Postgres fica fora: a suite roda em SQLite.
"""

# Standard Library
from unittest.mock import patch

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.nutrition.api.filtersets import IngredientFilterSet
from wger.nutrition.models import Ingredient


FETCH = 'wger.nutrition.models.Ingredient.fetch_ingredient_from_off'


class SearchNameBase(WgerTestCase):
    def search(self, value):
        with patch(FETCH, return_value=None) as self.fetch:
            return list(
                IngredientFilterSet().search_name_fulltext(
                    Ingredient.objects.all(), 'name__search', value
                )
            )

    def set_code(self, code):
        Ingredient.objects.filter(pk=1).update(code=code)


class SearchNameBlackBoxTestCase(SearchNameBase):
    """
    Tecnica: particionamento (numerico/nao numerico) e valor limite (tamanho)
    """

    def test_valid_barcode_lengths_find_by_code(self):
        """CE1, limites validos: 8, 12, 13 e 14 digitos"""
        for length in (8, 12, 13, 14):
            with self.subTest(length=length):
                code = '7' * length
                self.set_code(code)
                self.assertEqual([i.pk for i in self.search(code)], [1])
                self.fetch.assert_not_called()

    def test_invalid_lengths_are_not_a_barcode(self):
        """CE2, limites invalidos: vizinhos de cada tamanho valido"""
        for length in (7, 9, 11, 15):
            with self.subTest(length=length):
                code = '7' * length
                self.set_code(code)
                self.assertEqual(self.search(code), [])
                self.fetch.assert_not_called()

    def test_text_finds_by_name(self):
        """CE3: texto comum busca pelo nome"""
        self.assertIn(1, [i.pk for i in self.search('Test ingredient 1')])

    def test_text_without_match_is_empty(self):
        """CE4: texto sem resultado"""
        self.assertEqual(self.search('nao existe'), [])


class SearchNameWhiteBoxTestCase(SearchNameBase):
    """
    Tecnica: MC/DC de `value.isdigit() and len(value) in (8, 12, 13, 14)` (A and B)

    | Caso | A (digitos) | B (tamanho) | Decisao |
    | T1   | T           | T           | T       |
    | T2   | F           | T           | F       |
    | T3   | T           | F           | F       |
    """

    def test_mcdc_t1_digits_and_length(self):
        self.set_code('12345678')
        self.assertEqual([i.pk for i in self.search('12345678')], [1])

    def test_mcdc_t2_length_ok_but_not_digits(self):
        self.set_code('1234567a')
        self.assertEqual(self.search('1234567a'), [])
        self.fetch.assert_not_called()

    def test_mcdc_t3_digits_but_wrong_length(self):
        self.search('1234567')
        self.fetch.assert_not_called()

    def test_decision_barcode_not_found_falls_back_to_name(self):
        """Decisao `barcode_qs.exists()` falsa: procura no OFF e depois no nome"""
        Ingredient.objects.filter(pk=1).update(name='Mix 12345678')
        self.assertEqual([i.pk for i in self.search('12345678')], [1])
        self.fetch.assert_called_once_with('12345678')
