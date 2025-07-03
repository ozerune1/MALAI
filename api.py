import os
from dotenv import load_dotenv, set_key
import requests
import json
from langchain_core.tools import tool

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

@tool
def refresh_ACCESS_TOKEN(a="None"):
    '''
    Refreshes the access token for MyAnimeList. Use this if you get a 401 error when using the API, then retry the previous API call. The Action Input should be the word None.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = "https://myanimelist.net/v1/oauth2/token"

    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    response = requests.post(api_url, data=params).json()

    set_key(".env", "ACCESS_TOKEN", response['access_token'])
    set_key(".env", "REFRESH_TOKEN", response['refresh_token'])

    return "Success!"

@tool
def search_anime(anime_name):
    '''
    Takes a string and searches MyAnimeList for the anime. 
    The result will be a JSON table of titles and IDs. 
    All titles will be in the original language (Japanese, Chinese, or Korean). anime_details's alternative_titles section might have other titles.
    Use this when you know the name of an anime but not the ID, or searching for an anime by name.
    If the search returns 'invalid q', try using simpler search terms to widen the search.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = "https://api.myanimelist.net/v2/anime"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "q": anime_name
    } 

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def anime_details(values):
    '''
    Provides details on the anime from MyAnimeList using an integer ID. PRIMARY AUTHENTICATED USER ONLY (@me)!!!: my_list_status field, if and only if it is on the user's list, contains watching status, individual score, episodes watched, if they're rewatching, and time updated. All values required. This field will only ever get you MY details, so never ever use it to find anyone else's information.
    Use search_anime to find this ID.
    There should be 2 inputs separated by a |. One is the id in numerical form. This is followed by a comma separated list of fields to return, without spaces between commas.
    Possible fields are: id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics
    '''

    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    id, fields = values.split('|')

    api_url = f"https://api.myanimelist.net/v2/anime/{id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "fields": fields
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def ranked_anime(values):
    '''
    Searches anime by ranking. There should be 3 inputs separated by a |.
    Number of results to return. Make this as small as possible to get the necessary information.
    Number to offset search by.
    One of the following fields:
    all, airing, upcoming, tv, ova, movie, special, bypopularity, favorite 

    Example: 1|4|all will get the 5th top anime series.
    '''

    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    limit, offset, field = values.split('|')

    api_url = f"https://api.myanimelist.net/v2/anime/ranking"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "ranking_type": field,
        "limit": limit,
        "offset": offset
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def seasonal_anime(values):
    '''
    Gets seasonal anime from MyAnimelist. Values should be given separated by a |. All values required.
    Year in integer form
    Season: winter, spring, summer, or fall
    Sort type: anime_score or anime_num_list_users
    Limit: integer representing the number of anime to return. Keep as low as possible.
    Offset: integer representing the number away from the top. 0 will be the top rated or top users.
    '''

    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    year, season, sort, limit, offset = values.split('|')

    api_url = f"https://api.myanimelist.net/v2/anime/season/{year}/{season}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "ranking_type": sort,
        "limit": limit,
        "offset": offset
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def get_user_anime_list(values):
    '''
    Gets a user's anime list from MyAnimelist, which includes information about what the user has seen. Does not include scores, but can be sorted by score. The top result by score should be considered the favorite. No need to verify scores. Do not use to look for individual entries. Values should be given separated by a |.
    Username: Use @me for the main user's list
    Status: all, watching, completed, on_hold, dropped, plan_to_watch
    Sort: list_score (descending), list_updated_at (descending), anime_title (ascending), anime_start_date (descending)
    Limit: Number of results to return. Keep this as low as possible.
    Offset: integer representing the number away from the top. 0 will be the top of the list.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    user, status, sort, limit, offset = values.split("|")
    if status == "all":
        status = None

    api_url = f"https://api.myanimelist.net/v2/users/{user}/animelist"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "status": status,
        "sort": sort,
        "limit": limit,
        "offset": offset
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def update_anime_list(values):
    '''
    Updates a user's anime list from MyAnimelist. Make sure the fields not asked to be updated remain the same. Current status can be found using the anime_details tool. Values should be given separated by a |. All values required.
    anime_id
    Status: watching, completed, on_hold, dropped, plan_to_watch
    is_rewatching: True, False
    score: integer 0-10
    num_watched_episodes: integer number of episodes completed.
    num_times_rewatched: integer number of times the entry has been rewatched
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    id, status, is_rewatching, score, num_watched_episodes, num_times_rewatched = values.split("|")

    api_url = f"https://api.myanimelist.net/v2/anime/{id}/my_list_status"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "status": status,
        "score": score,
        "is_rewatching": is_rewatching,
        "num_watched_episodes": num_watched_episodes,
        "num_times_rewatched": num_times_rewatched
    }

    return json.dumps(requests.put(api_url, headers=headers, data=params).json())

