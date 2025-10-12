from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .types import PriceClassification


class _BaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class TradeRecord(_BaseModel):
    trade_price: Optional[int] = Field(alias="TradePrice", default=None)
    municipality_code: Optional[str] = Field(alias="MunicipalityCode", default=None)
    prefecture_ja: Optional[str] = Field(alias="Prefecture_ja", default=None)
    area: Optional[float] = Field(alias="Area", default=None)
    price_classification: Optional[PriceClassification] = Field(
        alias="PriceClassification", default=None
    )


class Municipality(_BaseModel):
    prefecture_code: Optional[str] = Field(alias="prefectureCode", default=None)
    municipality_code: Optional[str] = Field(alias="municipalityCode", default=None)
    municipality_name: Optional[str] = Field(alias="municipalityName", default=None)


class Prefecture(_BaseModel):
    code: str = Field(alias="code")
    name_ja: str = Field(alias="name_ja")
    name_en: str = Field(alias="name_en")
