import json
import os
import requests
from datetime import datetime


class ObjectConverter:
    def __init__(self, **kwargs):
        self.json = kwargs
        for i in self.json.keys():
            setattr(self, i, self.json[i])

    @classmethod
    def convert_obj(cls, obj):
        x = json.loads(obj)
        return cls(**x)

    def __repr__(self):
        return f"{self.json}"


class ShowroomAPI:
    def __init__(self):
        self.url = "https://www.showroom-live.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        }
        self.converter = ObjectConverter()

    def check_live(self, r_id: int = None):
        fetch_api = requests.get(
            f"{self.url}/api/live/live_info?room_id={r_id}", headers=self.headers
        )
        content = fetch_api.json()
        if content.get("live_status") == 2:
            return True
        return False

    def fetch_api(self, r_id: int = None):
        fetch_api = requests.get(
            url=f"{self.url}/api/live/streaming_url?room_id={r_id}&abr_available=1",
            headers=self.headers,
        )
        return fetch_api.json()

    def fetch_room(self, r_id: int = None):
        fetch_api = requests.get(
            url=f"{self.url}/api/live/live_info?room_id={r_id}",
            headers=self.headers,
        )
        return fetch_api.json()

    def get_streaming_url(self, r_id: int = None):
        json_content = self.converter.convert_obj(
            json.dumps(self.fetch_api(r_id=r_id))
        ).streaming_url_list[1]
        return json_content["url"]


class ShowroomClient:
    def __init__(self):
        self.api = ShowroomAPI()
        self.timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    def record_live(self, room_id: int = None):
        room = self.api.fetch_room(r_id=room_id)
        check = self.api.check_live(r_id=room_id)

        if check is True:
            url_stream = self.api.get_streaming_url(r_id=room_id)
            open("showroom.bat", "w").close()
            open("target.txt", "w").close()
            open("target.txt", "a").write(str(room_id))
            open("showroom.bat", "a").write(
                f'@echo off \ntitle Showroom - StawaDev. \ncolor 0a \nsetlocal \n:PROMPT \necho [ {self.timestamp} ] - Now Recording. \nffmpeg -loglevel "quiet" -i "{url_stream}" -filter_complex scale=1280:720 -map 0:a -c:a copy -bsf:a aac_adtstoasc "Live-{room["room_id"]}.mp4" \necho Press Q to continue... \nchoice /c q /n /m "Quit? :" \nif %errorlevel%==1 goto Finished \n:Finished \necho [ {self.timestamp} ] - Finished Recording. \npause'
            )
            os.system("showroom.bat")
            return {"status": "success", "File": f"Live-{room['room_id']}.mp4"}

        return {
            "status": "failed",
            "message": f"{room['room_name']} is not currently live",
        }