@tool
def delete_anime_from_list(id):
    '''
    Deletes an entry from the user's anime list. The only parameter is the anime id. The response will either be 200 or 404 indicating whether or not the item was on the list before deletion. 404 means it was never on the user's list.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = f"https://api.myanimelist.net/v2/anime/{id}/my_list_status"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "anime_id": id
    }

    return json.dumps(requests.delete(api_url, headers=headers, data=params).json())

@tool
def user_details(fields):
    '''
    Returns information about the user, as well as statistics such as counts of certain lists. The id should always be @me. It is not possible to get this information about other users.
    fields should be a comma separated list with no strings. Valid fields are: id, name, picture, gender, birthday, location, joined_at, anime_statistics, time_zone, is_supporter
    '''

    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = f"https://api.myanimelist.net/v2/users/@me"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "fields": fields
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def search_manga(manga_name):
    '''
    Takes a string and searches MyAnimeList for the manga. 
    The result will be a JSON table of titles and IDs. 
    All titles will be in the original language (Japanese, Chinese, or Korean). manga_details's alternative_titles section might have other titles.
    Use this when you know the name of a manga but not the ID, or searching for a manga by name.
    If the search returns 'invalid q', try using simpler search terms to widen the search.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = "https://api.myanimelist.net/v2/manga"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "q": manga_name
    } 

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def manga_details(values):
    '''
    Provides details on the manga from MyAnimeList using an integer ID. FOR THE AUTHENTICATED USER ONLY!!!!: my_list_status field, if and only if it is on the user's list, contains reading status, individual score, chapters read, if they're rereading, and time updated. This field will only ever get you MY details, so never ever use it to find anyone else's information.
    Use search_manga to find this ID.
    There should be 2 inputs separated by a |. One is the id in numerical form. This is followed by a comma separated list of fields to return, without spaces between commas.
    Possible fields are: id,title,main_picture,alternative_titles,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,genres,created_at,updated_at,media_type,status,genres,my_list_status,num_chapters,authors,pictures,background,related_anime,related_manga,related_manga,recommendations,serialization
    '''

    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    id, fields = values.split('|')

    api_url = f"https://api.myanimelist.net/v2/manga/{id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "fields": fields
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def ranked_manga(values):
    '''
    Searches manga by ranking. There should be 3 inputs separated by a |.
    Number of results to return. Make this as small as possible to get the necessary information.
    Number to offset search by.
    One of the following fields:
    all, manga, novels, oneshots, doujin, manhwa, manhua, bypopularity, favorite

    Example: 1|4|all will get the 5th top manga.
    '''

    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    limit, offset, field = values.split('|')

    api_url = f"https://api.myanimelist.net/v2/manga/ranking"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "ranking_type": field,
        "limit": limit,
        "offset": offset
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def get_user_manga_list(values):
    '''
    Gets a user's manga list from MyAnimelist, which includes information about what the user has read. Does not include scores, but can be sorted by score. The top result by score should be considered the favorite. You do not need to verify. Do not use to look for individual entries. Values should be given separated by a |. All values required. IT IS ABSOLUTELY IMPOSSIBLE TO FIND THE SCORES OF SPECIFIC USERS BY USERNAME!! NEVER UNDER ANY CIRCUMSTANCES SHOULD YOU TRY AND FIND THEM.
    Username: Use @me for the main user's list
    Status: all, reading, completed, on_hold, dropped, plan_to_read
    Sort: list_score (descending), list_updated_at (descending), manga_title (ascending), manga_start_date (descending)
    Limit: Number of results to return. Keep this as low as possible.
    Offset: integer representing the number away from the top. 0 will be the top of the list.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    user, status, sort, limit, offset = values.split("|")
    if status == "all":
        status = None

    api_url = f"https://api.myanimelist.net/v2/users/{user}/mangalist"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "status": status,
        "sort": sort,
        "limit": limit,
        "offset": offset
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def update_manga_list(values):
    '''
    Updates a user's manga list from MyAnimelist. Make sure the fields not asked to be updated remain the same. Current status can be found using the manga_details tool. Values should be given separated by a |. All values required.
    manga_id
    Status: reading, completed, on_hold, dropped, plan_to_read
    is_rereading: True, False
    score: integer 0-10
    num_volumes_read: integer number of volumes completed.
    num_chapters_read: integer number of chapters read.
    num_times_reread: integer number of times the entry has been reread
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    id, status, is_rereading, score, num_volumes_read, num_chapters_read, num_times_reread = values.split("|")

    api_url = f"https://api.myanimelist.net/v2/manga/{id}/my_list_status"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "status": status,
        "score": score,
        "is_rereading": is_rereading,
        "num_volumes_read": num_volumes_read,
        "num_chapters_read": num_chapters_read,
        "num_times_reread": num_times_reread
    }

    return json.dumps(requests.put(api_url, headers=headers, data=params).json())

@tool
def delete_manga_from_list(id):
    '''
    Deletes an entry from the user's manga list. The only parameter is the manga id. The response will either be 200 or 404 indicating whether or not the item was on the list before deletion. 404 means it was never on the user's list.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = f"https://api.myanimelist.net/v2/manga/{id}/my_list_status"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "manga_id": id
    }

    return json.dumps(requests.delete(api_url, headers=headers, data=params).json())

@tool
def get_forum_boards(values):
    '''
    Gets the available forum boards and subboards from MyAnimeList. Action Input should be None.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = f"https://api.myanimelist.net/v2/forum/boards"

    values = None

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    return json.dumps(requests.get(api_url, headers=headers).json())

@tool
def get_forum_topics(values):
    '''
    Gets the topics within a forum board and/or subboard. All values are required and should be separated by a |.
    board_id: Optional, recommended. acquired from get_forum_boards. None if none.
    subboard_id: Optional, recommended if available. None if none.
    query: Optional, recommended search query. None if none.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = f"https://api.myanimelist.net/v2/forum/topics"

    board_id, subboard_id, q = values.split('|')

    if board_id == "None":
        board_id = None
    if subboard_id == "None":
        subboard_id = None
    if q == "None":
        q = None

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "board_id": board_id,
        "subboard_id": subboard_id,
        "q": q,
        "limit": 10
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())

@tool
def read_forum_topic(id):
    '''
    Reads the forum topic from the given topic id, acquired from get_forum_topics.
    '''
    load_dotenv(override=True)

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    api_url = f"https://api.myanimelist.net/v2/forum/topic/{id}"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "limit": 10
    }

    return json.dumps(requests.get(api_url, headers=headers, params=params).json())