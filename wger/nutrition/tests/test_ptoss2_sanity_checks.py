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
PTOSS-2 - Funcao 2: IngredientData.sanity_checks

Ordem de projeto: caixa-branca (decisoes e MC/DC) -> caixa-preta (limites).
D1, D2... sao as decisoes numeradas no relatorio.
"""

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.dataclasses import IngredientData
from wger.utils.constants import CC_0_LICENSE_ID


def make_data(**overrides):
    """Ingrediente valido: 10g de proteina = 40 kcal"""
    data = {
        'name': 'Foo',
        'remote_id': '1',
        'language_id': 1,
        'energy': 40.0,
        'protein': 10.0,
        'carbohydrates': 0.0,
        'carbohydrates_sugar': None,
        'fat': 0.0,
        'fat_saturated': None,
        'fiber': None,
        'sodium': None,
        'code': None,
        'source_name': 'USDA',
        'source_url': '',
        'common_name': None,
        'brand': None,
        'license_id': CC_0_LICENSE_ID,
        'license_author': '',
        'license_title': '',
        'license_object_url': '',
    }
    data.update(overrides)
    return IngredientData(**data)


class SanityChecksWhiteBoxTestCase(SimpleTestCase):
    """
    Tecnica: cobertura de decisoes e MC/DC
    """

    def test_d1_empty_name_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Name is empty'):
            make_data(name='').sanity_checks()

    def test_d4_mcdc_value_none_is_allowed(self):
        """D4 (A=F): nutriente opcional ausente"""
        make_data(fiber=None).sanity_checks()

    def test_d4_mcdc_value_number_is_allowed(self):
        """D4 (A=T, B=F): valor presente e numerico"""
        make_data(fiber=1).sanity_checks()

    def test_d4_mcdc_value_text_is_rejected(self):
        """D4 (A=T, B=T): valor presente e nao numerico"""
        with self.assertRaisesRegex(ValueError, 'is not a number'):
            make_data(fiber='abc').sanity_checks()

    def test_d5_mcdc_zero_short_circuits(self):
        """D5 (A=F): zero nao passa na primeira condicao"""
        make_data(sodium=0).sanity_checks()

    def test_d5_mcdc_true_true_rejected(self):
        """D5 (A=T, B=T)"""
        with self.assertRaisesRegex(ValueError, 'greater than 100'):
            make_data(sodium=100.1).sanity_checks()

    def test_d5_mcdc_true_false_allowed(self):
        """D5 (A=T, B=F), tambem o limite exato de 100"""
        make_data(sodium=100).sanity_checks()

    def test_d6_mcdc_saturated_absent(self):
        """D6 (A=F)"""
        make_data(fat=2.0, energy=58.0, fat_saturated=None).sanity_checks()

    def test_d6_mcdc_saturated_not_greater(self):
        """D6 (A=T, B=F), com o limite saturada == gordura"""
        make_data(fat=2.0, energy=58.0, fat_saturated=2.0).sanity_checks()

    def test_d6_mcdc_saturated_greater(self):
        """D6 (A=T, B=T)"""
        with self.assertRaisesRegex(ValueError, 'Saturated fat'):
            make_data(fat=2.0, energy=58.0, fat_saturated=2.1).sanity_checks()

    def test_d7_mcdc_sugar_absent(self):
        """D7 (A=F)"""
        make_data(carbohydrates=5.0, energy=60.0, carbohydrates_sugar=None).sanity_checks()

    def test_d7_mcdc_sugar_not_greater(self):
        """D7 (A=T, B=F), com o limite acucar == carboidrato"""
        make_data(carbohydrates=5.0, energy=60.0, carbohydrates_sugar=5.0).sanity_checks()

    def test_d7_mcdc_sugar_greater(self):
        """D7 (A=T, B=T)"""
        with self.assertRaisesRegex(ValueError, 'Sugar'):
            make_data(carbohydrates=5.0, energy=60.0, carbohydrates_sugar=5.1).sanity_checks()

    def test_d9_mcdc_nutriscore_absent(self):
        """D9 (A=F)"""
        make_data(nutriscore=None).sanity_checks()

    def test_d9_mcdc_nutriscore_valid(self):
        """D9 (A=T, B=F)"""
        make_data(nutriscore='a').sanity_checks()

    def test_d9_mcdc_nutriscore_invalid(self):
        """D9 (A=T, B=T)"""
        with self.assertRaisesRegex(ValueError, 'nutriscore'):
            make_data(nutriscore='z').sanity_checks()

    def test_d10_mcdc_both_below_minimum_skip_the_check(self):
        """D10 (A=F, B=F): 13 kcal declaradas, 0 calculadas: nao compara"""
        make_data(energy=13, protein=0.0).sanity_checks()

    def test_d10_mcdc_declared_above_minimum(self):
        """D10 (A=T, B=F): 14 kcal declaradas, 0 calculadas: compara e rejeita"""
        with self.assertRaisesRegex(ValueError, 'does not match'):
            make_data(energy=14, protein=0.0).sanity_checks()

    def test_d10_mcdc_computed_above_minimum(self):
        """D10 (A=F, B=T): 0 kcal declaradas, 14 calculadas: compara e rejeita"""
        with self.assertRaisesRegex(ValueError, 'does not match'):
            make_data(energy=0, protein=3.5).sanity_checks()


class SanityChecksBlackBoxTestCase(SimpleTestCase):
    """
    Tecnica: valor limite e particionamento, complementando a analise estrutural
    """

    def test_name_is_truncated_at_200(self):
        """Limite: 201 caracteres vira 200"""
        data = make_data(name='a' * 201)
        data.sanity_checks()
        self.assertEqual(len(data.name), 200)

    def test_name_with_200_is_kept(self):
        """Limite: exatamente 200 fica igual"""
        data = make_data(name='a' * 200)
        data.sanity_checks()
        self.assertEqual(data.name, 'a' * 200)

    def test_optional_texts_are_truncated_when_present(self):
        """D2/D3 verdadeiras: marca e nome comum tambem sao cortados"""
        data = make_data(brand='b' * 201, common_name='c' * 201)
        data.sanity_checks()
        self.assertEqual(len(data.brand), 200)
        self.assertEqual(len(data.common_name), 200)

    def test_macro_sum_on_the_limit_is_allowed(self):
        """D8, limite: soma de exatamente 105 g"""
        make_data(protein=50.0, carbohydrates=50.0, fat=5.0, energy=445.0).sanity_checks()

    def test_macro_sum_above_the_limit_is_rejected(self):
        """D8, limite: soma logo acima de 105 g"""
        with self.assertRaisesRegex(ValueError, 'greater than 105'):
            make_data(protein=50.0, carbohydrates=50.0, fat=5.1, energy=446.0).sanity_checks()

    def test_energy_on_the_tolerance_limits_is_allowed(self):
        """D11, limites: declaradas 100 kcal aceitam de 65 a 135 calculadas"""
        make_data(energy=100, protein=16.5).sanity_checks()
        make_data(energy=100, protein=33.5).sanity_checks()

    def test_energy_below_the_tolerance_is_rejected(self):
        """D11: calculadas abaixo de 65"""
        with self.assertRaisesRegex(ValueError, 'does not match'):
            make_data(energy=100, protein=16.0).sanity_checks()

    def test_energy_above_the_tolerance_is_rejected(self):
        """D11: calculadas acima de 135"""
        with self.assertRaisesRegex(ValueError, 'does not match'):
            make_data(energy=100, protein=34.0).sanity_checks()
