"""Fixtures para pruebas HTTP del flujo comercial vigente de TortuScript."""
import hashlib

from tortuscript.auth import AuthRepository


def preparar_sesion_educativa(app, client, email="prueba@example.com", nombre="Ana", token="test-token"):
    """Crea cuenta verificada, inicia sesión, selecciona ChildProfile y completa onboarding."""
    db = app.config["ACCOUNT_DB"]
    password = "una-clave-larga-123"
    registro = client.post("/cuenta/registro", json={"email": email, "password": password})
    if registro.status_code != 202:
        raise AssertionError(f"registro de fixture: {registro.status_code} {registro.get_data(as_text=True)}")

    account_id = "acc_" + hashlib.sha256(email.strip().lower().encode()).hexdigest()[:24]
    AuthRepository(db).marcar_verificada(account_id)

    login = client.post("/cuenta/login", json={"email": email, "password": password})
    if login.status_code != 200:
        raise AssertionError(f"login de fixture: {login.status_code} {login.get_data(as_text=True)}")
    csrf = login.json["csrf"]

    perfil = client.post(
        "/cuenta/perfiles",
        json={"nombre": nombre},
        headers={"X-Tortu-CSRF": csrf},
    )
    if perfil.status_code != 201:
        raise AssertionError(f"perfil de fixture: {perfil.status_code} {perfil.get_data(as_text=True)}")

    seleccionado = client.post(
        "/cuenta/perfil",
        json={"perfil_id": perfil.json["perfil"]["id"]},
        headers={"X-Tortu-CSRF": csrf},
    )
    if seleccionado.status_code != 200:
        raise AssertionError(f"selección de fixture: {seleccionado.status_code} {seleccionado.get_data(as_text=True)}")

    onboarding = client.post(
        "/api/onboarding",
        json={"nombre": nombre, "experiencia": "nunca", "meta_min": 15},
        headers={"X-Tortu-Token": token},
    )
    if onboarding.status_code != 200:
        raise AssertionError(f"onboarding de fixture: {onboarding.status_code} {onboarding.get_data(as_text=True)}")

    return {"csrf": csrf, "perfil_id": perfil.json["perfil"]["id"], "headers": {"X-Tortu-Token": token}}
