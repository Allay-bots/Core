
#================================================================================
# Requirements
#================================================================================

import os
import sqlite3
from typing import Literal, Optional, Union, overload

import allay

#==============================================================================
# Database
#==============================================================================

class Database:
    """
    Handle the connection to our SQLite database
    """

    # Create the /data folder if it doesn't exist
    if not os.path.isdir("data"):
        os.mkdir("data")

    database = sqlite3.connect("data/database.db")

    # Load --------------------------------------------------------------------

    @staticmethod
    def load():
        "Load model files from installed plugins and builtins"
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

    @overload # fetch one row as tuple
    @staticmethod
    def query(
        query: str,
        args: Optional[Union[tuple, dict]],
        *,
        fetchone: Literal[True],
        returnrowcount: bool = False,
        astuple: Literal[True],
    ) -> tuple:
        ...

    @overload # fetch one row as dict
    @staticmethod
    def query(
        query: str,
        args: Optional[Union[tuple, dict]],
        *,
        fetchone: Literal[True],
        returnrowcount: bool = False,
        astuple: Literal[False],
    ) -> dict:
        ...

    @overload # fetch all rows as tuple
    @staticmethod
    def query(
        query: str,
        args: Optional[Union[tuple, dict]],
        *,
        fetchone: bool = False,
        returnrowcount: bool = False,
        astuple: Literal[True] = True,
    ) -> list[tuple]:
        ...

    @overload # fetch all rows as dict
    @staticmethod
    def query(
        query: str,
        args: Optional[Union[tuple, dict]],
        *,
        fetchone: bool = False,
        returnrowcount: bool = False,
        astuple: Literal[False] = False,
    ) -> list[dict]:
        ...

    @staticmethod
    def query(
        query: str,
        args: Optional[Union[tuple, dict]],
        *,
        fetchone: bool = False,
        returnrowcount: bool = False,
        astuple: bool = False,
    ) -> Union[int, list[dict], list[tuple], dict, tuple]:
        """
        Query the bot's database

        If SELECT, returns a list of results, or only the first result (if fetchone)
        For all other queries, returns the ID of the affected row, or the number of affected rows
            (if returnrowscount)

        :param query: The query to be performed
        :param args: The query arguments
        :param fetchone: If the query is a SELECT, returns only the first result
        :param returnrowcount: If the query is an INSERT, UPDATE or DELETE, returns the number of
            of affected rows
        :param astuple: If the query is a SELECT, returns the results as a tuple instead of a dict
        :return: The result of the query
        """

        cursor = Database.database.cursor()
        try:
            cursor.execute(query, args or [])
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
