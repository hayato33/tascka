"""アプリケーション設定モジュール。

pydantic-settingsを使って環境変数からアプリケーションの設定を読み込む。
pydantic-settingsは、Pydanticのバリデーション機能を活用して、
環境変数を型安全に読み込むためのライブラリ。

なぜpydantic-settingsを使うのか:
- 環境変数を直接 os.getenv() で読むと、型が常にstrになり型安全でない
- デフォルト値の管理やバリデーションを自前で書く必要がある
- pydantic-settingsなら、クラス定義するだけで自動的に環境変数を読み込み、
  型変換・バリデーション・デフォルト値設定をすべてやってくれる
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定。

    model_config の env_file で .env ファイルのパスを指定すると、
    環境変数が未設定の場合に .env ファイルからフォールバックで読み込む。
    環境変数 > .env ファイル の優先順位になる。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # extra="ignore" にすると、定義していない環境変数があってもエラーにならない
        extra="ignore",
    )

    # DATABASE_URL 環境変数から読み込む。
    # asyncpgドライバを使うため、URLは "postgresql+asyncpg://..." の形式にする。
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/taskdb"

    # SQLAlchemyが発行するSQLをログに出力するかどうか。
    # 開発環境ではTrue、本番環境ではFalseにする。
    sql_echo: bool = False

    # CORSで許可するオリジンのリスト。
    # カンマ区切りの文字列を受け取り、リストに変換する。
    # 開発環境ではNext.jsの開発サーバー (http://localhost:3000) を許可する。
    cors_origins: list[str] = ["http://localhost:3000"]


# Settings のインスタンスはアプリ全体で1つだけ生成して使い回す。
# この変数をインポートするだけで設定にアクセスできる。
settings = Settings()
