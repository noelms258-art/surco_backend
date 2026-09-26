from getpass import getpass
from werkzeug.security import generate_password_hash

password = getpass("Introduce la contraseña: ")

password_hash = generate_password_hash(password)

print("\nHash generado:")
print(password_hash)