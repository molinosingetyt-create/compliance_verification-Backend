from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User


def get_user_permission_codes(db: Session, user_id: int) -> set[str]:
    rows = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(User, User.role_id == Role.id)
        .filter(User.id == user_id)
        .all()
    )
    return {r[0] for r in rows if r and r[0]}
