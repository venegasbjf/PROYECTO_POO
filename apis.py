from concurrent.futures import as_completed, ThreadPoolExecutor
import time
from typing import Callable

import requests

from logger import logger


class RequestArgumentsDict(dict):


    def __init__(self, url: str, params: (dict | None) = None, headers: (dict | None) = None, timeout: (float | None) = 5):
        self["url"] = url
        self["params"] = params
        self["headers"] = headers
        self["timeout"] = timeout


class API:


    def __init__(self, api_key: str) -> None:

        self.api_key = api_key
        self.responses: list[requests.Response] = []


    def _make_get_request(self, arguments: RequestArgumentsDict) -> requests.Response:

        response = requests.get(arguments["url"], arguments["params"],
                                headers=arguments["headers"], timeout=arguments["timeout"])
        
        response.raise_for_status()

        return response


    def _make_get_requests(self, arguments_list: list[RequestArgumentsDict]) -> None:

        with ThreadPoolExecutor(max_workers=5) as executor:

            futures = [executor.submit(self._make_get_request, arguments)
                       for arguments in arguments_list]

            for future in as_completed(futures):
                try:
                    response = future.result()
                    self.responses.append(response)
                except requests.exceptions.Timeout as e:
                    logger.error("Timeout Error:", e)
    

    def _make_get_requests_in_chunks(self, arguments_list: list[RequestArgumentsDict], chunk_size: int, cooldown_seconds: float, do_meanwhile: (Callable | None)) -> None:

        chunked_arguments = [arguments_list[i:i + chunk_size]
                             for i in range(0, len(arguments_list), chunk_size)]

        for arguments_list in chunked_arguments:

            self._make_get_requests(arguments_list)

            start = time.time()

            if do_meanwhile is not None:
                do_meanwhile()

            missing_time = cooldown_seconds - time.time() + start

            if missing_time > 0:
                time.sleep(missing_time)


class SteamAPI(API):


    def get_owned_games(self, steam_id: int) -> requests.Response:

        arguments = RequestArgumentsDict("https://api.steampowered.com/IPlayerService/GetOwnedGames/v1",
                                         {"key": self.api_key, "steamid": steam_id, "include_appinfo": 1},
                                         timeout=15)

        response = self._make_get_request(arguments)
        
        return response


    def apps_details(self, games_ids: list[int], do_between_chunks: Callable) -> None:

        params_list = [{"key": self.api_key, "appids": game_id} for game_id in games_ids]
        arguments_list = [RequestArgumentsDict("http://store.steampowered.com/api/appdetails", params, timeout=10)  for params in params_list]

        self._make_get_requests_in_chunks(arguments_list, 50, 72.5, do_between_chunks)

    
    def get_player_summaries(self, steam_id: int) -> requests.Response:

        arguments = RequestArgumentsDict("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002",
                                         {"key": self.api_key, "steamids": steam_id}, timeout=15)

        response = self._make_get_request(arguments)
        
        return response


class SteamGridAPI(API):


    def steam_grids(self, game_id: int) -> requests.Response:

        arguments = RequestArgumentsDict(f"https://www.steamgriddb.com/api/v2/grids/steam/{game_id}", 
                                         {"dimensions": "600x900"}, {"Authorization": f"Bearer {self.api_key}"}, 10)
        
        response = self._make_get_request(arguments)

        return response

    
    def steam_heroes(self, game_id: int) -> requests.Response:

        arguments = RequestArgumentsDict(f"https://www.steamgriddb.com/api/v2/heroes/steam/{game_id}", 
                                         {"dimensions": "1920x620"}, {"Authorization": f"Bearer {self.api_key}"}, 10)
        
        response = self._make_get_request(arguments)

        return response


steam_api = SteamAPI("EA29ED634385FF016C0B0363F3F23D27")
steam_grid_api = SteamGridAPI("da02ff927bc9816956aa864cf62ba4ba")