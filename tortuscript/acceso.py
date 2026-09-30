"""Servicio de autorización comercial para acceso por ChildProfile.

La decisión comercial pertenece al Account; el acceso educativo se consulta por
ChildProfile. Este módulo no autentica, no cobra y no modifica progreso.
"""
from tortuscript.cuentas import CuentaRepository, CuentaError


class AccesoError(ValueError):
    """Error de autorización comercial."""


class AccesoProducto:
    def __init__(self, repository: CuentaRepository):
        self.repository = repository

    def puede_acceder(self, profile_id: str, product: str) -> bool:
        if not isinstance(profile_id, str) or not profile_id:
            return False
        if not isinstance(product, str) or not product.strip():
            return False
        return self.repository.tiene_entitlement_por_perfil(profile_id, product.strip())

    def exigir_acceso(self, profile_id: str, product: str) -> None:
        if not self.puede_acceder(profile_id, product):
            raise AccesoError("El perfil no tiene acceso al producto solicitado.")

    def resumen_acceso(self, profile_id: str, products: list[str]) -> dict[str, bool]:
        if not isinstance(products, list):
            raise AccesoError("La lista de productos no es válida.")
        return {
            product: self.puede_acceder(profile_id, product)
            for product in products
            if isinstance(product, str) and product.strip()
        }
