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
PTOSS-2 - Testes criados por TDD para wger.weight.helpers.parse_weight_csv
"""

# Standard Library
import datetime
from decimal import Decimal
from types import SimpleNamespace

# Django
from django.contrib.auth.models import User

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.weight.helpers import parse_weight_csv


class WeightCsvTddTestCase(WgerTestCase):
    def parse(self, csv_input):
        request = SimpleNamespace(user=User.objects.get(username='test'))
        return parse_weight_csv(request, {'csv_input': csv_input, 'date_format': '%Y-%m-%d'})

    def test_weight_below_minimum_is_an_error(self):
        """O modelo aceita de 30 kg a 600 kg: 29.99 vai para a lista de erros"""
        weights, errors = self.parse('2031-01-01,29.99\n2031-01-02,30')
        self.assertEqual([w.weight for w in weights], [Decimal('30')])
        self.assertEqual(errors, [['2031-01-01', '29.99']])
