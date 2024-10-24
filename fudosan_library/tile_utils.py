import math
import geopandas as gpd
from shapely.geometry import box
import requests
import jageocoder as jac
from typing import Tuple



def latlon(address: str) -> list[float, float]:
    """
    日本語の住所サーチ用かな？

    Returns: list[float, float]

    """
    jac.init(url='https://jageocoder.info-proto.com/jsonrpc')

    try:
        res = jac.search(address)
        x = res['candidates'][0]['x']
        y = res['candidates'][0]['y']
        point = [x, y]
        return point
    except Exception as e:
        print(e)
        return None


def latlon_to_tile(zoom: int, lng: float, lat: float) -> Tuple[int, int, int]:
    """
    緯度、経度、ズームレベルからタイル座標を求める関数。

    Args:
        zoom (int): ズームレベル
        lat (float): 緯度
        lng (float): 経度
        
    Returns:
        tuple: zoom, タイルのx座標、y座標
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


def tile_to_latlon(x, y, z):
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
    address_tile = latlon_to_tile(10, address_latlon[0], address_latlon[1])

    print(address_latlon)
    print(address_tile)