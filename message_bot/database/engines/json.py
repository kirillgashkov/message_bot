"""
Database engine will use local JSON file.
"""

import os.path
import json
from typing import Callable

from message_bot import database


class JSONEngine(database.engines.BaseEngine):

    def __init__(self, fp: str):
        super().__init__()
        self.filepath = fp
        self.pull()

    def push(self, callback: Callable[[], None] = lambda: ...):
        with open(self.filepath, 'w') as f:
            json.dump(self.table, f)
        callback()

    def pull(self, callback: Callable[[], None] = lambda: ...):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                new_table = json.load(f)
        else:
            new_table = dict()
        self.table = new_table
        callback()
