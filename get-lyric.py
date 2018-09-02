import sys
import dbus
import requests
from bs4 import BeautifulSoup

from genius_api_token import (
    GENIUS_API_TOKEN
)

API_TOKEN = GENIUS_API_TOKEN
BASE_URL = 'https://api.genius.com'
SEARCH_FAIL_MSG = 'The lyrics for this song were not found!'
WRONG_INPUT_MSG = 'Wrong number of arguments. Use two parameters to perform a custom search or none to get the song currently playing on Spotify.'


def request_song_info(song_title, artist_name):
    search_url = BASE_URL + '/search'
    data = {'q': song_title + ' ' + artist_name}
    headers = {'Authorization': 'Bearer ' + API_TOKEN}

    response = requests.get(search_url, data=data, headers=headers)

    return response

def request_songs_by_artist(artist_name):
    #TODO retrieve artist id instead of using the general search
    search_url = BASE_URL + '/search'
    data = {'q': artist_name}
    headers = {'Authorization': 'Bearer ' + API_TOKEN}

    response = requests.get(search_url, data=data, headers=headers)

    return response

def scrap_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    [h.extract() for h in html('script')]
    lyrics = html.find('div', class_='lyrics').get_text()

    return lyrics


def main():
    args_length = len(sys.argv)
    if args_length == 2:
        # TODO search for all lyrics of artist
        song_info = sys.argv
        artist_name = song_info[1]
        print('Artist: {}'.format(artist_name))
    elif args_length == 3:
        # Use input as song title and artist name
        # TODO validation
        song_info = sys.argv
        song_title, artist_name = song_info[1], song_info[2]
        print('Song {} by Artist: {}'.format(song_title, artist_name))
    else:
        print(WRONG_INPUT_MSG)
        return

    # Search for matches in request response
    response = request_song_info(song_title, artist_name)
    response_json = response.json()
    remote_song_info = None

    for hit in response_json['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    # Extract lyrics from URL if song was found
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        lyrics = scrap_song_url(song_url)

        write_lyrics_to_file(lyrics, song_title, artist_name)

        print(lyrics)
    else:
        print(SEARCH_FAIL_MSG)


def write_lyrics_to_file(lyrics, song, artist):
    file = open('lyric-view.txt', 'w')
    file.write('{} by {}'.format(song, artist))
    file.write(lyrics)
    file.close()


if __name__ == '__main__':
    main()
