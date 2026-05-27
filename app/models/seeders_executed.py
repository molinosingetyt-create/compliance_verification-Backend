from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from app.models.base import Base
from app.lib.timezone import now_bogota


# Modelo de control
class SeederExecuted(Base):
    __tablename__ = "seeders_executed"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    executed_at = Column(DateTime, default=now_bogota)
    created_at = Column(DateTime, default=now_bogota)
    updated_at = Column(
        DateTime, default=now_bogota, onupdate=now_bogota
    )


def run_seeder(db: Session, seeder_name: str, seeder_func):
    # Verifica si ya se ejecutó
    exists = db.query(SeederExecuted).filter_by(name=seeder_name).first()
    if exists:
        print(f"Seeder '{seeder_name}' ya ejecutado.")
        return
    # Ejecuta el seeder
    seeder_func(db)
    # Registra la ejecución
    db.add(SeederExecuted(name=seeder_name))
    db.commit()
    print(f"Seeder '{seeder_name}' ejecutado y registrado.")
