# app/schemas/base.py
from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CamelModel(BaseModel):
    """
    - Python側では snake_case フィールド名を使う
    - JSON では camelCase に自動変換する
    - ORM モデルからの取得にも対応（from_attributes=True）
    """

    model_config = ConfigDict(
        alias_generator=to_camel,   # snake_case -> camelCase
        populate_by_name=True,      # snake_case / camelCase どちらも受け取れる
        from_attributes=True,       # ORM モデルからの生成を許可
    )
