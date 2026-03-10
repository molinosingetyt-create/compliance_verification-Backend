import datetime
from app.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey
from sqlalchemy.orm import relationship


class UnitsPackedHour(Base):
    __tablename__ = "units_packed_hours"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    packaging_machine_id = Column(
        Integer, ForeignKey("packaging_machines.id"), nullable=True
    )
    grammage_id = Column(Integer, ForeignKey("grammages.id"), nullable=True)
    value = Column(String(150), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    packaging_machine = relationship("PackagingMachine", backref="units_packed_hours")
    grammage = relationship("Grammage", backref="units_packed_hours")

    def __repr__(self):
        return "<UnitsPackedHour.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        colums["packaging_machine"] = (
            self.packaging_machine.toDict() if self.packaging_machine else None
        )
        colums["grammage"] = self.grammage.toDict() if self.grammage else None
        return colums
