from .utils import *
import requests


class JutSuVideoSource:
    def __init__(self, title: str, ep: int, cdn_link: str) -> None:
        self.url, self.hash = cdn_link.split("?hash1=")
        self.title = title
        self.ep = ep

    def download(self, session: requests.Session, path: str) -> str:
        req = session.get(self.url, params={
                "hash1": self.hash
            }, 
            stream=True
        )

        if not req.ok:
            return "0"

        with open(path, 'wb') as f:
            size = int(req.headers.get('Content-Length'))

            bar = new_download_bar(size, self.ep)
            
            for chunk in req.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.next()
            
            bar.finish()
            f.close()

        return path  


class JutSuVideoPage:
    def __init__(self, ep: int, url: str) -> None:
        self.srcs = {}
        self.title = ""
        self.url = url
        self.ep = ep

    def fetch(self, session: requests.Session) -> bool:
        req = session.get(self.url)
        soup = BeautifulSoup(req.text, 'html.parser')

        videos = soup.find_all("source")

        if not videos:
            exit_app("К сожалению, в вашей стране это видео недоступно. Используйте VPN")

        title_obj = soup.find("div", class_="video_plate_title")
        if title_obj:
            title_name = title_obj.find("h2")

            if title_name:
                self.title = title_name.text

        for video in videos:
            self.srcs[video['res']] = JutSuVideoSource(self.title, self.ep, video['src'])

        return True


