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

    def test_weight_above_maximum_is_an_error(self):
        """600 e valido; 600.01 e Infinity vao para a lista de erros"""
        weights, errors = self.parse('2031-01-01,600\n2031-01-02,600.01\n2031-01-03,Infinity')
        self.assertEqual([w.weight for w in weights], [Decimal('600')])
        self.assertEqual(errors, [['2031-01-02', '600.01'], ['2031-01-03', 'Infinity']])

    def test_only_1000_rows_are_read(self):
        """O limite e de 1000 linhas: a linha 1001 nao e processada"""
        rows = '\n'.join(
            (datetime.date(2031, 1, 1) + datetime.timedelta(days=i)).isoformat() + ',80'
            for i in range(1001)
        )
        weights, errors = self.parse(rows)
        self.assertEqual(len(weights), 1000)
        self.assertEqual(errors, [])

    def test_blank_lines_are_ignored(self):
        """Uma linha em branco no meio do arquivo nao e um erro do usuario"""
        weights, errors = self.parse('2031-01-01,80\n\n2031-01-02,81\n')
        self.assertEqual(len(weights), 2)
        self.assertEqual(errors, [])

    def test_semicolon_separator_with_decimal_comma(self):
        """Formato comum no Brasil: o separador nao pode ser a virgula do decimal"""
        weights, errors = self.parse('2031-01-01;80,5\n2031-01-02;81,5')
        self.assertEqual([w.weight for w in weights], [Decimal('80.5'), Decimal('81.5')])
        self.assertEqual(errors, [])

    def test_tab_separator_with_decimal_comma(self):
        """Exportacao de planilha: tabulacao com decimal em virgula"""
        weights, errors = self.parse('2031-01-01\t80,5\n2031-01-02\t81,5')
        self.assertEqual([w.weight for w in weights], [Decimal('80.5'), Decimal('81.5')])
        self.assertEqual(errors, [])
