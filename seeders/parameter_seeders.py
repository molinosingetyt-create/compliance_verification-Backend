import json
import os
from app.models.parameters.brand import Brand
from app.models.parameters.grammage import Grammage
from app.models.parameters.lot_size import LotSize
from app.models.parameters.packaging_area import PackagingArea
from app.models.parameters.packaging_machine import PackagingMachine
from app.models.parameters.product import Product
from app.models.parameters.units_packed_hour import UnitsPackedHour

JSON_DIR = os.path.join(os.path.dirname(__file__), "../app/lib/json")


def load_json(filename):
    with open(os.path.join(JSON_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


def seed_brands(db):
    for data in load_json("brands.json"):
        if not db.query(Brand).filter_by(name=data["name"]).first():
            db.add(Brand(**data))
    db.commit()


def seed_grammages(db):
    for data in load_json("grammages.json"):
        if not db.query(Grammage).filter_by(name=data["name"]).first():
            db.add(Grammage(**data))
    db.commit()


def seed_lot_sizes(db):
    for data in load_json("lot_sizes.json"):
        if not db.query(LotSize).filter_by(name=data["name"]).first():
            db.add(LotSize(**data))
    db.commit()


def seed_packaging_areas(db):
    for data in load_json("packaging_areas.json"):
        if not db.query(PackagingArea).filter_by(name=data["name"]).first():
            db.add(PackagingArea(**data))
    db.commit()


def seed_packaging_machines(db):
    areas = {a.name: a.id for a in db.query(PackagingArea).all()}
    for data in load_json("packaging_machines.json"):
        area_name = data.pop("packaging_area", None)
        if area_name:
            data["packaging_area_id"] = areas.get(area_name)
        if not db.query(PackagingMachine).filter_by(name=data["name"]).first():
            db.add(PackagingMachine(**data))
    db.commit()


def seed_products(db):
    for data in load_json("products.json"):
        if not db.query(Product).filter_by(name=data["name"]).first():
            db.add(Product(**data))
    db.commit()


def seed_units_packed_hour(db):
    machines = {m.name: m.id for m in db.query(PackagingMachine).all()}
    grammages = {g.name: g.id for g in db.query(Grammage).all()}
    for data in load_json("units_packed_hour.json"):
        machine_name = data.pop("packaging_machine", None)
        grammage_name = data.pop("grammage", None)
        if machine_name:
            data["packaging_machine_id"] = machines.get(machine_name)
        if grammage_name:
            data["grammage_id"] = grammages.get(grammage_name)
        exists = (
            db.query(UnitsPackedHour)
            .filter_by(
                packaging_machine_id=data["packaging_machine_id"],
                grammage_id=data["grammage_id"],
            )
            .first()
        )
        if not exists:
            db.add(UnitsPackedHour(**data))
    db.commit()
