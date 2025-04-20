"""
This file has been written by Yunseok Jang z5286005 since 7 / 3 / 2023.
"""

import sys
import json
import mysql.connector
from web.mysql_util import get_pw

def search(json_) -> list[str]:
    """
    Search movies by keywords or genres

    Parameters
    json_ (json): 
    key->either keyword or genre
    content->if keyword, could be any words that might be movie name, description, casts or director
           ->if genre, could be multiple genres

    Returns
    list of movies info: Basic information of the movies that matches to the keyword or genre.
    """
    key, input = json_to_string(json_)
    if key == "keyword":
        return search_by_keyword(input)
    elif key == "genre":
        return search_by_tag(input)
    else:
        print('you need to pass in CORRECT KEY name which are keyword and genre.', file=sys.stderr)

def search_by_keyword(keywords:list[str]) -> list[str]:
    """
    Search movies by keywords

    Parameters
    keywords(list[str]): list of keywords
    
    Returns
    list of movies info: Basic information of the movies that matches to the keywords.
    """
    query = get_query("keyword", None)                      
    movie_ids = get_movie_id_for_keywords(query, keywords)  
    arg = [str(id) for id in movie_ids]                     
    if len(arg) == 0:
        print("There is no matching movie !")
        return None
    query = get_query("movie", arg)                         
    movie_info = get_data(query, arg, 1)                       
    return movie_info

def search_by_tag(tags:list[str]) -> list[str]:
    """
    Search movies by genres

    Parameters
    tags(list[str]: list of genres
    
    Returns
    list of movies info: Basic information of the movies that matches to the genres.
    """
    query = get_query("genre", tags)                       
    tags_id = convert_tags_to_list_of_ids(tags)            
    movie_id = get_data(query, tags_id, 0)                 
    movie_id.sort(key=lambda a: a[1], reverse = True)      
    arg = [str(id[0]) for id in movie_id]                  
    if len(arg) == 0:
        print("There is no matching movie !")
        return None
    query = get_query("movie", arg)                        
    movie_info = get_data(query, arg, 1)                   
    return movie_info

def get_data(qry:str, arg:list[str], tag:int) -> any:
    """
    Connects to the database and execute the given query

    Parameters
    qry(str): query in string type
    arg(list[str]): list of keywords or genres in string type
    tag(int): 0 gets the genres matches, 1 gets the keywords matches
    
    Returns
    Fetched data from database of given query
    """
    connection = mysql.connector.connect(host = 'localhost',
                                         database = 'holywood',
                                         user = 'root',
                                         password = get_pw())
    if tag == 0:
        cursor = connection.cursor()
    if tag == 1:
        cursor = connection.cursor(dictionary=True)
    cursor.execute(qry, arg)
    return cursor.fetchall()

def get_query(key:str, bags:list[str]):
    """
    Gets the appropriate query

    Parameters
    key(str): either "keyword" or "genre" or "movie"
    bags(list[str]): list of arguments 
    
    Returns
    query
    """
    query = ""
    if key == "genre":
        query = "SELECT movie_id, count(genre_id)\
                FROM Genres_of_Movies\
                WHERE genre_id = %s"
        for i in range(len(bags)-1):
            query += " OR genre_id = %s"
        query += "GROUP BY movie_id;"
    elif key == "keyword":
        query = "SELECT id\
                FROM Movies\
                WHERE LOWER(name) like %s \
                OR LOWER(description) like %s \
                OR LOWER(director) like %s\
                OR LOWER(casts) like %s;"
    elif key == "movie":
        query = "SELECT *\
                FROM Movies\
                WHERE id = %s"
        for i in range(len(bags)-1):
            query += " OR id = %s"
        query += ";"
    return query

def get_movie_id_for_keywords(query:str, keywords:list[str]) -> set():
    """
    Gets the movies id that contains the keywords

    Parameters
    query(str): query to fetch the data
    keywords(list[str]): list of keywords
    
    Returns
    set of movies id that contains the keywords
    """
    movie_ids = set()
    for keyword in keywords:        
        list_of_ids = \
            get_data(query, ['%'+keyword.lower()+'%']*4, 0)
        for id in list_of_ids:
            movie_ids.add(id[0])    
    return movie_ids

def json_to_string(json_) -> tuple([str, list[str]]):
    """
    Change the keywords and genres from json format to list of string

    Parameters
    json_ (json): 
    key->either keyword or genre
    content->if keyword, could be any words that might be movie name, description, casts or director
           ->if genre, could be multiple genres
    
    Returns
    tuple of key and the content. key is either "keyword" or "genre". content is list of either keywords or genres.
    """
    input = json.loads(json_)
    if "genre" in input.keys():
        genre = input["genre"].split(", ")
        return "genre", genre
    else:
        keyword = input["keyword"].split(" ")
        return "keyword", keyword

def convert_tags_to_list_of_ids(tags:list[str]) -> list[int]:
    """
    Changes genres(in string) to genres id(in int)

    Parameters
    tags: list of genres
    
    Returns
    list of genres id
    """
    tags_id = []
    for tag in tags:
        tags_id.append(str(genre_in_id(tag)))
    return tags_id
    
def genre_in_id(genre:str) -> int:
    """
    Maps genre to id

    Parameters
    genre: genre
    
    Returns
    genre id
    """
    if genre.lower() == "action":
        return 1
    elif genre.lower() == "adventure":
        return 2
    elif genre.lower() == "comedy":
        return 3 
    elif genre.lower() == "drama":
        return 4 
    elif genre.lower() == "science Fiction":
        return 5 
    elif genre.lower() == "animation":
        return 6 
    elif genre.lower() == "fantasy":
        return 7 
    elif genre.lower() == "horror":
        return 8 
    elif genre.lower() == "romance":
        return 9 
    elif genre.lower() == "thriller":
        return 10 
    elif genre.lower() == "crime":
        return 11
    elif genre.lower() == "mystery":
        return 12