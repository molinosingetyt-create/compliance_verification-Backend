from app.models.base import Base
from app.lib.timezone import now_bogota
from sqlalchemy import Column, Integer, String, DateTime, inspect, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(80), unique=True, index=True)
    full_name = Column(String(150), nullable=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    packaging_area_id = Column(Integer, ForeignKey("packaging_areas.id"), nullable=True)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(DateTime, default=now_bogota, onupdate=now_bogota)

    role = relationship("Role", backref="users")
    packaging_area = relationship("PackagingArea", backref="users")

    def __repr__(self):
        return "<User.id %r>" % self.id

    def toDict(self):
        colums = {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
        colums["role"] = self.role.toDict() if self.role else None
        colums["packaging_area"] = (
            self.packaging_area.toDict() if self.packaging_area else None
        )
        # no exponer password_hash
        colums.pop("password_hash", None)
        return colums

