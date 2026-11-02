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
PTOSS-2 - Testes criados por TDD para a validacao de ingredientes
"""

# Django
from django.test import SimpleTestCase

# wger
from wger.nutrition.models import Ingredient
from wger.nutrition.tests.test_ptoss2_sanity_checks import make_data


class IngredientValidationTddTestCase(SimpleTestCase):
    def test_negative_macro_is_rejected(self):
        """Nao existe quantidade negativa de um nutriente"""
        with self.assertRaisesRegex(ValueError, 'negative'):
            make_data(sodium=-1).sanity_checks()

    def test_negative_energy_is_rejected(self):
        """-1 kcal passava: declarada e calculada ficam abaixo do minimo de 13 kcal"""
        with self.assertRaisesRegex(ValueError, 'negative'):
            make_data(energy=-1, protein=0.0).sanity_checks()
