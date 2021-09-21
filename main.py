from typing import List, Union
from requests.sessions import Session
import re
import time


class LoLInviteCodeBot:
    """
    台版英雄聯盟2021年8/8周年慶活動
    全自動試LoL邀請碼
    """

    def __init__(self, lol_tokens: Union[str, list], source_urls: Union[str, list]):
        """
        Args:
            lol_tokens (Union[str, list]): 網頁token, 可在遊戲路徑內`./Game/Logs/LeagueClient Logs/YYYY-MM-DDTHH-mm-dd_xxxxx_LeagueClientUxHelper-renderer.log`中找到, 應為64字英數
            source_urls (Union[str, list]): 要抓取的網頁URL, 會自動從網頁內抓取符合`LOL\w{10}`之值
        """
        self.source_urls = source_urls
        self.used = []

        if isinstance(lol_tokens, str):
            self.lol_sessions: List[Session] = [self.create_session(lol_tokens)]
        else:
            self.lol_sessions: List[Session] = [self.create_session(token) for token in lol_tokens]

        self.session = Session()
        self.session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"

    def create_session(token: str):
        session = Session()
        session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) LeagueOfLegendsClient/11.15.388.2387 (CEF 74) Safari/537.36"
        session.headers["token"] = token
        return session

    def fetch_codes(self):
        codes = []
        for source in self.source_urls:
            resp = self.session.get(source)

            source_codes = re.findall(r"LOL\w{10}", resp.text)
            codes += source_codes

        print(f"Got {len(codes)} codes")
        return codes

    def use_code(self, code: str):
        print("Trying:", code)
        for session in self.lol_sessions:
            resp = session.post(
                "https://bargain.lol.garena.tw/api/enter",
                json={"code": code, "confirm": True},
            )
            data = resp.json()
            print(data)

            if data.get("enter_code_amount") == 60 or data.get("error") == "ERROR__ENTER_CODE_AMOUNT_OUT_OF_QUOTA":
                self.lol_sessions.remove(session)

        time.sleep(0.5)

    def run(self, fetch_delay: int = 5):
        """
        開始執行

        Args:
            fetch_delay (int, optional): 抓取網頁間隔(秒), 預設為5.
        """
        while True:
            codes = self.fetch_codes()
            for code in codes:
                if code in self.used:
                    continue

                self.use_code(code)
                self.used.append(code)

            time.sleep(fetch_delay)


if __name__ == "__main__":
    lol = LoLInviteCodeBot(
        lol_tokens=[""],
        source_urls=["https://forum.gamer.com.tw/C.php?bsn=17532&snA=674866&last=1"],
    )
    lol.run()