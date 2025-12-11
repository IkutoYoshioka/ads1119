from fastapi import APIRouter

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])

@router.get("")
def list_audit_logs():
    """
    監査ログ一覧を取得。
    """
    # TODO: 実装
    pass

@router.get("/{logId}")
def get_audit_log(logId: str):
    """
    特定の監査ログ詳細を取得。
    """
    # TODO: 実装
    pass