from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey
from sqlalchemy.orm import relationship


class ComplianceVerification(Base):
    __tablename__ = "compliance_verifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sampled = Column(String(150))
    # Destino comercial: nacional | exportacion
    market_destination = Column(String(30), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    grammage_id = Column(Integer, ForeignKey("grammages.id"), nullable=True)
    analyzed = Column(String(150))
    machine_id = Column(Integer, ForeignKey("packaging_machines.id"), nullable=True)
    lot_expires = Column(String(150))
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(
        DateTime, default=now_bogota, onupdate=now_bogota
    )

    product = relationship("Product", backref="compliance_verifications")
    brand = relationship("Brand", backref="compliance_verifications")
    grammage = relationship("Grammage", backref="compliance_verifications")
    machine = relationship("PackagingMachine", backref="compliance_verifications")

    def __repr__(self):
        return "<ComplianceVerification.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        colums["product"] = self.product.toDict() if self.product else None
        colums["brand"] = self.brand.toDict() if self.brand else None
        colums["grammage"] = self.grammage.toDict() if self.grammage else None
        colums["machine"] = self.machine.toDict() if self.machine else None
        return colums
