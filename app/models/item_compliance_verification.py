import datetime
from app.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey
from sqlalchemy.orm import relationship


class ItemComplianceVerification(Base):
    __tablename__ = "item_compliance_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    compliance_verification_id = Column(
        Integer, ForeignKey("compliance_verifications.id"), nullable=True
    )
    nominal_quantity = Column(String(150))
    sample_weight_agm = Column(String(150))
    average_weight = Column(String(150))
    actual_quantity = Column(String(150))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    compliance_verification = relationship(
        "ComplianceVerification", backref="item_compliance_verifications"
    )

    def __repr__(self):
        return "<ItemComplianceVerification.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        colums["compliance_verification"] = (
            self.compliance_verification.toDict()
            if self.compliance_verification
            else None
        )
        return colums
