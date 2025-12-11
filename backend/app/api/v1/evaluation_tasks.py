# app/api/v1/evaluation_tasks.py
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation-tasks", tags=["evaluation-tasks"])


@router.get("/my")
def get_my_tasks(periodId: str = None):
    """
    ログインユーザーが評価者となっているタスク一覧を取得。
    """
    # TODO: 実装
    pass

@router.get("")
def get_all_tasks():
    """
    すべての評価タスク一覧を取得。
    管理者用。
    """
    # TODO: 実装
    pass


@router.get("/{taskId}")
def get_task_detail(taskId: str):
    """
    個別評価画面用のタスク詳細を取得。
    セクション・設問・現在のスコア等はevaluation-resultsやquestion-master,evaluation-formsで取得する。
    """
    # TODO: 実装
    pass


@router.patch("/{taskId}")
def update_task(taskId: str):
    """
    評価進行・ステータス更新。
    """
    # TODO: 実装
    pass

