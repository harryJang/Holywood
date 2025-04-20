"""
This file includes tests for functions from backend.
"""

#ADD more files that need to be added!
import pytest
from search import search, search_by_keyword, search_by_tag

#ADD global variables that need to be added!

'''
search.py
'''
class TestSearch:
    def test_search_by_keywords(self):
        movie_info = search_by_keyword(["harry", "KATE", "fully functioning dinosaur"])
        assert movie_info[0][0] == "Harry Potter and the Deathly Hallows: Part 1"
        assert movie_info[0][1] == "https://m.media-amazon.com/images/M/MV5BMTgxZTI1MWMtYmFiOS00ZjAxLTk3Y2EtOWE5Y2E5NjFkZTVmXkEyXkFqcGdeQXVyNDI3NjU1NzQ@._V1_.jpg"
        assert movie_info[1][0] == "Titanic"
        assert movie_info[2][0] == "Jurassic World"
    
    def test_search_by_tags(self):
        movie_info = search_by_tag(["Action","Adventure","Animation"])
        assert movie_info[0][0] == "Harry Potter and the Deathly Hallows: Part 1"
        assert movie_info[0][1] == "https://m.media-amazon.com/images/M/MV5BMTgxZTI1MWMtYmFiOS00ZjAxLTk3Y2EtOWE5Y2E5NjFkZTVmXkEyXkFqcGdeQXVyNDI3NjU1NzQ@._V1_.jpg"
        assert movie_info[1][0] == "Avatar"
        assert movie_info[2][0] == "Jurassic World"
        assert movie_info[3][0] == "The Lord of the Rings: The Return of the King"
        assert movie_info[4][0] == "Skyfall"
    
    def test_search(self):
        json_ = '{"keyword":"harry potter kate fully functioning dinosaur SOMERANDOMWORD"}'
        movie_info = search(json_)
        assert movie_info[0][0] == "Harry Potter and the Deathly Hallows: Part 1"
        assert movie_info[0][1] == "https://m.media-amazon.com/images/M/MV5BMTgxZTI1MWMtYmFiOS00ZjAxLTk3Y2EtOWE5Y2E5NjFkZTVmXkEyXkFqcGdeQXVyNDI3NjU1NzQ@._V1_.jpg"
        assert movie_info[1][0] == "Titanic"
        assert movie_info[2][0] == "Jurassic World"

        json_ = '{"genre":"action, adventure, animation"}'
        movie_info = search(json_)
        assert movie_info[0][0] == "Harry Potter and the Deathly Hallows: Part 1"
        assert movie_info[0][1] == "https://m.media-amazon.com/images/M/MV5BMTgxZTI1MWMtYmFiOS00ZjAxLTk3Y2EtOWE5Y2E5NjFkZTVmXkEyXkFqcGdeQXVyNDI3NjU1NzQ@._V1_.jpg"
        assert movie_info[1][0] == "Avatar"
        assert movie_info[2][0] == "Jurassic World"
        assert movie_info[3][0] == "The Lord of the Rings: The Return of the King"
        assert movie_info[4][0] == "Skyfall"

"""
OOOO.py
"""
    

if __name__ == "__main__":
    pytest.main(['tests.py'])