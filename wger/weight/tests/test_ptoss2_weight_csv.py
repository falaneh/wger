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
PTOSS-2 - Funcao 4: wger.weight.helpers.parse_weight_csv

Ordem de projeto: caixa-branca (MC/DC) -> caixa-preta (classes e limites).
"""

# Standard Library
import datetime
from decimal import Decimal
from types import SimpleNamespace

# Django
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.weight.helpers import parse_weight_csv
from wger.weight.models import WeightEntry


class WeightCsvBase(WgerTestCase):
    def parse(self, csv_input, date_format='%Y-%m-%d'):
        request = SimpleNamespace(user=User.objects.get(username='test'))
        return parse_weight_csv(request, {'csv_input': csv_input, 'date_format': date_format})


class WeightCsvWhiteBoxTestCase(WeightCsvBase):
    """
    Tecnica: MC/DC de `unique_among_csv and unique_in_db and parsed_weight` (A and B and C)

    | Caso | A | B | C | Decisao |
    | T1   | T | T | T | T       |
    | T2   | F | T | T | F       |
    | T3   | T | F | T | F       |
    | T4   | T | T | F | F       |

    Pares: A = T1-T2, B = T1-T3, C = T1-T4.
    """

    def test_mcdc_t1_valid_row(self):
        weights, errors = self.parse('2031-01-01,80')
        self.assertEqual([w.weight for w in weights], [Decimal('80')])
        self.assertEqual(errors, [])

    def test_mcdc_t2_date_repeated_in_csv(self):
        weights, errors = self.parse('2031-01-01,80\n2031-01-01,81')
        self.assertEqual(len(weights), 1)
        self.assertEqual(errors, [['2031-01-01', '81']])

    def test_mcdc_t3_date_already_in_database(self):
        user = User.objects.get(username='test')
        date = make_aware(datetime.datetime(2031, 1, 1))
        WeightEntry.objects.create(user=user, date=date, weight=Decimal('70'))

        weights, errors = self.parse('2031-01-01,80')
        self.assertEqual(weights, [])
        self.assertEqual(errors, [['2031-01-01', '80']])

    def test_mcdc_t4_weight_zero(self):
        weights, errors = self.parse('2031-01-01,0')
        self.assertEqual(weights, [])
        self.assertEqual(errors, [['2031-01-01', '0']])

    def test_branch_sniffer_error_uses_excel_dialect(self):
        """Branch do except csv.Error: entrada vazia, sem delimitador detectavel"""
        self.assertEqual(self.parse(''), ([], []))


class WeightCsvBlackBoxTestCase(WeightCsvBase):
    """
    Tecnica: particionamento de equivalencia e valor limite
    """

    def test_ce1_decimal_point_and_comma_separator(self):
        """CE1: separador virgula e decimal com ponto"""
        weights, errors = self.parse('2031-01-01,80.5\n2031-01-02,81.5')
        self.assertEqual([w.weight for w in weights], [Decimal('80.5'), Decimal('81.5')])
        self.assertEqual(errors, [])

    def test_ce2_invalid_date(self):
        """CE2: data fora do formato"""
        self.assertEqual(self.parse('01/01/2031,80')[0], [])

    def test_ce3_invalid_weight(self):
        """CE3: peso nao numerico"""
        self.assertEqual(self.parse('2031-01-01,abc')[0], [])

    def test_ce4_missing_column(self):
        """CE4: linha sem a coluna do peso"""
        weights, errors = self.parse('2031-01-01')
        self.assertEqual(weights, [])
        self.assertEqual(len(errors), 1)

    def test_entries_belong_to_the_request_user(self):
        """Saida: o registro criado pertence ao usuario da requisicao"""
        weights, _ = self.parse('2031-01-01,80')
        self.assertEqual(weights[0].user.username, 'test')

    def test_limit_inside_row_limit(self):
        """Limite: 999 linhas dentro do maximo sao todas lidas"""
        rows = '\n'.join(
            (datetime.date(2031, 1, 1) + datetime.timedelta(days=i)).isoformat() + ',80'
            for i in range(999)
        )
        self.assertEqual(len(self.parse(rows)[0]), 999)
