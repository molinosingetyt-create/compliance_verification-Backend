from fastapi import HTTPException
from app.models.compliance_verification import ComplianceVerification
from app.models.item_compliance_verification import ItemComplianceVerification
from app.models.parameters.units_packed_hour import UnitsPackedHour
from app.models.parameters.grammage import Grammage
from app.models.parameters.lot_size import LotSize
from app.lib.config.database import SessionLocal
import logging


class ComplianceVerificationController:

    @staticmethod
    def create(data):
        db = SessionLocal()
        try:
            # Validación básica de entrada
            required_fields = ["machine_id", "grammage_id", "items", "product_id", "brand_id", "sampled", "analyzed", "lot_expires"]
            for field in required_fields:
                if not hasattr(data, field):
                    raise HTTPException(status_code=400, detail=f"Falta el campo requerido: {field}")
            if not isinstance(data.items, list) or len(data.items) == 0:
                raise HTTPException(status_code=400, detail="La lista de ítems no puede estar vacía")

            with SessionLocal() as db:
                # 1️⃣ Buscar configuración base
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
                    logging.error("No existe configuración de unidades/hora")
                    raise HTTPException(
                        status_code=404, detail="No existe configuración de unidades/hora"
                    )

                grammage_obj = (
                    db.query(Grammage).filter(Grammage.id == data.grammage_id).first()
                )
                if not grammage_obj:
                    logging.error("Gramaje no encontrado")
                    raise HTTPException(status_code=404, detail="Gramaje no encontrado")

                # Extraer valor nominal y tolerancia
                nominal_value = float("".join(filter(str.isdigit, grammage_obj.name)))
                try:
                    tolerance = float(grammage_obj.tolerance)
                except Exception:
                    logging.error("Error extrayendo tolerancia de gramaje")
                    raise HTTPException(status_code=400, detail="Tolerancia inválida")

                # 2️⃣ Buscar tamaño de lote y reglas de error
                lot_size = ComplianceVerificationController.get_sample_size(
                    int(units_hour.value), db
                )
                if not lot_size:
                    logging.error("No existe configuración de lote")
                    raise HTTPException(
                        status_code=404, detail="No existe configuración de lote"
                    )
                required_sample_size = int(lot_size.sample_size)
                received_sample_size = len(data.items)
                if received_sample_size < required_sample_size:
                    logging.error(f"Muestra insuficiente: {received_sample_size} de {required_sample_size}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Muestra insuficiente. Se requieren {required_sample_size} ítems, pero se recibieron {received_sample_size}."
                    )

                # 3️⃣ Procesar Items y Contar Errores
                items_to_save = []
                count_t1 = 0
                count_t2 = 0

                # Límites de control
                limit_t1 = nominal_value - tolerance
                limit_t2 = nominal_value - (tolerance * 2)

                for item in data.items:
                    try:
                        actual_weight = float(item.sample_weight_agm)
                        average_weight = float(item.average_weight)
                    except Exception:
                        logging.error("Peso inválido en ítem")
                        raise HTTPException(status_code=400, detail="Peso inválido en ítem")
                    status_item = 1

                    # Validación de Errores (Prioridad T2 sobre T1)
                    if actual_weight < limit_t2:
                        status_item = 3
                        count_t2 += 1
                    elif actual_weight < limit_t1:
                        status_item = 1
                        count_t1 += 1

                    items_to_save.append(
                        ItemComplianceVerification(
                            compliance_verification_id=None,
                            nominal_quantity=nominal_value,
                            sample_weight_agm=actual_weight,
                            average_weight=average_weight,
                            actual_quantity=actual_weight - average_weight,
                            status=status_item,
                        )
                    )

                # 4️⃣ Determinación del Resultado Final (CUMPLE / NO CUMPLE)
                allowed_t1 = int(lot_size.allowed_with_error)
                final_status = 1
                if count_t2 > 0 or count_t1 > allowed_t1:
                    final_status = 2

                # 5️⃣ Guardar Verificación Principal
                verification = ComplianceVerification(
                    sampled=data.sampled,
                    product_id=data.product_id,
                    brand_id=data.brand_id,
                    grammage_id=data.grammage_id,
                    analyzed=data.analyzed,
                    machine_id=data.machine_id,
                    lot_expires=data.lot_expires,
                    status=final_status,
                )

                db.add(verification)
                db.commit()
                db.refresh(verification)
                for i in items_to_save:
                    i.compliance_verification_id = verification.id
                db.bulk_save_objects(items_to_save)
                db.commit()

                return {
                    "message": "Verificación procesada",
                    "result": final_status,
                    "errors_found": {"T1": count_t1, "T2": count_t2},
                    "allowed_t1": allowed_t1,
                    "data": verification,
                }
        except HTTPException as e:
            raise
        except Exception as e:
            logging.exception("Error inesperado en verificación de cumplimiento")
            raise HTTPException(status_code=500, detail=str(e))

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
    @staticmethod
    def get_sample_size(units_value, db):
        """
        Obtiene el tamaño de lote adecuado según el valor de unidades.
        Args:
            units_value (int): Unidades por hora.
            db: Sesión de base de datos.
        Returns:
            LotSize | None: Objeto de tamaño de lote o None si no hay coincidencia.
        """
        lot_sizes = (
            db.query(LotSize).filter(LotSize.status == 1).order_by(LotSize.id).all()
        )
        for lot in lot_sizes:
            name = lot.name.lower()
            try:
                if "menos" in name:
                    limit = int(name.split()[0])
                    if units_value <= limit:
                        return lot
                elif "a" in name:
                    parts = name.split("a")
                    min_val = int(parts[0].strip())
                    max_val = int(parts[1].strip())
                    if min_val <= units_value <= max_val:
                        return lot
                else:
                    limit = int(name)
                    if units_value <= limit:
                        return lot
            except Exception:
                logging.warning(f"Error interpretando nombre de lote: {name}")
                continue
        return None
