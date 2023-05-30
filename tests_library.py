import unittest
from library import Library

class LibraryTestCase(unittest.TestCase):

    def setUp(self):
        self.library = Library(76561198941605330, "EA29ED634385FF016C0B0363F3F23D27", "da02ff927bc9816956aa864cf62ba4ba") # replace values to get data an images of the account

    def test_create_user_library_successfull(self):
        self.assertEqual(self.library.create_user_library()["response"], "success") # pass the test if everything goes well
        
    def test_create_user_library_account_info_error(self):
        self.assertEqual(self.library.create_user_library()["response"], "account information error") # passes the test if the account information is not obtained
        
    def test_create_user_library_account_games_error(self):
        self.assertEqual(self.library.create_user_library()["response"], "error games account") # pass the test if you don't get the games from the account

if __name__ == "__main__":
    unittest.main()