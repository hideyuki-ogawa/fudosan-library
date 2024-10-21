from dataclasses import dataclass

from base import EstateLibraryBase


@dataclass
class KokudoSuchi(EstateLibraryBase):

    def elementary_area(self, z, x, y, response_format="geojson"):
        """
        小学校区を取得するAPI


        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT004", params)

    def junior_high_area(self, z, x, y, response_format="geojson"):
        """
        中学校区を取得するAPI


        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT005", params)

    def gakko(self, z, x, y, response_format="geojson"):
        """
        学校のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT006", params)

    def kinder(self, z, x, y, response_format="geojson"):
        """
        幼児園・保育園のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT007", params)

    def iryo(self, z, x, y, response_format="geojson"):
        """
        医療機関のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT010", params)

    def fukushi(self, z, x, y, response_format="geojson"):
        """
        福祉施設のデータを取得するAPI

        z: int 13以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT011", params)

    def pop500m(self, z, x, y, response_format="geojson"):
        """
        将来推計人口500mメッシュを取得するAPI

        2020-2050年　５年おき

        z: int 11以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT013", params)

    def passanger(self, z, x, y, response_format="geojson"):
        """
        駅別乗降客数
        z: int 11以上
        """
        params = {"z": z, "x": x, "y": y, "response_format": response_format}
        return self._geo_request("XKT015", params)


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
