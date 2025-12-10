from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/home")
def get_dashboard_home():
    """
    ダッシュボードのホーム情報を取得。
    """
    # TODO: 実装
    pass