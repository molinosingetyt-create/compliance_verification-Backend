from app.models.base import Base
from app.models.parameters import (
    brand,
    grammage,
    product,
    lot_size,
    packaging_area,
    packaging_machine,
    units_packed_hour,
)

# Modelos operativos (asegura que se registren en metadata).
from app.models import compliance_verification  # noqa: F401
from app.models import item_compliance_verification  # noqa: F401
from app.models import package_weight  # noqa: F401
from app.models import role  # noqa: F401
from app.models import user  # noqa: F401
from app.models import permission  # noqa: F401
from app.models import role_permission  # noqa: F401
