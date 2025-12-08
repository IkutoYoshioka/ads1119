# app/api/v1/evaluation_tasks.py
from fastapi import APIRouter

router = APIRouter(prefix="/evaluation-tasks", tags=["evaluation-tasks"])


@router.get("/my")
def get_my_tasks():
    """
    ログインユーザーが評価者となっているタスク一覧を取得。
    """
    # TODO: 実装
    pass


@router.get("/{task_id}")
def get_task_detail(task_id: int):
    """
    個別評価画面用のタスク詳細を取得。
    セクション・設問・現在のスコア等。
    """
    # TODO: 実装
    pass


@router.put("/{task_id}")
def save_task(task_id: int):
    """
    タスクの下書き保存。
    """
    # TODO: 実装
    pass


@router.post("/{task_id}/submit")
def submit_task(task_id: int):
    """
    タスクの提出。
    一次 → 二次 → 最終 の順を守る。
    """
    # TODO: 実装
    pass
