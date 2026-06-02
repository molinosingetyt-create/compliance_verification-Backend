from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, String, DateTime, inspect


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True)  # administrador | ingeniero | auxiliar (perfil)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(DateTime, default=now_bogota, onupdate=now_bogota)

    def __repr__(self):
        return "<Role.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        return colums

