from fastapi import APIRouter

router = APIRouter(prefix="/exports", tags=["exports"])

@router.get("/evaluation-results")
def export_evaluation_results():
    """
    評価結果データをエクスポート。
    """
    # TODO: 実装
    pass