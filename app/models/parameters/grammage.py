from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, String, DateTime, inspect


class Grammage(Base):
    __tablename__ = "grammages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), unique=True, index=True)
    alias = Column(String(150))
    tolerance = Column(String(150))
    url = Column(String(150), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(
        DateTime, default=now_bogota, onupdate=now_bogota
    )

    def __repr__(self):
        return "<Grammage.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        return colums
