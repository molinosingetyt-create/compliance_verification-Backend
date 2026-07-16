import statistics
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from app.models.compliance_verification import ComplianceVerification
from app.models.item_compliance_verification import ItemComplianceVerification
from app.models.package_weight import PackageWeight
from app.models.parameters.units_packed_hour import UnitsPackedHour
from app.models.parameters.grammage import Grammage
from app.models.parameters.lot_size import LotSize
from app.models.parameters.packaging_machine import PackagingMachine
from app.lib.config.database import SessionLocal
from app.lib.timezone import now_bogota
from app.lib.security.sampling_scope import (
    assert_verification_access,
    filter_verifications_owned,
)
from app.models.user import User
from sqlalchemy.orm import joinedload
from fastapi.encoders import jsonable_encoder
import logging


ALLOWED_MARKET_DESTINATIONS = frozenset({"nacional", "exportacion"})


class ComplianceVerificationController:
    @staticmethod
    def _active_only(query):
        return query.filter(ComplianceVerification.deleted_at.is_(None))

    @staticmethod
    def _apply_created_at_range(query, date_from: str | None, date_to: str | None):
        if date_from:
            try:
                start = datetime.strptime(date_from.strip(), "%Y-%m-%d")
                query = query.filter(ComplianceVerification.created_at >= start)
            except ValueError:
                raise HTTPException(status_code=400, detail="date_from inválida (use YYYY-MM-DD)")
        if date_to:
            try:
                end = datetime.strptime(date_to.strip(), "%Y-%m-%d").replace(
                    hour=23, minute=59, second=59
                )
                query = query.filter(ComplianceVerification.created_at <= end)
            except ValueError:
                raise HTTPException(status_code=400, detail="date_to inválida (use YYYY-MM-DD)")
        return query

    @staticmethod
    def _compute_item_status(actual_quantity: float, nominal_value: float, tolerance: float) -> int:
        limit_t1 = nominal_value - tolerance
        limit_t2 = nominal_value - (tolerance * 2)
        if actual_quantity < limit_t2:
            return 3
        if actual_quantity < limit_t1:
            return 2
        return 1

    @staticmethod
    def _recompute_verification_status(verification: ComplianceVerification, nominal_value: float, tolerance: float):
        items = verification.item_compliance_verifications or []
        count_t1 = 0
        count_t2 = 0
        net_sum = 0.0

        for item in items:
            try:
                aq = float(item.actual_quantity)
            except Exception:
                aq = 0.0
            net_sum += aq
            new_status = ComplianceVerificationController._compute_item_status(aq, nominal_value, tolerance)
            item.status = new_status
            if new_status == 2:
                count_t1 += 1
            elif new_status == 3:
                count_t1 += 1
                count_t2 += 1

        # reglas de lote
        allowed_t1 = 0
        try:
            with SessionLocal() as db:
                units_hour = (
                    db.query(UnitsPackedHour)
                    .filter(
                        UnitsPackedHour.packaging_machine_id == verification.machine_id,
                        UnitsPackedHour.grammage_id == verification.grammage_id,
                        UnitsPackedHour.status == 1,
                    )
                    .first()
                )
                if units_hour:
                    lot_size = ComplianceVerificationController.get_sample_size(int(units_hour.value), db)
                    if lot_size:
                        allowed_t1 = int(lot_size.allowed_with_error)
        except Exception:
            allowed_t1 = 0

        final_status = 1
        if count_t2 > 0 or count_t1 > allowed_t1:
            final_status = 2
        n = len(items)
        avg_net = (net_sum / n) if n > 0 else 0
        if avg_net < nominal_value:
            final_status = 2
        verification.status = final_status

        return {
            "verification_status": final_status,
            "errors_found": {"T1": count_t1, "T2": count_t2},
            "allowed_t1": allowed_t1,
            "avg_net_weight": round(avg_net, 2),
        }


    @staticmethod
    def create(data, sampled_by_user_id: int | None = None):
        try:
            # Validación básica de entrada
            required_fields = [
                "machine_id",
                "grammage_id",
                "items",
                "product_id",
                "brand_id",
                "sampled",
                "market_destination",
                "analyzed",
                "lot_expires",
            ]
            for field in required_fields:
                if not hasattr(data, field):
                    raise HTTPException(
                        status_code=400, detail=f"Falta el campo requerido: {field}"
                    )
            if not isinstance(data.items, list) or len(data.items) == 0:
                raise HTTPException(
                    status_code=400, detail="La lista de ítems no puede estar vacía"
                )

            market_destination = (getattr(data, "market_destination", None) or "").strip().lower()
            if market_destination not in ALLOWED_MARKET_DESTINATIONS:
                raise HTTPException(
                    status_code=400,
                    detail="Destino comercial inválido. Use nacional o exportacion.",
                )

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
                        status_code=404,
                        detail="No existe configuración de unidades/hora",
                    )

                grammage_obj = (
                    db.query(Grammage).filter(Grammage.id == data.grammage_id).first()
                )
                if not grammage_obj:
                    logging.error("Gramaje no encontrado")
                    raise HTTPException(status_code=404, detail="Gramaje no encontrado")

                # Extraer valor nominal y tolerance
                nominal_value = float("".join(filter(str.isdigit, grammage_obj.name)))
                try:
                    tolerance = float(grammage_obj.tolerance)
                except Exception:
                    logging.error("Error extrayendo tolerance de gramaje")
                    raise HTTPException(status_code=400, detail="tolerance inválida")

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
                    logging.error(
                        "Muestra insuficiente: %s de %s",
                        received_sample_size,
                        required_sample_size,
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "Muestra insuficiente. Se requieren "
                            f"{required_sample_size} ítems, pero se recibieron "
                            f"{received_sample_size}."
                        ),
                    )

                # 3️⃣ Procesar Items y Contar Errores
                items_to_save = []
                count_t1 = 0
                count_t2 = 0
                net_content_sum = 0.0  # suma de contenido neto por ítem (para promedio global)

                # Límites de control
                limit_t1 = nominal_value - tolerance
                limit_t2 = nominal_value - (tolerance * 2)

                for item in data.items:
                    try:
                        actual_weight = float(item.sample_weight_agm)
                        average_weight = float(item.average_weight)
                    except Exception:
                        logging.error("Peso inválido en ítem")
                        raise HTTPException(
                            status_code=400, detail="Peso inválido en ítem"
                        )
                    net_content_sum += average_weight
                    status_item = 1

                    # Validación de Errores (Prioridad T2 sobre T1)
                    if average_weight < limit_t2:
                        status_item = 3
                        count_t2 += 1
                    elif average_weight < limit_t1:
                        status_item = 2
                        count_t1 += 1

                    items_to_save.append(
                        ItemComplianceVerification(
                            compliance_verification_id=None,
                            nominal_quantity=nominal_value,
                            sample_weight_agm=actual_weight,
                            average_weight=actual_weight - average_weight,
                            actual_quantity=average_weight,
                            status=status_item,
                        )
                    )

                # 4️⃣ Determinación del Resultado Final (CUMPLE / NO CUMPLE)
                allowed_t1 = int(lot_size.allowed_with_error)
                final_status = 1
                if count_t2 > 0 or count_t1 > allowed_t1:
                    final_status = 2
                # Tercera condición: el promedio del contenido neto debe ser >= al nominal
                avg_net_content = net_content_sum / received_sample_size
                if avg_net_content < nominal_value:
                    final_status = 2

                # 5️⃣ Guardar Verificación Principal
                verification = ComplianceVerification(
                    sampled=data.sampled,
                    market_destination=market_destination,
                    product_id=data.product_id,
                    brand_id=data.brand_id,
                    grammage_id=data.grammage_id,
                    analyzed=data.analyzed,
                    machine_id=data.machine_id,
                    lot_expires=data.lot_expires,
                    sampled_by_user_id=sampled_by_user_id,
                    status=final_status,
                )

                db.add(verification)
                db.commit()

                # 5.1️⃣ Guardar pesos de empaques (si vienen en el request)
                if getattr(data, "package_weights", None):
                    weights_to_save = []
                    for w in data.package_weights:
                        if w is None:
                            continue
                        s = str(w).strip()
                        if s == "":
                            continue
                        weights_to_save.append(
                            PackageWeight(
                                compliance_verification_id=verification.id,
                                weight=s,
                            )
                        )
                    if weights_to_save:
                        db.bulk_save_objects(weights_to_save)
                        db.commit()

                for i in items_to_save:
                    i.compliance_verification_id = verification.id
                db.bulk_save_objects(items_to_save)
                db.commit()
                db.refresh(verification)

                response_data = {
                    "detail": (
                        "¡Verificación procesada exitosamente! Resultado: "
                        f"{'CUMPLE' if final_status == 1 else 'NO CUMPLE'}"
                    ),
                    "result": final_status,
                    "errors_found": {"T1": count_t1, "T2": count_t2},
                    "allowed_t1": allowed_t1,
                    "data": verification,
                }

            # Esto convierte el objeto 'verification' en un diccionario simple
            return jsonable_encoder(response_data)
        except HTTPException:
            raise
        except Exception as e:
            logging.exception("Error inesperado en verificación de cumplimiento")
            raise HTTPException(status_code=500, detail=str(e))

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

    @staticmethod
    def get_all(
        user: User,
        permission_codes: set[str],
        date_from: str | None = None,
        date_to: str | None = None,
    ):
        db = SessionLocal()
        try:
            query = (
                db.query(ComplianceVerification)
                .options(
                    joinedload(ComplianceVerification.product),
                    joinedload(ComplianceVerification.machine).joinedload(
                        PackagingMachine.packaging_area
                    ),
                    joinedload(ComplianceVerification.grammage),
                    joinedload(ComplianceVerification.brand),
                    joinedload(ComplianceVerification.item_compliance_verifications)
                )
                .order_by(ComplianceVerification.id.desc())
            )
            query = ComplianceVerificationController._active_only(query)
            query = ComplianceVerificationController._apply_created_at_range(
                query, date_from, date_to
            )
            verifications = query.all()
            verifications = filter_verifications_owned(verifications, user, permission_codes)

            result = []

            for v in verifications:
                items = v.item_compliance_verifications
                net_weights = []   # actual_quantity (Contenido neto real)
                gross_weights = []  # sample_weight_agm (Contenido bruto: neto + bolsa)
                
                # Contadores de errores según status del item
                t1_errors_count = 0
                t2_errors_count = 0
                under_nominal_count = 0 # Unidades debajo del peso neto nominal

                # Extraer valor nominal del gramaje
                nominal_value = 0
                if v.grammage:
                    digits = "".join(filter(str.isdigit, v.grammage.name))
                    nominal_value = float(digits) if digits else 0

                for item in items:
                    try:
                        # Procesar Pesos
                        val_net = float(item.actual_quantity) if item.actual_quantity is not None else None
                        val_gross = float(item.sample_weight_agm) if item.sample_weight_agm is not None else None

                        if val_net is not None:
                            net_weights.append(val_net)
                            # Unidades debajo del peso neto nominal
                            if val_net < nominal_value:
                                under_nominal_count += 1
                        
                        if val_gross is not None:
                            gross_weights.append(val_gross)

                        # Conteo de errores por ESTADO del item
                        # 1 = OK, 2 = Error T1, 3 = Error T2
                        if item.status == 2:
                            t1_errors_count += 1
                        elif item.status == 3:
                            t1_errors_count += 1
                            t2_errors_count += 1

                    except (ValueError, TypeError):
                        continue

                # Cálculos Estadísticos
                n = len(net_weights)
                avg_net_weight = sum(net_weights) / n if n > 0 else 0
                avg_gross_weight = sum(gross_weights) / len(gross_weights) if len(gross_weights) > 0 else 0
                
                # Desviación estándar (Neto)
                std_dev = statistics.stdev(net_weights) if n > 1 else 0

                # Porcentaje de unidades bajo el peso neto
                percentage_under_nominal = (under_nominal_count / n * 100) if n > 0 else 0

                result.append({
                    "id": v.id,
                    "created_at": v.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "sampled": v.sampled,
                    "market_destination": v.market_destination,
                    "product_id": v.product_id,
                    "machine_id": v.machine_id,
                    "brand_id": v.brand_id,
                    "grammage_id": v.grammage_id,
                    "packaging_area_id": (
                        v.machine.packaging_area_id if v.machine else None
                    ),
                    "packaging_area_name": (
                        v.machine.packaging_area.name
                        if v.machine and v.machine.packaging_area
                        else None
                    ),
                    "product_name": v.product.name if v.product else None,
                    "machine_name": v.machine.name if v.machine else None,
                    "grammage_name": v.grammage.name if v.grammage else None,
                    "brand_name": v.brand.name if v.brand else None,
                    "tolerance": float(v.grammage.tolerance) if v.grammage and v.grammage.tolerance else 0,
                    
                    # --- Métricas Calculadas ---
                    "nominal_value": nominal_value,
                    "avg_net_weight": round(avg_net_weight, 2),      # Promedio contenido real
                    "avg_gross_weight": round(avg_gross_weight, 2),  # Promedio con empaque
                    "t1_errors_count": t1_errors_count,              # Basado en status 2
                    "t2_errors_count": t2_errors_count,              # Basado en status 3
                    "under_nominal_count": under_nominal_count,      # Unidades < peso neto
                    "percentage_under_nominal": round(percentage_under_nominal, 2),
                    "standard_deviation": round(std_dev, 4),
                    # --------------------------
                    
                    "analyzed": v.analyzed,
                    "lot_expires": v.lot_expires,
                    "status": v.status, # Status final de la verificación (Cumple/No cumple)
                })

            return result

        except Exception as e:
            logging.exception("Error al listar verificaciones con métricas corregidas")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
            
    @staticmethod
    def get_by_id(id, user: User, permission_codes: set[str]):
        db = SessionLocal()
        try:
            verification = (
                ComplianceVerificationController._active_only(
                    db.query(ComplianceVerification)
                )
                .options(
                    joinedload(ComplianceVerification.item_compliance_verifications),
                    joinedload(ComplianceVerification.package_weights),
                    joinedload(ComplianceVerification.product),
                    joinedload(ComplianceVerification.brand),
                    joinedload(ComplianceVerification.grammage),
                    joinedload(ComplianceVerification.machine),
                )
                .filter(ComplianceVerification.id == id)
                .first()
            )

            return assert_verification_access(verification, user, permission_codes)

        except HTTPException:
            raise
        except Exception as e:
            logging.exception("Error obteniendo verificación por ID")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    @staticmethod
    def soft_delete(verification_id: int, user: User, permission_codes: set[str]):
        db = SessionLocal()
        try:
            verification = (
                ComplianceVerificationController._active_only(
                    db.query(ComplianceVerification)
                )
                .filter(ComplianceVerification.id == verification_id)
                .first()
            )
            assert_verification_access(verification, user, permission_codes)
            verification.deleted_at = now_bogota()
            db.add(verification)
            db.commit()
            return {"detail": "Muestreo eliminado correctamente"}
        except HTTPException:
            raise
        except Exception as e:
            logging.exception("Error eliminando verificación")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    @staticmethod
    def get_package_weights(id, user: User, permission_codes: set[str]):
        db = SessionLocal()
        try:
            verification = (
                ComplianceVerificationController._active_only(
                    db.query(ComplianceVerification)
                )
                .options(joinedload(ComplianceVerification.package_weights))
                .filter(ComplianceVerification.id == id)
                .first()
            )

            assert_verification_access(verification, user, permission_codes)

            weights = []
            for w in verification.package_weights or []:
                try:
                    weights.append(float(w.weight))
                except Exception:
                    # si por alguna razón hay valores no numéricos, los devolvemos como string
                    pass

            avg = round(sum(weights) / len(weights), 2) if weights else 0
            return {"package_weights": weights, "average_weight": avg}
        except HTTPException:
            raise
        except Exception as e:
            logging.exception("Error obteniendo pesos de empaques")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()

    @staticmethod
    def update_package_weights(
        verification_id: int,
        package_weights: list[float],
        user: User,
        permission_codes: set[str],
    ):
        if not package_weights:
            raise HTTPException(status_code=400, detail="Debe enviar al menos un peso de empaque")
        parsed: list[float] = []
        for w in package_weights:
            try:
                val = float(w)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Peso de empaque inválido")
            if val <= 0:
                raise HTTPException(status_code=400, detail="Cada peso de empaque debe ser mayor que cero")
            parsed.append(round(val, 2))

        with SessionLocal() as db:
            verification = (
                ComplianceVerificationController._active_only(
                    db.query(ComplianceVerification)
                )
                .options(joinedload(ComplianceVerification.item_compliance_verifications))
                .options(joinedload(ComplianceVerification.package_weights))
                .options(joinedload(ComplianceVerification.grammage))
                .filter(ComplianceVerification.id == verification_id)
                .first()
            )
            assert_verification_access(verification, user, permission_codes)

            for pw in list(verification.package_weights or []):
                db.delete(pw)
            db.flush()

            for w in parsed:
                db.add(
                    PackageWeight(
                        compliance_verification_id=verification.id,
                        weight=str(w),
                    )
                )
            db.flush()

            package_avg = ComplianceVerificationController._package_average_for_verification(
                verification
            )
            for item in verification.item_compliance_verifications or []:
                try:
                    agm = float(item.sample_weight_agm)
                except (TypeError, ValueError):
                    continue
                ComplianceVerificationController._apply_item_weights_from_agm(
                    item, agm, package_avg
                )
                db.add(item)

            grammage_obj = (
                db.query(Grammage)
                .filter(Grammage.id == verification.grammage_id)
                .first()
            )
            if not grammage_obj:
                raise HTTPException(status_code=404, detail="Gramaje no encontrado")

            nominal_value = float("".join(filter(str.isdigit, grammage_obj.name)) or 0)
            try:
                tolerance = float(grammage_obj.tolerance)
            except Exception:
                tolerance = 0.0

            metrics = ComplianceVerificationController._recompute_verification_status(
                verification, nominal_value, tolerance
            )
            db.add(verification)
            db.commit()

            verdict = "CUMPLE" if metrics["verification_status"] == 1 else "NO CUMPLE"
            return {
                "detail": (
                    f"Pesos de empaque actualizados. Promedio: {package_avg} g. "
                    f"Veredicto del muestreo: {verdict}."
                ),
                "package_weights": parsed,
                "average_weight": package_avg,
                "metrics": metrics,
            }

    @staticmethod
    def _package_average_for_verification(verification: ComplianceVerification) -> float:
        weights = []
        for w in verification.package_weights or []:
            try:
                weights.append(float(w.weight))
            except (TypeError, ValueError):
                continue
        return round(sum(weights) / len(weights), 2) if weights else 0.0

    @staticmethod
    def _apply_item_weights_from_agm(item: ItemComplianceVerification, agm: float, package_avg: float):
        """Qi = AGM − promedio empaque; ATM (campo average_weight) = AGM − Qi."""
        qi = round(agm - package_avg, 2)
        item.sample_weight_agm = str(round(agm, 2))
        item.actual_quantity = str(qi)
        item.average_weight = str(round(agm - qi, 2))

    @staticmethod
    def _apply_item_weights_from_qi(item: ItemComplianceVerification, qi: float, package_avg: float):
        agm = round(qi + package_avg, 2)
        item.actual_quantity = str(round(qi, 2))
        item.sample_weight_agm = str(agm)
        item.average_weight = str(round(agm - qi, 2))

    @staticmethod
    def update_item(
        item_id: int,
        sample_weight_agm: Optional[float] = None,
        actual_quantity: Optional[float] = None,
        user: User | None = None,
        permission_codes: set[str] | None = None,
    ):
        if sample_weight_agm is None and actual_quantity is None:
            raise HTTPException(
                status_code=400,
                detail="Debe enviar sample_weight_agm o actual_quantity",
            )

        with SessionLocal() as db:
            item = (
                db.query(ItemComplianceVerification)
                .filter(ItemComplianceVerification.id == item_id)
                .first()
            )
            if not item:
                raise HTTPException(status_code=404, detail="Ítem no encontrado")

            verification = (
                ComplianceVerificationController._active_only(
                    db.query(ComplianceVerification)
                )
                .options(joinedload(ComplianceVerification.item_compliance_verifications))
                .options(joinedload(ComplianceVerification.package_weights))
                .options(joinedload(ComplianceVerification.grammage))
                .filter(ComplianceVerification.id == item.compliance_verification_id)
                .first()
            )
            if not verification:
                raise HTTPException(status_code=404, detail="Verificación no encontrada")

            if user is not None and permission_codes is not None:
                assert_verification_access(verification, user, permission_codes)

            package_avg = ComplianceVerificationController._package_average_for_verification(
                verification
            )

            if sample_weight_agm is not None:
                agm = float(sample_weight_agm)
                if agm <= 0:
                    raise HTTPException(status_code=400, detail="AGM debe ser mayor que cero")
                ComplianceVerificationController._apply_item_weights_from_agm(
                    item, agm, package_avg
                )
            else:
                qi = float(actual_quantity)
                ComplianceVerificationController._apply_item_weights_from_qi(
                    item, qi, package_avg
                )

            grammage_obj = (
                db.query(Grammage)
                .filter(Grammage.id == verification.grammage_id)
                .first()
            )
            if not grammage_obj:
                raise HTTPException(status_code=404, detail="Gramaje no encontrado")

            nominal_value = float("".join(filter(str.isdigit, grammage_obj.name)) or 0)
            try:
                tolerance = float(grammage_obj.tolerance)
            except Exception:
                tolerance = 0.0

            metrics = ComplianceVerificationController._recompute_verification_status(
                verification, nominal_value, tolerance
            )

            db.add(item)
            db.add(verification)
            db.commit()
            db.refresh(item)
            db.refresh(verification)

            verdict = "CUMPLE" if metrics["verification_status"] == 1 else "NO CUMPLE"
            return {
                "detail": f"Ítem actualizado. Veredicto del muestreo: {verdict}.",
                "metrics": metrics,
                "item": item.toDict(),
                "verification": verification.toDict(),
            }

    @staticmethod
    def update_item_actual_quantity(item_id: int, actual_quantity: float):
        """Compatibilidad: edición directa de Qi."""
        return ComplianceVerificationController.update_item(
            item_id, actual_quantity=actual_quantity
        )
