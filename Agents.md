# Agents.md (fudosan-library 最新仕様 + uv対応 + API仕様書参照)

## 🧭 目的

このエージェントは、**国土交通省 不動産情報ライブラリAPI** をPythonで利用するためのSDK **「fudosan-library」** を開発する。
HTTP通信、厳密な型、GeoJSON処理、エラーハンドリング、再試行ロジックを備えた**堅牢でテスト駆動なライブラリ**を構築することを目的とする。

---

## 📘 外部仕様書

* 不動産情報APIの公式仕様書は `../info/fudosan-lib.md` に格納されている。
  CodexエージェントはこのPDFを参照してAPIパラメータ・レスポンス構造を正確に取得すること。

---

## 🧑‍💻 開発哲学

### 1. テスト駆動開発（TDD）を中核とする

* 全ての機能は **テストが先**。`Red → Green → Refactor` サイクルを厳守する。
* 実装は必ず失敗するテストを作ってから始める。
* テストがグリーンでないコードはマージ禁止。
* 例外系・再試行・Geo変換など副作用を伴う処理はすべてユニットテストで保証する。
* CI で `pytest` + `mypy --strict` がグリーンでなければビルドは失敗。

### 2. 型安全と契約

* 全ての関数・戻り値に型注釈を付与。`mypy --strict` 準拠。
* APIレスポンスは `TypedDict` で受け、アプリ内部は `pydantic` モデルに変換。
* コード値（例: `priceClassification`）は `Literal` / `Enum` で制約。
* HTTP層は `Protocol` 抽象を介してテスト容易性を確保。

### 3. 単一責務・拡張性

* HTTPクライアント、モデル、Geo変換、CLI、ログを明確に分離。
* Geo依存は `fudosan-library[geo]` オプションとし、軽量コアを維持。

---

## 📦 プロジェクト概要

| 項目          | 内容                                                         |
| ----------- | ---------------------------------------------------------- |
| パッケージ名      | `fudosan-library`                                          |
| Pythonバージョン | 3.10以上                                                     |
| テスト         | `pytest`, `respx`, `pytest-recording`                      |
| 型検査         | `mypy --strict`                                            |
| 静的解析        | `ruff`                                                     |
| 依存          | `httpx`, `pydantic`                                        |
| オプション       | `geopandas`, `pyogrio`, `pyproj`, `mapclassify`, `shapely` |
| 出力形式        | JSON / GeoJSON / GeoDataFrame                              |

---

## 🧱 モジュール構成

```
src/fudosan_library/
├── __init__.py
├── client.py        # HTTPクライアント本体
├── endpoints.py     # APIエンドポイント定義
├── exceptions.py    # カスタム例外
├── types.py         # Literal, TypedDict, Protocol
├── models.py        # Pydantic モデル
└── geo.py           # GeoPandas 連携ユーティリティ
```

---

## ⚙️ 機能仕様

### 認証

* ヘッダ: `Ocp-Apim-Subscription-Key`
* 初期化時に `FudosanClient(api_key="...")`

### 主要エンドポイント

| コード      | 名称          | 内容      | 形式                |
| -------- | ----------- | ------- | ----------------- |
| `XIT001` | 不動産価格情報     | JSON    | 配列                |
| `XIT002` | 市区町村一覧      | JSON    | オブジェクト            |
| `XPT001` | 取引ポイント      | GeoJSON | FeatureCollection |
| `XPT002` | 地価公示・調査ポイント | GeoJSON | FeatureCollection |
| `XKT002` | 用途地域        | GeoJSON | FeatureCollection |

---

## 📜 型仕様

```python
PriceClassification = Literal["01", "02"]  # 01=取引, 02=成約

class FeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    features: List[Feature]

class TradeRecord(BaseModel):
    TradePrice: Optional[int]
    MunicipalityCode: Optional[str]
    Prefecture_ja: Optional[str]
    Area: Optional[float]
```

---

## 💥 例外ポリシー

| HTTPコード | 例外                      | 再試行          |
| ------- | ----------------------- | ------------ |
| 400     | BadRequestError         | ✖            |
| 401     | AuthError               | ✖            |
| 404     | NotFoundError           | ✖            |
| 429     | ServerError(rate limit) | ⚪（指数＋Jitter） |
| 5xx     | ServerError             | ⚪            |

