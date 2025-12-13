# app/api/v1/offices.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.office import Office
from app.crud.crud_office import list_active
from app.schemas.office import OfficeOut

router = APIRouter(prefix="/offices", tags=["offices"])

@router.get("", response_model=list[OfficeOut])
def get_offices(db: Session = Depends(get_db)):
    return list_active(db)


@router.get("/{officeId}")
def get_office(officeId: int):
    """
    特定の施設情報を取得。
    """
    # TODO: 実装
    pass


@router.post("")
def create_office():
    """
    施設を新規登録する。
    管理者
    """
    # TODO: 実装
    pass


@router.patch("/{officeId}")
def update_office(officeId: int):
    """
    施設情報を更新する。
    管理者
    """
    # TODO: 実装
    pass


@router.delete("/{officeId}")
def delete_office(officeId: int):
    """
    施設を削除（または無効化）する。
    管理者
    """
    # TODO: 実装
    pass
