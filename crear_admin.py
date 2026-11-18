
from getpass import getpass
from werkzeug.security import generate_password_hash

from database import init_db, get_user_by_username, create_user


def main():
    init_db()

    username = input("Usuario administrador: ").strip()

    if not username:
        print("El usuario no puede estar vacío.")
        return

    if get_user_by_username(username):
        print("El usuario ya existe.")
        return

    password = getpass("Contraseña: ")
    confirmation = getpass("Confirmar contraseña: ")

    if len(password) < 8:
        print("La contraseña debe tener al menos 8 caracteres.")
        return

    if password != confirmation:
        print("Las contraseñas no coinciden.")
        return

    password_hash = generate_password_hash(password)

    create_user(username, password_hash)

    print("Administrador creado correctamente.")


if __name__ == "__main__":
    main()
