from fastapi import HTTPException
from app.models.compliance_verification import ComplianceVerification
from app.models.item_compliance_verification import ItemComplianceVerification
from app.models.parameters.units_packed_hour import UnitsPackedHour
from app.models.parameters.lot_size import LotSize
from app.lib.config.database import SessionLocal


class ComplianceVerificationController:

    @staticmethod
    def create(data):

        db = SessionLocal()

        try:

            # 1️⃣ buscar unidades empacadas por hora
            units_hour = (
                db.query(UnitsPackedHour)
                .filter(
                    UnitsPackedHour.packaging_machine_id == data.machine_id,
                    UnitsPackedHour.grammage_id == data.grammage_id,
                    UnitsPackedHour.status == 1,
                )
                .first()
            )

            if not units_hour:
                raise HTTPException(
                    status_code=404,
                    detail="No existe configuración de unidades empacadas por hora para esta máquina",
                )

            units_value = int(units_hour.value)

            # 2️⃣ buscar tamaño de lote
            lot_size = ComplianceVerificationController.get_sample_size(units_value, db)

            if not lot_size:
                raise HTTPException(
                    status_code=404, detail="No existe configuración de tamaño de lote"
                )

            # si es inspección total
            if lot_size.sample_size.lower() == "inspeccion total":
                sample_required = units_value
            else:
                sample_required = int(lot_size.sample_size)

            # 3️⃣ validar tamaño de muestra
            if len(data.items) != sample_required:

                raise HTTPException(
                    status_code=400,
                    detail=f"""
                    El tamaño de muestra es incorrecto.

                    Producción por hora: {units_value}
                    Tamaño de muestra requerido: {sample_required}
                    Items enviados: {len(data.items)}
                    """,
                )

            # 4️⃣ crear verificación
            verification = ComplianceVerification(
                sampled=data.sampled,
                product_id=data.product_id,
                brand_id=data.brand_id,
                grammage_id=data.grammage_id,
                analyzed=data.analyzed,
                machine_id=data.machine_id,
                lot_expires=data.lot_expires,
            )

            db.add(verification)
            db.commit()
            db.refresh(verification)

            # 5️⃣ guardar items
            items = []

            for item in data.items:
                items.append(
                    ItemComplianceVerification(
                        compliance_verification_id=verification.id,
                        nominal_quantity=item.nominal_quantity,
                        sample_weight_agm=item.sample_weight_agm,
                        average_weight=item.average_weight,
                        actual_quantity=item.actual_quantity,
                    )
                )

            db.bulk_save_objects(items)
            db.commit()

            return {
                "message": "Verificación creada correctamente",
                "items_received": len(data.items),
                "data": verification.toDict(),
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

        finally:
            db.close()

    def get_sample_size(units_value, db):

        lot_sizes = (
            db.query(LotSize).filter(LotSize.status == 1).order_by(LotSize.id).all()
        )

        for lot in lot_sizes:

            name = lot.name.lower()

            # 20 o menos
            if "menos" in name:
                limit = int(name.split()[0])
                if units_value <= limit:
                    return lot

            # rango 600 a 100000
            elif "a" in name:
                parts = name.split("a")
                min_val = int(parts[0].strip())
                max_val = int(parts[1].strip())

                if min_val <= units_value <= max_val:
                    return lot

            # valores exactos (40,60,80...)
            else:
                limit = int(name)
                if units_value <= limit:
                    return lot

        return None
