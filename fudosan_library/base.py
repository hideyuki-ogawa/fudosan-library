from dataclasses import dataclass

import geopandas as gpd
import requests
from shapely.geometry import box
import pandas as pd


@dataclass
class EstateLibraryBase:

    api_key: str
    base_url: str = "https://www.reinfolib.mlit.go.jp/ex-api/external"

    @property
    def headers(self):
        return {"Ocp-Apim-Subscription-Key": self.api_key}

    def _request(self, endpoint, params):
        url = f"{self.base_url}/{endpoint}?"
        r = requests.get(url, headers=self.headers, params=params)
        if r.status_code != 200:
            raise Exception(f"Request failed with status code {r.status_code}")
        return pd.DataFrame(r.json().get("data"))

    def _geo_request(self, endpoint, params):
        url = f"{self.base_url}/{endpoint}?"
        r = requests.get(url, headers=self.headers, params=params)
        if r.status_code != 200:
            raise Exception(f"Request failed with status code {r.status_code}")
        _crs = r.json()["crs"]["properties"]["name"]
        try:
            df = gpd.GeoDataFrame.from_features(r.json()["features"], crs=_crs)
            df = df.sort_index(axis=1)
            return df
        except Exception as e:
            print(e)
            pass

    @staticmethod
    def create_tile_gdf(self, z, x, y):
        """
        タイル座標からGeoDataFrameを作成する

        :param z: ズームレベル
        :param x: タイルのx座標
        :param y: タイルのy座標
        :return: GeoDataFrame
        """
        geometry = self.create_tile_geometry(x, y, z)
        gdf = gpd.GeoDataFrame({"geometry": [geometry]}, crs="EPSG:4326")
        gdf["tile_x"] = x
        gdf["tile_y"] = y
        gdf["zoom"] = z
        return gdf


if __name__ == "__main__":

    import os
    import sys
    from area_data import PrefCode, CityCode

    secret_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "secret")
    )
    sys.path.append(secret_path)
    from secret import FUDOSAN_LIBRARY_API_KEY

    end_point = "XIT001?"
    pref_code = PrefCode("京都").pref_code()
    city_code = CityCode(pref_code, "宇治市", FUDOSAN_LIBRARY_API_KEY).city_code()
    print(pref_code, city_code)
    year = 2023
    quater = 1
    params = {"year": year, "quater": quater, "area": pref_code, "city": city_code}
    elb = EstateLibraryBase(FUDOSAN_LIBRARY_API_KEY)
    d = elb._request(end_point, params)
    print(d)
