import os
import random
import re
import requests

from apis import steam_api, steam_grid_api
from logger import logger
from databases import game_db, unsuccessful_ids_db, users_db

from concurrent.futures import ThreadPoolExecutor



class GamesData:


    def __init__(self, steam_id: int) -> None:

        self.steam_id = steam_id

        self.owned_games = self.__get_owned_games().difference(self.__get_unsuccessful_ids())

        self.games_data = self.__get_games_data_from_game_db()

        self.games_images_paths = self.__get_games_images_paths()

        self.__request_games_data()


    def __get_unsuccessful_ids(self) -> set[int]:

        unsuccesful_apps = set()

        if os.path.exists(unsuccessful_ids_db.path):

            unsuccessful_ids_db._connect()

            unsuccesful_apps = unsuccessful_ids_db.get_all_ids()

            unsuccessful_ids_db._disconnect()

        return unsuccesful_apps
    

    def __get_owned_games_from_steam_api(self) -> (set[int] | None):

        try:
            owned_games_response = steam_api.get_owned_games(self.steam_id)
            owned_games = {game["appid"] for game in owned_games_response.json()["response"]["games"]}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ocurrio un error al hacer el request de los juegos de la cuenta {self.steam_id}: {e}")
        
        except KeyError:
            logger.error(f"El request se realizo correctamente sin embargo no hubo respuesta, esto posiblemente se deba a que la cuenta {self.steam_id} no es publica")
        
        else:

            users_db._create_table()

            users_db.update_owned_games(self.steam_id, owned_games)

            users_db._disconnect()

            return owned_games
    

    def __get_owned_games_from_users_db(self) -> (set[int] | None):

        if os.path.exists(users_db.path):

            users_db._connect()

            owned_games = users_db.get_user_owned_games(self.steam_id)

            users_db._disconnect()

            return owned_games
            
        
    def __get_owned_games(self) -> set[int]:

        owned_games = self.__get_owned_games_from_steam_api()

        if not owned_games:

            owned_games = self.__get_owned_games_from_users_db()

            if not owned_games:

                raise Exception("No se encontro los juegos de la cuenta")

        return owned_games
    

    def __get_games_data_from_game_db(self) -> dict[int, dict]:

        games_data = {}
        
        if os.path.exists(game_db.path):

            game_db._connect()

            for game_id in self.owned_games:

                game_data = game_db.get_game(game_id)

                if game_data:

                    games_data[game_id] = game_data

            game_db._disconnect()

        return games_data
        
    
    def __get_games_images_paths(self) -> dict[int, dict[str, str | None]]:

        games_images_paths = {game_id: {"library_600x900_path": None, "library_hero_path": None} for game_id in self.owned_games}

        images_folder_path = os.path.join("library", "images")

        if os.path.exists(images_folder_path):

            pattern = r"(library_600x900|library_hero)\.(jpg|png|webp)"

            for game_id in self.owned_games:

                game_images_path = os.path.join(images_folder_path, str(game_id))

                if not os.path.exists(game_images_path):
                    continue

                images_files = [file for file in os.listdir(game_images_path) if re.fullmatch(pattern, file)]

                library_600x900 = None
                library_hero = None

                for image_file in images_files:

                    if not library_600x900 and "library_600x900" in image_file:

                        library_600x900 = image_file

                        games_images_paths[game_id]["library_600x900_path"] = os.path.join(game_images_path, library_600x900)

                    elif not library_hero and "library_hero" in image_file:

                        library_hero = image_file

                        games_images_paths[game_id]["library_hero_path"] = os.path.join(game_images_path, library_hero)

                    if library_600x900 and library_hero:
                        break
        
        return games_images_paths

    
    def __download_images_from_steam_and_add_paths(self, games_ids: list[int]) -> None:

        images_folder_path = os.path.join("library", "images")

        key_image_url = {"library_600x900_path": ("library_600x900", "library_600x900_2x"), "library_hero_path": ("library_hero", "library_hero")}

        for game_id in games_ids:

            game_images_path = os.path.join(images_folder_path, str(game_id))

            # Creates directory if not exist
            os.makedirs(game_images_path, exist_ok=True)

            for key, path in self.games_images_paths[game_id].items():

                if not path:

                    image_path = os.path.join(game_images_path, key_image_url[key][0])

                    url = f"https://steamcdn-a.akamaihd.net/steam/apps/{game_id}/{key_image_url[key][1]}.jpg"

                    try:

                        response = requests.get(url, timeout=10)
                        response.raise_for_status()

                        try:

                            with open(image_path + ".jpg", "wb") as image_file:

                                image_file.write(response.content)

                            self.games_images_paths[game_id][key] = image_path + ".jpg"

                        except IOError as e:
                            logger.error(e)

                    except requests.exceptions.ConnectionError as e:
                        logger.error(e)
                        raise

                    except requests.exceptions.RequestException as e:
                        logger.error(e)
                        self.__download_image_from_steam_grid_and_add_path(game_id, key_image_url[key][0], image_path)


    def __download_image_from_steam_grid_and_add_path(self, game_id: int, image: str, image_path: str) -> None:

        image_request = {"library_600x900": steam_grid_api.steam_grids, "library_hero": steam_grid_api.steam_heroes}

        try:

            response = image_request[image](game_id)
            response.raise_for_status()

            images_urls = response.json()

            if images_urls["success"]:
                
                try:
                    random_image_data = random.choice(images_urls["data"])

                    url = random_image_data["url"]
                    extension = re.findall(r"(.jpg|.png|.webp)", url)[0]

                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    try:

                        with open(image_path + extension, "wb") as image_file:

                            image_file.write(response.content)

                        self.games_images_paths[game_id][f"{image}_path"] = image_path + extension

                    except IOError as e:
                        logger.error(e)

                except IndexError as e:
                    logger.error(e)

        except requests.exceptions.ConnectionError as e:
            logger.error(e)
            raise

        except requests.exceptions.RequestException as e:
            logger.error(e)


    def __get_games_data_from_requests(self) -> None:
        games_data = {}
        
        game_db._create_table()
        unsuccessful_ids_db._create_table()

        for response in steam_api.responses:

            game_id, details = next(iter(response.json().items()))
            game_id = int(game_id)

            if not details.get("success"):
                unsuccessful_ids_db.add_id(game_id)
                continue

            data = details["data"]
            game_data = {
                "steam_appid": game_id,
                "name": data["name"],
                "release_date": data["release_date"]["date"],
                "description": data.get("detailed_description", ""),
                "developers": set(data.get("developers", [])),
                "publishers": set(data.get("publishers", [])),
                "categories": {c["description"] for c in data.get("categories", [])},
                "genres": {g["description"] for g in data.get("genres", [])},
            }

            games_data[game_id] = game_data
            game_db.add_game(game_data)

        game_db._disconnect()
        unsuccessful_ids_db._disconnect()

        steam_api.responses.clear()

        self.games_data.update(games_data)
        self.__download_images_from_steam_and_add_paths(list(games_data))

    
    def __request_games_data(self) -> None:
        games_with_data = list(self.games_data)
        games_without_data = [game_id for game_id in self.owned_games if game_id not in self.games_data]

        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(steam_api.apps_details, games_without_data, self.__get_games_data_from_requests)
            future2 = executor.submit(self.__download_images_from_steam_and_add_paths, games_with_data)
            future1.result()
            future2.result()

        self.__get_games_data_from_requests()
