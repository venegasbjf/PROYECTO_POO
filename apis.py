from __future__ import annotations

import time

from abc import ABC

from logger import logger

from requests import get, Response, Timeout, ConnectionError, HTTPError, RequestException

from typing import Iterable

from random import choice


class Request:
    
    def __init__(self, url: str, params: (dict[str] | None) = None, headers: (dict[str] | None) = None, timeout: (float | None) = 5) -> None:
        self.url = url
        self.params = params
        self.headers = headers
        self.timeout = timeout


class API(ABC):

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _make_get_request(self, request: Request) -> Response:
        response = get(request.url, request.params, headers=request.headers, timeout=request.timeout)
        response.raise_for_status()
        return response
    
    def _make_tolerant_get_request(self, request: Request) -> (Response | None):
        try:
            return self._make_get_request(request)
            
        except ConnectionError as e:
            logger.error(repr(e))
            raise
            
        except HTTPError as e:
            logger.error(repr(e))
            
        except RequestException as e:
            logger.error(repr(e))

    def _make_get_requests(self, requests: list[Request], save_responses: list[Response]) -> None:
        while len(requests) > 0:

            try:
                response = self._make_get_request(requests[-1])
                save_responses.append(response)
                del requests[-1]

            except Timeout as e:
                logger.error(repr(e))

            except ConnectionError as e:
                logger.error(repr(e))
                raise

            except HTTPError as e:
                logger.error(repr(e))
                raise

            except RequestException as e:
                logger.error(repr(e))
                raise

    def _make_get_requests_in_chunks(self, requests: list[Request], chunk_size: int, chunk_wait_sec: float) -> list[Response]:
        chunked_requests = [requests[start_slice:start_slice+chunk_size] for start_slice in range(0, len(requests), chunk_size)]
        responses = []
        
        while len(chunked_requests) > 0:

            try:
                self._make_get_requests(chunked_requests[-1], responses)
                del chunked_requests[-1]
                
            except ConnectionError as e:
                logger.warning("Conexión perdida: "+ repr(e))
                break
            
            except RequestException as e:
                logger.warning("Ocurrio un error mientras se realizaban peticiones a la API: " + repr(e))  
                break
                
            if chunked_requests:
                time.sleep(chunk_wait_sec)
            
        return responses
    
    def _request_image_bytes(self, url: str) -> (bytes | None):
        request = Request(url)
        response = self._make_tolerant_get_request(request)
        image_bytes = response.content if response else None 
        return image_bytes


class SteamAPI(API):

    def get_player_summaries(self, steam_id: str) -> (dict[str, str] | None):
        request = Request("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002", {"key": self._api_key, "steamids": steam_id})
        response = self._make_get_request(request).json()["response"]["players"]
        player_summaries = {"steamid": steam_id, "personaname": response[0]["personaname"], "avatarfull": response[0]["avatarfull"], "profileurl": response[0]["profileurl"]} if response else None
        return player_summaries

    def get_owned_games(self, steam_id: str) -> (dict[int, str] | None):
        request = Request("https://api.steampowered.com/IPlayerService/GetOwnedGames/v1", {"key": self._api_key, "steamid": steam_id, "include_appinfo": 1})
        response = self._make_get_request(request).json()["response"]
        owned_games = {game["appid"]: game["name"] for game in response["games"]} if response else None
        return owned_games

    def get_apps_details(self, steam_apps_ids: Iterable[int], owned_games: dict[int, str]) -> dict[int, dict[str]]:
        requests = [Request("http://store.steampowered.com/api/appdetails", {"key": self._api_key, "appids": steam_appid}) for steam_appid in steam_apps_ids]
        responses = self._make_get_requests_in_chunks(requests, 65, 70)
        apps_details = {}
        
        for response in responses:
            
            steam_appid, response = response.json().popitem()
            steam_appid = int(steam_appid)
            app_details = {}
            data = response.get("data", {})
                
            app_details["description"] = data.get("detailed_description", "")
            app_details["developers"] = data.get("developers", [])
            app_details["publishers"] = data.get("publishers", [])
            app_details["categories"] = [categorie["description"] for categorie in data.get("categories", [])]
            app_details["genres"] = [genre["description"] for genre in data.get("genres", [])]
            app_details["release_date"] = data.get("release_date", {}).get("date", "")
            app_details["name"] = owned_games[steam_appid]
            
            apps_details[steam_appid] = app_details
            
        return apps_details
    
    def get_grid(self, steam_appid: int) -> (tuple[bytes, str] | None):
        grid_bytes = self._request_image_bytes(f"https://steamcdn-a.akamaihd.net/steam/apps/{steam_appid}/library_600x900_2x.jpg")
        grid = (grid_bytes, "jpg") if grid_bytes else None
        return grid
    
    def get_heroe(self, steam_appid: int) -> (tuple[bytes, str] | None):
        heroe_bytes = self._request_image_bytes(f"https://steamcdn-a.akamaihd.net/steam/apps/{steam_appid}/library_hero.jpg")
        heroe = (heroe_bytes, "jpg") if heroe_bytes else None
        return heroe
        

class SteamGridAPI(API):
    
    def __get_image_bytes_and_file_type_from_response(self, response: Response) -> (tuple[bytes, str] | None):
        response = response.json()
            
        if response["success"] and response["data"]:   
            an_image_url = choice(response["data"])["url"]
            image_bytes = self._request_image_bytes(an_image_url)
                
            if image_bytes:    
                file_type = an_image_url.split(".").pop()
                return image_bytes, file_type

    def get_grid(self, steam_appid: int) -> (tuple[bytes, str] | None):
        request = Request(f"https://www.steamgriddb.com/api/v2/grids/steam/{steam_appid}", {"dimensions": "600x900"}, {"Authorization": f"Bearer {self._api_key}"})
        response = self._make_tolerant_get_request(request)
        grid = self.__get_image_bytes_and_file_type_from_response(response) if response else None
        return grid
        
    
    def get_heroe(self, steam_appid: int) -> (tuple[bytes, str] | None):
        request = Request(f"https://www.steamgriddb.com/api/v2/heroes/steam/{steam_appid}", {"dimensions": "1920x620"}, {"Authorization": f"Bearer {self._api_key}"})
        response = self._make_tolerant_get_request(request)
        heroe = self.__get_image_bytes_and_file_type_from_response(response) if response else None
        return heroe