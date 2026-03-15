"""SQLAlchemyモデルパッケージ。

すべてのモデルをここからインポートできるようにする。
Alembicがマイグレーションファイルを自動生成する際、
このパッケージからモデルを見つけるために必要。
"""

from app.models.tag import Tag, task_tags  # noqa: F401
from app.models.task import Task  # noqa: F401
