from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, String, DateTime, inspect


class Permission(Base):
    """
    Permiso atómico. Ejemplos:
    - sampling:view
    - sampling:create
    - sampling:edit
    - users:manage
    """

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(80), unique=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(DateTime, default=now_bogota, onupdate=now_bogota)

    def __repr__(self):
        return "<Permission.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        return colums

