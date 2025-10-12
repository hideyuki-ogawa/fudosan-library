from __future__ import annotations

from typing import Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

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
    prefecture_code: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("prefectureCode", "prefecture_code", "prefCode"),
    )
    municipality_code: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("municipalityCode", "municipality_code", "id"),
    )
    municipality_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "municipalityName",
            "municipality_name",
            "name",
            "name_ja",
        ),
    )
    municipality_name_en: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "municipalityNameEn",
            "municipality_name_en",
            "name_en",
        ),
    )


class Prefecture(_BaseModel):
    code: str = Field(alias="code")
    name_ja: str = Field(alias="name_ja")
    name_en: str = Field(alias="name_en")
