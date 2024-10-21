import math
import geopandas as gpd
from shapely.geometry import box
import requests


def latlon_to_tile(lng, lat, zoom=11):
    """
    緯度、経度、ズームレベルからタイル座標を求める関数。

    Args:
        lat (float): 緯度
        lng (float): 経度
        zoom (int): ズームレベル

    Returns:
        tuple: タイルのx座標、y座標
    """
    n = 2.0**zoom
    x_tile = int((lng + 180.0) / 360.0 * n)
    y_tile = int(
        (
            1.0
            - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat)))
            / math.pi
        )
        / 2.0
        * n
    )

    return zoom, x_tile, y_tile


def latlon(address):
    url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    params = {
        "q": address,
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        coords = res.json()[0]["geometry"]["coordinates"]
        point = [coords[0], coords[1]]
        return point
    except requests.exceptions.HTTPError as e:
        print(e)


def tile_to_latlon(self, x, y, z):
    """
    タイル座標を緯度経度に変換する

    :param x: タイルのx座標
    :param y: タイルのy座標
    :param z: ズームレベル
    :return: (緯度, 経度)のタプル
    """
    n = 2.0**z
    lon_deg = x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


def create_tile_geometry(self, x, y, z):
    """
    タイル座標からジオメトリ（ポリゴン）を作成する

    :param x: タイルのx座標
    :param y: タイルのy座標
    :param z: ズームレベル
    :return: シェイプリーのPolygonオブジェクト
    """
    # タイルの四隅の座標を計算
    nw = self.tile_to_latlon(x, y, z)
    ne = self.tile_to_latlon(x + 1, y, z)
    se = self.tile_to_latlon(x + 1, y + 1, z)
    sw = self.tile_to_latlon(x, y + 1, z)

    # ポリゴンを作成
    return box(
        min(nw[1], sw[1]), min(sw[0], se[0]), max(ne[1], se[1]), max(nw[0], ne[0])
    )


if __name__ == "__main__":
    address = '京都市下京区玉津島町294'
    address_latlon = latlon(address)
    address_tile = latlon_to_tile(address_latlon[0], address_latlon[1])

    print(address_latlon)
    print(address_tile)