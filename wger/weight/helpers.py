# -*- coding: utf-8 -*-

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

# Standard Library
import csv
import datetime
import decimal
import io
import itertools
import logging

# Django
from django.utils.timezone import make_aware

# wger
from wger.weight.models import (
    MAX_WEIGHT,
    MIN_WEIGHT,
    WeightEntry,
)


logger = logging.getLogger(__name__)

MAX_ROW_COUNT = 1000


def parse_weight_csv(request, cleaned_data):
    try:
        dialect = csv.Sniffer().sniff(cleaned_data['csv_input'])
    except csv.Error:
        dialect = 'excel'

    # csv.reader expects a file-like object, so use StringIO
    parsed_csv = csv.reader(io.StringIO(cleaned_data['csv_input']), dialect)
    distinct_weight_entries = []
    entry_dates = set()
    weight_list = []
    error_list = []

    # Process the CSV items first
    for row in itertools.islice(parsed_csv, MAX_ROW_COUNT):
        try:
            parsed_date = make_aware(
                datetime.datetime.strptime(row[0], cleaned_data['date_format'])
            )
            parsed_weight = decimal.Decimal(row[1].replace(',', '.'))
            duplicate_date_in_db = WeightEntry.objects.filter(
                date=parsed_date, user=request.user
            ).exists()
            # within the list there are no duplicate dates
            unique_among_csv = parsed_date not in entry_dates

            # there is no existing weight entry in the database for that date
            unique_in_db = not duplicate_date_in_db

            # the weight respects the same limits as the model
            weight_in_range = MIN_WEIGHT <= parsed_weight <= MAX_WEIGHT

            if unique_among_csv and unique_in_db and weight_in_range:
                distinct_weight_entries.append((parsed_date, parsed_weight))
                entry_dates.add(parsed_date)
            else:
                error_list.append(row)

        except (ValueError, IndexError, decimal.InvalidOperation):
            error_list.append(row)

    # Create the valid weight entries
    for date, weight in distinct_weight_entries:
        weight_list.append(WeightEntry(date=date, weight=weight, user=request.user))

    return weight_list, error_list
