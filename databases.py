from abc import ABC, abstractmethod
import os
import sqlite3


class Database(ABC):

    @abstractmethod
    def __init__(self, table_name: str, columns_type: dict[str, str]) -> None:

        self._keys = list(columns_type)
        self.__folder = os.path.join("library", "data")
        self.__primary_key = self._keys[0]
        self.__create_table_command = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column} {datatype}' for column, datatype in columns_type.items()])})"
        self.__insert_row_command = f"INSERT INTO {table_name} ({', '.join(list(columns_type))}) VALUES ({', '.join(['?' for _ in range(len(columns_type))])})"
        self.__update_column_value_command = f"UPDATE {table_name} SET column = ? WHERE {self.__primary_key} = ?"
        self.__select_row_command = f"SELECT * FROM {table_name} WHERE {self.__primary_key} = ?"
        self.__select_all_command = f"SELECT * FROM {table_name}"

        self.path = os.path.join(self.__folder ,f"{table_name}.db")
        

    def _connect(self) -> None:
        self.conn = sqlite3.connect(self.path)
        self.__cursor = self.conn.cursor()

    def _disconnect(self) -> None:
        self.conn.close()

    def _create_table(self) -> None:
        os.makedirs(self.__folder, exist_ok=True)
        self._connect()
        self.__cursor.execute(self.__create_table_command)

    def _add_row(self, row_values: dict) -> None:
        self.__cursor.execute(self.__insert_row_command, tuple(row_values.values()))
        self.conn.commit()

    def _update_column_value(self, column: str, column_value, primary_key_value) -> None:
        self.__cursor.execute(self.__update_column_value_command.replace("column", column), (column_value, primary_key_value))
        self.conn.commit()

    def _get_row(self, primary_key_value) -> tuple | None:
        self.__cursor.execute(self.__select_row_command, (primary_key_value,))
        return self.__cursor.fetchone()

    def _get_all(self) -> list[tuple]:
        self.__cursor.execute(self.__select_all_command)
        return self.__cursor.fetchall()


class GameDatabase(Database):

    def __init__(self) -> None:
        super().__init__("GameDatabase", 
                         {"steam_appid": "INTEGER PRIMARY KEY", 
                          "name": "TEXT", 
                          "description": "TEXT", 
                          "developers": "TEXT", 
                          "publishers": "TEXT", 
                          "categories": "TEXT", 
                          "genres": "TEXT", 
                          "release_date": "TEXT"})

    def add_game(self, game_data: dict) -> None:
        game_data = {key: ", ".join(value) if key[-1] == "s" else value for key, value in game_data.items()}
        self._add_row(game_data)

    def get_game(self, steam_appid: int) -> dict | None:
        game_data = self._get_row(steam_appid)
        if not game_data:
            return None

        game_data = {key: set(value.split(", ")) if key[-1] == "s" else value for key, value in zip(self._keys, game_data)}
        return game_data


class UnsuccessfulIDsDatabase(Database):

    def __init__(self) -> None:
        super().__init__("UnsuccessfulIDs", 
                         {"steam_appid": "INTEGER PRIMARY KEY"})

    def add_id(self, steam_appid: int) -> None:
        self._add_row({"steam_appid": steam_appid})

    def get_all_ids(self) -> set[int]:
        ids = {steam_appid[0] for steam_appid in self._get_all()}
        return ids


class UsersDatabase(Database):

    def __init__(self) -> None:
        super().__init__("Users", 
                         {"steam_id": "INTEGER PRIMARY KEY", 
                          "name": "TEXT", 
                          "owned_games": "TEXT", 
                          "steam_api_key": "TEXT", 
                          "steamgriddb_key": "TEXT"})

    def add_user(self, user_data: dict) -> None:
        user_data["owned_games"] = ", ".join([str(steam_appid) for steam_appid in user_data["owned_games"]])
        self._add_row(user_data)

    def update_owned_games(self, steam_id: int, owned_games: set[int]) -> None:
        self._update_column_value("owned_games", ", ".join([str(steam_appid) for steam_appid in owned_games]), steam_id)

    def update_steam_api_key(self, steam_id: int, steam_api_key: str) -> None:
        self._update_column_value("steam_api_key", steam_api_key, steam_id)

    def update_steamgriddb_key(self, steam_id: int, steamgriddb_key: str) -> None:
        self._update_column_value("steamgriddb_key", steamgriddb_key, steam_id)

    def get_user_owned_games(self, steam_id: int) -> (set[int] | None):
        user_data = self.get_user(steam_id)
        return user_data["owned_games"] if user_data else None

    def get_user(self, steam_id: int, cast_owned_games: bool = True) -> (dict | None):
        user_data = self._get_row(steam_id)
        if not user_data:
            return None

        user_data = {key: value for key, value in zip(self._keys, user_data)}
        if cast_owned_games:
            if user_data["owned_games"]:
                user_data["owned_games"] = {int(steam_appid) for steam_appid in user_data["owned_games"].split(', ')}
            else:
                user_data["owned_games"] = set()
        
        return user_data


game_db = GameDatabase()
unsuccessful_ids_db = UnsuccessfulIDsDatabase()
users_db = UsersDatabase()