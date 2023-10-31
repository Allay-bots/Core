
#================================================================================
# Requirements
#================================================================================

# Standard libs ---------------------------------------------------------------

import os
import sqlite3
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, List, Optional, Union

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

    @staticmethod
    def query(
        query: str,
        args: Union[tuple, dict] = [],
        *,
        fetchone: bool = False,
        returnrowcount: bool = False,
        astuple: bool = False,
    ) -> Union[int, List[dict], dict]:
        """
        Faire une requête à la base de données du bot

        Si SELECT, retourne une liste de résultats, ou seulement le premier résultat (si fetchone)
        Pour toute autre requête, retourne l'ID de la ligne affectée, ou le nombre de lignes
        affectées (si returnrowscount)

        :param query: La requête à faire
        :param args: Les arguments de la requête
        :param fetchone: Si la requête est un SELECT, retourne seulement le premier résultat
        :param returnrowcount: Si la requête est un INSERT, UPDATE ou DELETE, retourne le nombre
            de lignes affectées
        :param astuple: Si la requête est un SELECT, retourne les résultats sous forme de tuple
        :return: Le résultat de la requête
        """

        cursor = Database.database.cursor()
        try:
            cursor.execute(query, args)
            if query.startswith("SELECT"):
                _type = tuple if astuple else dict
                if fetchone:
                    row = cursor.fetchone()
                    result = _type() if row is None else _type(row)
                else:
                    result = list(map(_type, cursor.fetchall()))
            else:
                Database.database.commit()
                if returnrowcount:
                    result = cursor.rowcount
                else:
                    result = cursor.lastrowid
        except Exception as exception:
            cursor.close()
            raise exception
        cursor.close()
        return result