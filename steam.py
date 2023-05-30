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
        self.__steam_exe_path = os.path.join(self.__steam_path, "Steam.exe")
        self.__steam_apps_path = os.path.join(self.__steam_path, "steamapps")
    
    def play_game(self, game_id: str) -> None:
        subprocess.run(f"{self.__steam_exe_path} -applaunch {game_id}")
        
    def delete_game(self, game_id: str) -> None:
        subprocess.run(f"{self.__steam_exe_path}  +app_uninstall {game_id}")
        
    def is_steam_installed(self) -> dict[str, bool]:
        return {"is_steam_installed": os.path.exists(self.__steam_exe_path) and os.path.exists(self.__steam_apps_path)}
        
    def get_game_state(self, game_id: str) -> str:
        
        if not (os.path.exists(self.__steam_exe_path) and os.path.exists(self.__steam_apps_path)):
            return "Steam deleted"
        
        appmanifest_path = os.path.join(self.__steam_apps_path, f"appmanifest_{game_id}") + ".acf"
        
        if not os.path.exists(appmanifest_path):
            return "Not installed"
        
        state_flags = ""
        
        with open(appmanifest_path) as appmanifest_file:
            state_flags = list(appmanifest_file)[6].strip()[1]
            
        if state_flags == "4":
            return "Installed"
        
        if state_flags == "6":
            return "Installed, need to update"
        
        if state_flags == "1026":
            return "Not installed, updating"
        
        else:
            return "?"  
        
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
                logger.error("Se ha producido un error al buscar la ruta de steam en el registro de windows.")
            
        else:
            logger.info("Las funciones relacionadas con Steam sólo pueden utilizarse en un ordenador con Windows.")

        return steam_path