from typing import List, Optional

from fastapi import Depends, HTTPException, Security, status

from pandemic import APIRouter

from ...commons import PagenationQuery
from ...database import Session, get_db
from . import schemas
from . import usecase as uc
from .models import User
from .perm import (
    FilterRole,
    UserRoles,
    get_current_active_user,
    get_current_admin_user,
    get_current_user,
    get_current_user_id,
)
from .utils import OAuth2PasswordRequestForm

guest_router = APIRouter()
user_router = APIRouter()
user_me_router = APIRouter()


@guest_router.post("/register", response_model=schemas.User)
async def register_user(
    db: Session = Depends(get_db),
    *,
    action: uc.RegisterUser,
) -> schemas.User:
    return action.do(db)


@guest_router.post("/login", response_model=schemas.Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    action = uc.TryLogin(
        user_name=form_data.username,
        password=form_data.password,
        scopes=form_data.scopes,
    )
    return action.do(db)


@guest_router.post(
    "/register_first_admin",
    response_model=schemas.User,
    description="""アプリケーション初期化状態の時、管理者ユーザーを作成します""",
)
async def register_first_admin(
    db: Session = Depends(get_db),
    *,
    action: uc.RegisterFirstAdmin,
) -> schemas.User:

    return action.do(db)


@user_me_router.post("/logout")
async def logout_me(result=Depends(uc.logout_user)):
    return result


@user_me_router.get("/", response_model=schemas.User)
async def get_me(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_active_user, scopes=["me"]),
):
    return current_user


@user_me_router.delete("/", status_code=200, response_model=int)
async def withdraw_me(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_active_user, scopes=["me"]),
) -> int:
    action = uc.DeleteUser(id=current_user.id)
    return action.do(db)


@user_me_router.patch("/modify_password", status_code=200, response_model=None)
async def modify_password_me(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_active_user, scopes=["me"]),
    *,
    data: uc.ModifiPassword,
) -> int:
    action = uc.ModifyUserPassword(user_id=current_user.id, password=data.password)
    return action.do(db)


@user_me_router.get("/admin_or_power", response_model=schemas.User)
async def get_me_if_admin_or_power(
    db: Session = Depends(get_db),
    current_user: User = FilterRole(UserRoles.admin, UserRoles.poweruser),
):
    return current_user


# @staticmethod
# @user_me_router.patch("/{id}", response_model=schemas.User)
# async def patch(
#     db: Session = Depends(get_db),
#     current_user: User = Security(get_current_active_user, scopes=["me"]),
#     *,
#     id: int,
#     data: schemas.User.prefab("Patch", optionals=...),
# ):
#     return UserService.patch(db, id=id, **data.dict())


@user_router.get("/", response_model=List[schemas.User])
async def index_user(
    db: Session = Depends(get_db),
    current_user: User = FilterRole(UserRoles.admin, UserRoles.poweruser),
    *,
    q: PagenationQuery,
):
    query = uc.IndexUser().query(db)
    return query.offset(q.skip).limit(q.limit).all()


@user_router.get("/{id}", response_model=schemas.User)
async def get_user(
    db: Session = Depends(get_db),
    current_user: User = FilterRole(UserRoles.admin, UserRoles.poweruser),
    *,
    id: int,
):
    acition = uc.GetUser(id=id)
    return acition.do(db)


# @staticmethod
# @user_router.delete("/user/{id}", status_code=200, response_model=int)
# async def delete_user(
#     db: Session = Depends(get_db),
#     current_user: User = Security(get_current_user),
#     *,
#     id: int,
# ) -> int:
#     return UserService.delete(db, id=id)
