import win32gui
import re
import requests
from bs4 import BeautifulSoup

def get_spotify_window_title():
    # Older versions of Spotify
    # The window class name is simply "SpotifyMainWindow"
    window_title = win32gui.GetWindowText(win32gui.FindWindow("SpotifyMainWindow", None))

    if window_title != "":
        return window_title

    # Newer versions of Spotify
    # The window class name is a generic "Chrome_WidgetWin_0" so I have to check if the window title looks like a song is playing
    # Format of window title: "Artist - Song"
    def winEnumHandler(hwnd, titles):
        if win32gui.IsWindowVisible(hwnd):
            if win32gui.GetClassName(hwnd) == "Chrome_WidgetWin_0" and re.match(".* - .*", win32gui.GetWindowText(hwnd)):
                titles.append(win32gui.GetWindowText(hwnd))

    titles = []
    win32gui.EnumWindows(winEnumHandler, titles)

    if len(titles) != 0:
        window_title = titles[0]
    
    if window_title == "":
        print("Spotify is not currently playing a song!")
        
    return window_title

def get_current_song_info():
    window_title = get_spotify_window_title()

    if window_title != "":
        split_title = window_title.split(" - ")

        return split_title # [artist, song_name]

def find_lyrics(artist, song_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + 'tuBG1HjEK2A4XvI9lItFPguQklA02Zi5xXeZxrquQe_uO_zcSEbHzhu7VPr0A6nc'}
    search_url = base_url + '/search'
    data = {'q': song_name + ' ' + artist}
    response = requests.get(search_url, data=data, headers=headers)

    json = response.json()

    remote_song_info = None

    for hit in json['response']['hits']:
        if artist.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    if remote_song_info:
        page = requests.get(remote_song_info['result']['url'])
        html = BeautifulSoup(page.text, 'html.parser')
        lyrics = html.find('div', class_='lyrics').get_text()

        return artist, song_name, remote_song_info['result']['url'], lyrics.strip()
    else:
        print('"' + artist + " - " + song_name + '" could not be found using the Genius API!')

def get_current_lyrics():
    current_song_info = get_current_song_info()

    if current_song_info:
        artist, song_name, url, current_song_lyrics = find_lyrics(current_song_info[0], current_song_info[1])

        if current_song_lyrics:
            print(artist + " - " + song_name)
            print(url + '\n')
            print(current_song_lyrics)

def main():
    get_current_lyrics()

if __name__ == "__main__":
    main()
