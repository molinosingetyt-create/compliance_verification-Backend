from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, inspect
from sqlalchemy.orm import relationship


class RolePermission(Base):
    __tablename__ = "role_permissions"

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(DateTime, default=now_bogota, onupdate=now_bogota)

    role = relationship("Role", backref="role_permissions")
    permission = relationship("Permission", backref="role_permissions")

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        colums["permission"] = self.permission.toDict() if self.permission else None
        return colums

