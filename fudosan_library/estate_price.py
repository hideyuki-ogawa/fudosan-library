from dataclasses import dataclass

from base import EstateLibraryBase
import pandas as pd


@dataclass
class EstatePriceData(EstateLibraryBase):
    """
    京都市北区のように、下の層がある場合、
    京都市で指定してもデータが取得できない。
    """

    def transaction_price(
        self, year: int, quater: int, pref_code: str, city_code: str
    ) -> pd.DataFrame:
        params = {"year": year, "quater": quater, "area": pref_code, "city": city_code}
        return self._request("XIT001?", params)

    def kante_hyoka(self, year: int, area: str, division: str):
        """
        必要パラメータ
        year: int
            YYYY
        area: str(2桁数値)
            都道府県コード NN
        division: str(2桁数値)
            00…住宅地
            03…宅地見込地
            05…商業地
            07…準工業地
            09…工業地
            10…調整区域内宅地
            13…現況林地
            20…林地（都道府県地価調査）
        """
        params = {"year": self.year, "area": self.pref_code, "division": self.division}
        return self._request("XCT001?", params)

    def transaction_point(
        self,
        z,
        x,
        y,
        from_,
        to_,
        response_format="geojson",
        priceClassification: str = None,
        landTypeCode: str = None,
    ):
        """
        Params:
            z: int zoomの値は11 - 15
            x: int
            y: int
            from_: YYYYN YYYY: 西暦、 N: 四半期 20053より指定可能
            to_: YYYYN YYYY: 西暦、 N: 四半期 20053より指定可能
            priceClassification: 価格情報区分コード : NN(数値２桁)
                01: 不動産取引価格情報のみ
                02: 成約価格情報のみ
                未指定: 両方
            landTypeCode: 土地区分コード : NN(数値２桁)
                01 … 宅地（土地）
                02 … 宅地（土地と建物）
                07 … 中古マンション等
                10 … 農地
                11 … 林地
                未指定 … すべて
                ※複数指定する場合は、「landTypeCode=01,02,07」のようにカンマ区切りで指定してください。
        """

        params = {
            "z": z,
            "x": x,
            "y": y,
            "from": from_,
            "to": to_,
            "priceClassification": priceClassification,
            "landTypeCode": landTypeCode,
            "response_format": response_format,
        }

        return self._geo_request("XPT001", params)

    def koji_chika(
        self,
        z,
        x,
        y,
        year,
        response_format="geojson",
        priceClassification: str = None,
        useCategoryCode: str = None,
    ):
        """
        Params:
            z: int zoomの値は13 - 15
            x: int
            y: int
            year: int
            priceClassification: 価格情報区分コード : N(数値1桁)
                0: 国土交通省地価公示のみ
                1: 都道府県地価調査のみ
                未指定: 両方
            useCategoryCode: 用途区分コード : NN(数値２桁)
                形式はNN（数字2桁）
                00 … 住宅地
                03 … 宅地見込地
                05 … 商業地
                07 … 準工業地
                09 … 工業地
                10 … 市街地調整区域内の現況宅地
                13 … 市街地調整区域内の現況林地（国土交通省地価公示のみ）
                20 … 林地（都道府県地価調査のみ）
                未指定 … すべて
                ※複数指定する場合は、「useCategoryCode=00,03,05」のようにカンマ区切りで指定してください。
        """
        params = {
            "z": z,
            "x": x,
            "y": y,
            "year": year,
            "priceClassification": priceClassification,
            "useCategoryCode": useCategoryCode,
            "response_format": response_format,
        }
        df = self._geo_request("XPT002", params)
        # df['current_price'] = df['u_current_years_price_ja'].map(lambda x: int(x.split('(')[0].replace(',', '')))
        # df['kenpe_ratio'] = df['u_regulations_building_coverage_ratio_ja'].map(lambda x: int(x.split('(')[0]))
        # df['yoseki_ratio'] = df['u_regulations_floor_area_ratio_ja'].map(lambda x: int(x.split('(')[0]))
        # df['year_on_year_change_rate'] = df['year_on_year_change_rate'].map(lambda x: float(x))
        return df

    def fudosan_kanteisho(self, year, area, division):
        """
        Params:
            year: int (YYYY 4桁)
            area: str 都道府県コード(NN 2桁数値)
            division: str(NN 2桁数値)
                00…住宅地
                03…宅地見込地
                05…商業地
                07…準工業地
                09…工業地
                10…調整区域内宅地
                13…現況林地
                20…林地（都道府県地価調査）
        """
        params = {"year": year, "area": area, "division": division}
        return self._request("XCT001?", params)


if __name__ == "__main__":

    import os
    import sys
    from area_data import PrefCode, CityCode

    secret_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "secret")
    )
    sys.path.append(secret_path)
    from secret import FUDOSAN_LIBRARY_API_KEY

    pref_code = PrefCode("京都").pref_code()
    city_code = CityCode(pref_code, "宇治市", FUDOSAN_LIBRARY_API_KEY).city_code()
    print(pref_code, city_code)

    year = 2023
    quater = 1 

    epd = EstatePriceData(FUDOSAN_LIBRARY_API_KEY)
    d = epd.transaction_price(year, quater, pref_code, city_code)
    print(d)

    from tile_utils import latlon, latlon_to_tile

    address = '京都市下京区玉津島町294'
    address_latlon = latlon(address)
    address_tile = latlon_to_tile(address_latlon[0], address_latlon[1], 13)
    print(address_latlon)
    print(address_tile)
    d2 = epd.koji_chika(address_tile[0], address_tile[1], address_tile[2], 2023)
    print(d2)
