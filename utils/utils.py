from requests import Session
from os import system
from sys import platform
from progress.bar import Bar
from colorama import Fore, Style
from bs4 import BeautifulSoup


ERROR_CURSOR = Fore.LIGHTRED_EX + "> "
COLOR_CURSOR = Fore.LIGHTMAGENTA_EX + "> "
CLEAR_CURSOR = Style.RESET_ALL

session = Session()
session.headers.update({     
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
})

def clear_con():
    if platform.startswith("win"):
        system("cls")
    else:
        system("clear")

def print_logo():
    print(Fore.YELLOW + \
"""       _       _    _____       
      | |     | |  / ____|      
      | |_   _| |_| (___  _   _ 
  _   | | | | | __|\___ \| | | |
 | |__| | |_| | |_ ____) | |_| |
  \____/ \__,_|\__|_____/ \__,_|
""")
    print(Fore.LIGHTGREEN_EX + "Вставьте ссылку на аниме или его название\n\nПример #1: " + Fore.WHITE + "https://jut.su/mirai-nikki/" + Fore.LIGHTGREEN_EX + "\nПример #2: "+ Fore.WHITE + "Дневник будущего")
    print(Fore.LIGHTBLACK_EX + "\nby " + Fore.LIGHTBLUE_EX + "@qweme32" + Fore.LIGHTBLACK_EX + " with " +  Fore.LIGHTRED_EX + "<3\n" + Style.RESET_ALL)

def new_download_bar(size: int, ep: int) -> Bar:
    max_value = int(size/8192) + 1
    mb_size = round(size/1024/1024, 1)
    return Bar(f"Скачивание (Эпизод: {ep})", max=max_value, suffix="%(percent)d%% (" + str(mb_size) + " MB)")

def exit_app(msg = None, code: int = 0) -> None:
    if msg:
        print(ERROR_CURSOR + msg + Style.RESET_ALL)

    exit(code)

def get_anime_page(text: str) -> BeautifulSoup:
    url = "https://jut.su/qweqweqweqwe"

    if "jut.su/" in text:
        url = text
    else:
        url = "https://jut.su/" + text

    req = session.get(url)

    if req.ok:
        soup = BeautifulSoup(req.text, 'html.parser')
        
        if soup.find("h1", class_="anime_padding_for_title"):
            return soup
        else:
            exit_app("Пожалуйста вставьте url на аниме, а не видео!")

    exit_app("По вашему запросу аниме не найдено!")

def parse_anime_page(soup: BeautifulSoup) -> dict:
    data = {}

    try:
        data["title"] = soup.find("meta", property="yandex_recommendations_title")["content"]
        data["tags"] = []
        data["seasons"] = {}
        data["films"] = {}
        data["url"] = soup.find("link", rel="canonical")["href"]

        for tag in soup.find_all("meta", property="yandex_recommendations_category"):
            data["tags"].append(tag["content"])

        all_anime_links = []
        sort_link_type = data["url"].replace("https://jut.su", "")

        for url in soup.find_all("a", class_="video"):
            if url["href"].startswith(sort_link_type):
                all_anime_links.append(url["href"])

        for anime_link in all_anime_links:
            if anime_link.split("/")[2].startswith("film-"):
                film = int(anime_link.split("/")[2].replace("film-", "").replace(".html", ""))
                data["films"][film] = anime_link

            elif anime_link.split("/")[2].startswith("season-"):
                ep = int(anime_link.split("/")[3].replace("episode-", "").replace(".html", ""))
                season = int(anime_link.split("/")[2].replace("season-", ""))

                anime_data = {
                    "url": "https://jut.su" + anime_link,
                    "ep": ep
                }

                if season in data["seasons"]:
                    data["seasons"][season].append(anime_data)
                else:
                    data["seasons"][season] = []
                    data["seasons"][season].append(anime_data)
            else:
                ep = int(anime_link.split("/")[2].replace("episode-", "").replace(".html", ""))
                season = 1
                
                anime_data = {
                    "url": "https://jut.su" + anime_link,
                    "ep": ep
                }

                if season in data["seasons"]:
                    data["seasons"][season].append(anime_data)
                else:
                    data["seasons"][season] = []
                    data["seasons"][season].append(anime_data)

    except Exception as e:
        exit_app(f"Parse error: {e.args}")

    return data

    