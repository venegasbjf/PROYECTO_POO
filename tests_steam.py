import unittest
from steam import Steam

class SteamTestCase(unittest.TestCase):

    def setUp(self):
        self.steam = Steam()

    def test_is_steam_installed(self):
        result = self.steam.is_steam_installed()
        is_steam_installed = True  # Replace depending if you have steam installed or not
        self.assertIs(result["is_steam_installed"], is_steam_installed)

    def test_get_game_state_steam_deleted(self):
        result = self.steam.get_game_state("105600") # Replace with a game that is expected to meet the condition
        self.assertEqual(result, "Steam deleted")

    def test_get_game_state_not_installed(self):
        result = self.steam.get_game_state("105600") # Replace with a game that is expected to meet the condition
        self.assertEqual(result, "Not installed")

    def test_get_game_state_installed(self):
        result = self.steam.get_game_state("105600") # Replace with a game that is expected to meet the condition
        self.assertEqual(result, "Installed")

    def test_get_game_state_update_needed(self):
        result = self.steam.get_game_state("105600") # Replace with a game that is expected to meet the condition
        self.assertEqual(result, "Installed, need to update")

    def test_get_game_state_not_installed_updating(self):
        result = self.steam.get_game_state("105600") # Replace with a game that is expected to meet the condition
        self.assertEqual(result, "Not installed, updating")

    def test_find_windows_steam_path(self):
        result = self.steam._Steam__find_windows_steam_path()
        self.assertEqual(result, "")  # Replace with expected Windows path if known else leave it as ""
        
    def test_start_game(self):
        self.steam.play_game("105600") # Replace with a ID of any game that you have
        
    def test_delete_game(self):
        self.steam.delete_game("105600") # Replace with a ID of any game that you have

if __name__ == "__main__":
    unittest.main()
