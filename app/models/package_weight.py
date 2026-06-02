from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey
from sqlalchemy.orm import relationship


class PackageWeight(Base):
    __tablename__ = "package_weights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    compliance_verification_id = Column(
        Integer, ForeignKey("compliance_verifications.id"), nullable=False, index=True
    )
    weight = Column(String(150))
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(DateTime, default=now_bogota, onupdate=now_bogota)

    compliance_verification = relationship(
        "ComplianceVerification", backref="package_weights"
    )

    def __repr__(self):
        return "<PackageWeight.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        return colums

