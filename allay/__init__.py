
import os
import sqlite3

from allay import core
from allay import plugins

data_model = "allay/core/data/model.sql"
database = sqlite3.connect("allay/core/data/database.db")

def update_database_structure():
    cursor = database.cursor()
    with open(data_model, "r", encoding="utf-8") as file:
        cursor.executescript(file.read())

    # pylint: disable=redefined-outer-name
    for plugin in plugins.all:
        if os.path.isfile(plugins.path + plugin + "/data/model.sql"):
            with open("./plugins/" + plugin + "/data/model.sql", "r", encoding="utf-8") as file:
                cursor.executescript(file.read())
    cursor.close()

update_database_structure()