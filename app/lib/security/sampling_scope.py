from typing import Iterable, Set

from fastapi import HTTPException

from app.models.compliance_verification import ComplianceVerification
from app.models.user import User

VIEW_ALL_CODE = "sampling:view-all"
VIEW_OWN_CODE = "sampling:view-own"


def user_views_all_sampling(codes: Set[str]) -> bool:
    """Si tiene view-all ve todo; si solo view-own, solo los suyos; sin alcance explícito → todo (legacy)."""
    if VIEW_ALL_CODE in codes:
        return True
    if VIEW_OWN_CODE in codes:
        return False
    return True


def verification_owned_by_user(verification: ComplianceVerification, user: User) -> bool:
    if verification.sampled_by_user_id is not None:
        return verification.sampled_by_user_id == user.id

    sampled = (verification.sampled or "").strip().casefold()
    if not sampled:
        return False

    identities = {
        (user.full_name or "").strip().casefold(),
        (user.username or "").strip().casefold(),
    }
    identities.discard("")
    return sampled in identities


def filter_verifications_owned(
    verifications: Iterable[ComplianceVerification],
    user: User,
    codes: Set[str],
) -> list[ComplianceVerification]:
    if user_views_all_sampling(codes):
        return list(verifications)
    return [v for v in verifications if verification_owned_by_user(v, user)]


def assert_verification_access(
    verification: ComplianceVerification | None,
    user: User,
    codes: Set[str],
) -> ComplianceVerification:
    if verification is None or verification.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Verificación no encontrada")
    if user_views_all_sampling(codes):
        return verification
    if not verification_owned_by_user(verification, user):
        raise HTTPException(status_code=403, detail="Sin permiso para acceder a este muestreo")
    return verification
