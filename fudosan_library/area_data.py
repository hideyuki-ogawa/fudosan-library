import json
from dataclasses import dataclass
import os

import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
PREFCODE_JSON_PATH = os.path.join(current_dir, "data", "pref-code-jp.json")


@dataclass
class PrefCode:
    """
    都道府県コードを取得するクラス
    params:
        pref_name: str 都道府県名
    """

    pref_name: str

    def pref_code(self):
        with open(PREFCODE_JSON_PATH, "r", encoding="utf-8") as f:
            pref_code_json = json.load(f)
        for p_name, p_code in pref_code_json.items():
            if p_name.startswith(self.pref_name):
                return p_code
        raise Exception(f"No pref_code found for {self.pref_name}")


@dataclass
class CityCode:

    pref_code: str
    city_name: str
    api_key: str

    @property
    def headers(self):
        return {"Ocp-Apim-Subscription-Key": self.api_key}

    @property
    def params(self):
        return {"area": self.pref_code}

    def city_code(self):
        url = "https://www.reinfolib.mlit.go.jp/ex-api/external/XIT002"
        r = requests.get(url, headers=self.headers, params=self.params)
        if r.status_code == 200:
            for d in r.json().get("data", []):
                if d["name"].startswith(self.city_name):
                    return d["id"]
            raise Exception(f"No City Code found for {self.city_name}")


if __name__ == "__main__":
    import sys

    secret_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "secret")
    )
    sys.path.append(secret_path)
    from secret import FUDOSAN_LIBRARY_API_KEY

    pc = PrefCode("京都")
    print(pc.pref_code())
    kyoto_pref_code = pc.pref_code()
    cc = CityCode(kyoto_pref_code, "宇治", FUDOSAN_LIBRARY_API_KEY)
    c_code = cc.city_code()
    print(c_code)
