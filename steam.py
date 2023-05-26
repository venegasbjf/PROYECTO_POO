from __future__ import annotations

import os
import platform
import re
import subprocess
import winreg

from logger import logger


class Steam:

    def __init__(self) -> None:
        self.__steam_path = self.__find_windows_steam_path()
    
    def play_game(self, game_id: int) -> None:
        steam_exe = os.path.join(self.__steam_path, "Steam.exe")
        subprocess.run(f"{steam_exe} -applaunch {game_id}")
        
    def steam_data(self) -> dict[str]:
        return {"steam_path": self.__is_steam_installed(), "installed_games": self.__get_installed_games()}
        
    def __is_steam_installed(self) -> bool:
        steam_executable_path  = os.path.join(self.__steam_path, "steam.exe")
        is_installed = os.path.exists(steam_executable_path)
        return is_installed
    
    def __get_installed_games(self) -> list[int]:
        installed_game_ids = []
        library_folders_file_path  = os.path.join(self.__steam_path, "steamapps", "libraryfolders.vdf")
        try:
            with open(library_folders_file_path) as library_folders_file:
                # Flag to keep track of whether we are currently in the "apps" section
                in_apps = False

                for line in library_folders_file:
                    # If we are in the "apps" section, search for app IDs in the file
                    if in_apps:
                        match = re.search(r"\d{1,10}", line)
                        if match:
                            app_id = match.group()
                            installed_game_ids.append(int(app_id))
                        # Continue to the next iteration without checking for the "apps" section
                        continue
                    
                    # Check if we have reached the "apps" section
                    if "\"apps\"" in line:
                        # Set the in_apps flag to True to indicate we are now in the "apps" section
                        in_apps = True
        except OSError:
            logger.info("Steam games could not be obtained")
            
        return installed_game_ids
        
    def __find_windows_steam_path(self) -> str:
        steam_path = ""
        if platform.system() == "Windows":
            steam_registry_key = r"Software\Valve\Steam"
            try:
                # Open the Steam registry key for the currently logged-in user
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, steam_registry_key) as key:
                    # Get the Steam install path from the Windows registry
                    steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
            except OSError as e:
                logger.error(repr(e))
        else:
            logger.info("Steam related functions can only be used on a Windows computer")

        return steam_path