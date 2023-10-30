
#================================================================================
# Requirements
#================================================================================

# Standard libs ---------------------------------------------------------------

import os
import sqlite3

# Modules ---------------------------------------------------------------------

import allay

#==============================================================================
# Database
#==============================================================================

class Database:

    
    if not os.path.isdir("data"):
        os.mkdir("data")
    
    database = sqlite3.connect("data/database.db")

    # Load --------------------------------------------------------------------

    @staticmethod
    def load():

        cursor = Database.database.cursor()

        # Core
        with open("allay/core/data/model.sql", "r", encoding="utf-8") as file:
            cursor.executescript(file.read())

        # Builtins
        for builtin in allay.builtins.all:
            model = os.path.join(allay.builtins.path, builtin, "data/model.sql")
            if os.path.isfile(model):
                with open(model, "r", encoding="utf-8") as file:
                    cursor.executescript(file.read())

        # Plugins
        for plugin in allay.plugins.all:
            model = os.path.join(allay.plugins.path, plugin, "data/model.sql")
            if os.path.isfile(model):
                with open(model, "r", encoding="utf-8") as file:
                    cursor.executescript(file.read())

        cursor.close()