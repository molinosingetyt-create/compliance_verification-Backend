import datetime
from app.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey
from sqlalchemy.orm import relationship


class PackagingMachine(Base):
    __tablename__ = "packaging_machines"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), unique=True, index=True)
    alias = Column(String(150))
    url = Column(String(150), nullable=True)
    packaging_area_id = Column(Integer, ForeignKey("packaging_areas.id"), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    packaging_area = relationship("PackagingArea", backref="packaging_machines")

    def __repr__(self):
        return "<PackagingMachine.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        colums["packaging_area"] = (
            self.packaging_area.toDict() if self.packaging_area else None
        )
        return colums
