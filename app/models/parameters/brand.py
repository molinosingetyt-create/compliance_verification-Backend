import datetime
from app.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, inspect


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), unique=True, index=True)
    alias = Column(String(150))
    url = Column(String(150), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    def __repr__(self):
        return "<Brand.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        return colums
