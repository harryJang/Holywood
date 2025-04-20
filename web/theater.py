from serpapi import GoogleSearch

def search_theater(name, location):
    """
    A function that search the theaters around the given location and movie's name

    Params:
    name - movie's name
    location - the location of the user input and to be searched on Google.

    Returns:
    a SerpApi showtimes scrapped dictionary. If showtimes isn't found, empty list will
    be return.
    """
    #select_location = request.form['key']
    #select_location = "Sydney, Australia"
    params = {
    "q": f"showtime for {name}",
    "location": f"{location}",
    "hl": "en",
    "api_key": "9d131d60fde13e654d30791173c3e99e6a36001e08ffae80690110ed0ba5734e",
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    try:
        showtimes = results["showtimes"][0]["theaters"]
        return showtimes
    except Exception as e:
        showtimes = []
        return showtimes