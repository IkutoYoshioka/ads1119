from fastapi import APIRouter

router = APIRouter(prefix="/imports", tags=["imports"])

@router.post("/employees")
def import_employees():
    """
    社員データをインポート。
    """
    # TODO: 実装
    pass

@router.post("/questions")
def import_questions():
    """
    質問データをインポート。
    """
    # TODO: 実装
    pass