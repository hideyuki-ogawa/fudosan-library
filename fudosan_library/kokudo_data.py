from dataclasses import dataclass

from base import EstateLibraryBase


@dataclass
class KokudoSuchi(EstateLibraryBase):

    def elementary_area(self, z, x, y, response_format="geojson"):
        """
        12. 小学校区を取得するAPI
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT004", params)

    def junior_high_area(self, z, x, y, response_format="geojson"):
        """
        13. 中学校区を取得するAPI
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT005", params)

    def gakko(self, z, x, y, response_format="geojson"):
        """
        14. 学校のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT006", params)

    def kinder(self, z, x, y, response_format="geojson"):
        """
        15. 幼児園・保育園のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT007", params)

    def iryo(self, z, x, y, response_format="geojson"):
        """
        16. 医療機関のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT010", params)

    def fukushi(self, z, x, y, response_format="geojson"):
        """
        17. 福祉施設のデータを取得するAPI
        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT011", params)

    def pop500m(self, z, x, y, response_format="geojson"):
        """
        18. 将来推計人口500mメッシュを取得するAPI

        2020-2050年　５年おき

        z: int 11以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT013", params)

    def train_passanger(self, z, x, y, response_format="geojson"):
        """
        20, 駅別乗降客数
        z: int 11以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT015", params)

    def saigai_kiken_area(self, z, x, y, administrativeAreaCode: str= None, response_format="geojson") -> gpd.GeoDataFrame:
        """
        21. 災害危険区域
        11 <= z <= 15 
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format, "adminstrativeAreaCode": administrativeAreaCode}
        return self._geo_request("XKT016?", params)
    
    def library_data(self, z, x, y, response_format="geojson", administrativeAreaCode: str=None) -> gpd.GeoDataFrame:
        """
        22. 図書館

        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format, "adminstrativeAreaCode": administrativeAreaCode}
        return self._geo_request("XKT017?", params)

    def yakuba_shukaisho(self, z, x, y, response_format="geojson") -> gpd.GeoDataFrame:
        """
        23. 市区町村村役場及び集会施設
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT018?", params)       

    def shizen_kouen(self, z, x, y, response_format="geojson", pref_code=None, city_code=None) -> gpd.GeoDataFrame:
        """
        24. 自然公園地域

        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format, "pref_code": pref_code, "city_code": city_code}
        return self._geo_request("XKT019?", params) 

    def moritsuchi_area(self, z, x, y, response_format="geojson") -> gpd.GeoDataFrame:
        """
        25. 大規模盛土造成地マップ
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format, "pref_code": pref_code, "city_code": city_code}
        return self._geo_request("XKT020?", params)         

    def jisuberi_area(self, z, x, y, response_format="geojson", pref_code=None, city_code=None) -> gpd.GeoDataFrame:
        """
        26. 地すべり防止地区
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format, "pref_code": pref_code, "city_code": city_code}
        return self._geo_request("XKT021?", params)         

    def kyusyamen_area(self, z, x, y, response_format="geojson", pref_code=None, city_code=None) -> gpd.GeoDataFrame:
        """
        26. 地すべり防止地区
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format, "pref_code": pref_code, "city_code": city_code}
        return self._geo_request("XKT022?", params)  


if __name__ == "__main__":
    import os
    import sys

    secret_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "secret")
    )
    sys.path.append(secret_path)
    from secret import FUDOSAN_LIBRARY_API_KEY

    from tile_utils import latlon, latlon_to_tile

    address = '京都市下京区玉津島町294'
    address_latlon = latlon(address)
    address_tile = latlon_to_tile(address_latlon[0], address_latlon[1], 13)
    print(address_latlon)
    print(address_tile)

    ks = KokudoSuchi(FUDOSAN_LIBRARY_API_KEY)
    passanger = ks.passanger(address_tile[0], address_tile[1], address_tile[2])
    print(type(passanger))
    print(passanger)

