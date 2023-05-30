import unittest
import os
from databases import GamesDatabase

class TestGamesDatabase(unittest.TestCase):

    def setUp(self):
        self.games_database = GamesDatabase()

    def tearDown(self):
        # Clean up the database file after each test
        if os.path.exists(self.games_database._Database__database_path):
            os.remove(self.games_database._Database__database_path)

    def test_add_games_and_get_games(self):
        # Test adding games and retrieving them from the database
        games_data = {
            1: {
                "description": "Description 1",
                "developers": ["Developer 1", "Developer 2"],
                "publishers": ["Publisher 1", "Publisher 2"],
                "categories": ["Category 1", "Category 2"],
                "genres": ["Genre 1", "Genre 2"],
                "release_date": "2022-01-01",
                "name": "Game 1"
            },
            2: {
                "description": "Description 2",
                "developers": ["Developer 3", "Developer 4"],
                "publishers": ["Publisher 3", "Publisher 4"],
                "categories": ["Category 3", "Category 4"],
                "genres": ["Genre 3", "Genre 4"],
                "release_date": "2022-02-02",
                "name": "Game 2"
            }
        }

        # Add games to the database
        self.games_database.add_games(games_data)

        # Get games from the database
        retrieved_games = self.games_database.get_games(games_data.keys())

        self.assertEqual(retrieved_games, games_data)

# Run the tests
if __name__ == "__main__":
    unittest.main()
