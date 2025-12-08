from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/evaluator")
def get_evaluator_dashboard():  
    """
    被評価者ダッシュボード用データを返す。
    """
    # TODO: 実装
    pass

@router.get("/evaluatee")
def get_evaluatee_dashboard():
    """
    評価者ダッシュボード用データを返す。
    """
    # TODO: 実装
    pass

@router.get("/manager/{facility_id}")
def get_manager_dashboard(facility_id: int):
    """
    施設長ダッシュボード用データを返す。
    """
    # TODO: 実装
    pass

@router.get("/admin")
def get_admin_dashboard():
    """
    管理者ダッシュボード用データを返す。
    """
    # TODO: 実装
    pass