---

## 🌍 Geoモジュール仕様

```python
def geojson_to_gdf(geojson: FeatureCollection | str, *, crs: Optional[str] = None) -> geopandas.GeoDataFrame
```

* GeoJSON→GeoDataFrame 変換。
* CRSは既定で `EPSG:4326`。
* `pip install fudosan-library[geo]` 未導入時はエラーをraise。

---

## 🧪 テスト駆動開発（TDD）方針

### テスト原則

* 実装は常にテスト駆動。テストコードを先に書き、成功で完了とみなす。
* テスト名は行動仕様（Bddスタイル）に近い自然言語で表現。
* API呼び出し・例外・再試行・Geo変換を単体でカバー。

### カバレッジ目標

| 種別          | カバレッジ | 検証観点                |
| ----------- | ----- | ------------------- |
| Unit        | 100%  | 型・値・例外・再試行          |
| Integration | 90%   | 実APIモック             |
| Geo         | 90%   | CRS/GeoDataFrame 変換 |
| 全体          | ≥95%  | CIで強制               |

### テスト構成

```
tests/
├── test_client_contract_xit001.py
├── test_client_contract_xpt001.py
├── test_retries_rate_limit.py
└── test_geo_conversion.py
```

---

## 🔬 環境構築

### 🧰 uvによる開発環境セットアップ

`uv` は高速で依存を解決するPythonパッケージマネージャ。pipよりも軽量・確実に環境を再現できる。

```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 新規仮想環境作成
uv venv

# アクティベート
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# 依存導入（開発込み）
uv pip install -e .[dev,geo]

# テスト実行
uv run pytest -q
```

### 💻 Makefile (ショートカット)

```makefile
.PHONY: format lint type test cov build clean

format:
	ruff format
lint:
	ruff check
type:
	mypy --strict src tests
test:
	pytest -q
cov:
	pytest --cov=fudosan_library --cov-fail-under=95
build:
	uv build
clean:
	rm -rf .pytest_cache .mypy_cache dist build *.egg-info
```

---

## 🧬 CI/CD 構成

### GitHub Actions

* PR / main push で `ruff`, `mypy --strict`, `pytest --cov` 自動実行。
* `v*` タグ push 時に `uv build` → `GitHub Release` → `PyPI` 公開。

### CI ワークフロー (ci.yml)

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [ main ]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install deps
        run: |
          uv pip install -e .[dev]
      - name: Lint
        run: ruff check
      - name: Type check
        run: mypy --strict src tests
      - name: Test
        run: pytest --cov=fudosan_library --cov-fail-under=95
```

---

## ✅ Definition of Done

* [ ] すべての関数がTDDに基づいて実装済み
* [ ] `mypy --strict` 警告ゼロ
* [ ] `pytest` 全通過、カバレッジ95%以上
* [ ] `README.md` に使用例（価格・取引ポイント・用途地域）
* [ ] `uv run` によるローカル実行が成功
* [ ] GeoPandas連携 (`fudosan-library[geo]`) 確認済み
* [ ] API仕様書 (`../info/houjin-bango-pdf.pdf`) 準拠確認済み

---

## 🧠 Codexエージェントの行動規範

| フェーズ                 | Codexの目的   | 成果物                |
| -------------------- | ---------- | ------------------ |
| 1. Test First        | 失敗するテスト作成  | tests/ 各ファイル       |
| 2. Implement to Pass | テストを通す最小実装 | client.py / geo.py |
| 3. Refactor          | 重複排除・型最適化  | ✅ mypy strict      |
| 4. Validate          | CI/CD 全通過  | ✅ pytest green     |
| 5. Document          | README更新   | Quick Start 追記     |

---

## 🧩 今後の拡張

* 非同期クライアント (`AsyncFudosanClient`)
* PBF(Mapbox Vector Tile)対応
* キャッシュ層 (`httpx-cache`)
* CLI (`typer`) ベース
* Notebook デモ (`examples/notebooks/demo.ipynb`)

---

