"""
Database engine will use Google Sheets via gspread.
"""

from typing import Dict, List, Callable

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from message_bot.database.engines import BaseEngine


class GsheetEngine(BaseEngine):

    KEY_FIELD = '__key__'

    def __init__(self, creds_file: str, sds_name: str, wks_name: str):
        super().__init__()
        creds = credentials(creds_file)
        gclient = gspread.authorize(creds)
        self.worksheet = gclient.open(sds_name).worksheet(wks_name)

    def push(self, callback: Callable[[], None] = lambda: ...):
        rows = get_all_values(self._table)
        row_count = len(rows)
        col_count = len(rows[0])

        self.worksheet.resize(row_count, col_count)
        cells = self.worksheet.range(1, 1, row_count, col_count)
        for cell in cells:
            cell.value = rows[cell.row-1][cell.col-1]

        self.worksheet.update_cells(cells)
        callback()

    def pull(self, callback: Callable[[], None] = lambda: ...):
        records = self.worksheet.get_all_records()

        new_table = dict()
        for record in records:
            key = record[self.KEY_FIELD]
            record.pop(self.KEY_FIELD)
            filtered = {k: v for k, v in record.items() if v != ''}
            new_table[key] = filtered

        self._table = new_table
        callback()


#
# Utilities
#


def credentials(fp: str) -> ServiceAccountCredentials:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    return ServiceAccountCredentials.from_json_keyfile_name(fp, scope)


def get_all_fields(records: Dict[str, Dict[str, str]]) -> List[str]:
    fields = set()
    for values in records.values():
        fields = fields.union(values.keys())
    return [GsheetEngine.KEY_FIELD] + sorted(fields)


def get_all_values(records: Dict[str, Dict[str, str]]) -> List[List[str]]:
    fields = get_all_fields(records)
    rows = [fields]

    empty_row = ['' for _ in range(len(fields))]
    indices = {f: i for i, f in enumerate(fields)}
    for key, record in records.items():
        row = empty_row.copy()
        row[indices[GsheetEngine.KEY_FIELD]] = key
        for f, v in record.items():
            row[indices[f]] = v
        rows.append(row)

    return rows
