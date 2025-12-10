from fastapi import APIRouter

router = APIRouter(prefix="/periods", tags=["periods"])

@router.get("")
def list_periods():
    """
    期間一覧を取得。
    """
    # TODO: 実装
    pass

@router.get("/{periodId}")
def get_period(periodId: str):
    """
    指定した期間の詳細を取得。
    """
    # TODO: 実装
    pass

@router.patch("/{periodId}")
def update_period(periodId: str):
    """
    期間の更新。
    """
    # TODO: 実装
    pass