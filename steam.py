from __future__ import annotations

import os
import platform
import re
import winreg
import subprocess


class Steam:


    def __init__(self) -> None:
        self.steam_path = self.__find_windows_steam_path()
    
    
    def __find_windows_steam_path(self) -> str:
        """
        Retrieve the path to the Steam folder on a Windows machine using the Windows registry.
        """

        steam_path = ""

        if platform.system() == "Windows":

            steam_registry_key = r"Software\Valve\Steam"
            try:
                # Open the Steam registry key for the currently logged-in user
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, steam_registry_key) as key:
                    # Get the Steam install path from the Windows registry
                    steam_path = winreg.QueryValueEx(key, "SteamPath")[0]

            except OSError as e:
                print(f"Error reading Windows registry: {e}")

        return steam_path


    def is_steam_installed(self) -> bool:
        """
        Checks if Steam is installed on the system.
        """

        steam_executable_path  = os.path.join(self.steam_path, "steam.exe")

        is_installed = os.path.exists(steam_executable_path)

        if not is_installed:
            print(f"Steam.exe does not exist at {self.steam_path}")

        return is_installed
    
    def get_installed_games(self) -> list[str]:
        """
        Function to get the locally installed Steam app IDs on the system.
        """
        
        if not self.is_steam_installed():
            print("")
            return []

        installed_game_ids = []

        library_folders_file  = os.path.join(self.steam_installation.steam_path, "steamapps", "libraryfolders.vdf")

        try:
            with open(library_folders_file, "r") as f:
                # Flag to keep track of whether we are currently in the "apps" section
                in_apps = False

                for line in f:
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
        # If there was an error reading the file
        except OSError as e:
            # Log an error message
            print(f"Error reading file {library_folders_file}: {e}")
            
        return installed_game_ids

"""

class Library:

    def __init__(self) -> None:
        self.steam_path = "c:/program files (x86)/steam"
    
    def open_or_install_game_or_actualizar(self, game_id: str) -> None:

        Create the path to the Steam.exe file
        steam_exe = os.path.join(self.steam_path, "Steam.exe")

        Use the subprocess module to launch/install the Steam game
        subprocess.run(f"{steam_exe} -applaunch {game_id}")

    def prueba(self, game_id: str) -> None:
        
        steam_exe = os.path.join(self.steam_path, "Steam.exe")

        Use the subprocess module to launch/install the Steam game
        subprocess.run(f"app_info_print {game_id}", executable=steam_exe,)

libreria = Library()
libreria.prueba("1293820")

result = subprocess.run("app_status 1293820", stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="C:/Program Files (x86)/Steam/steam.exe")
output = result.stdout.decode('utf-8')
print(output)

"""