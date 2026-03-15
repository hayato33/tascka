"""SQLAlchemy ベースモデル定義。

すべてのモデルが継承する基底クラスを定義する。
DeclarativeBase を使うことで、モデルクラスを定義するだけで
SQLAlchemyが自動的にテーブル定義を認識する。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """すべてのSQLAlchemyモデルの基底クラス。

    DeclarativeBase を継承したクラスを作ることで、
    このクラスを継承したすべてのモデルが自動的にSQLAlchemyのメタデータに登録される。
    Alembicはこのメタデータを参照してマイグレーションを自動生成する。
    """

    pass
