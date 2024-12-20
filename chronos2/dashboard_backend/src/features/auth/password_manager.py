import bcrypt


class PasswordManager:

    def hash_password(self, password: str) -> str:
        password = password.encode()
        return bcrypt.hashpw(password, bcrypt.gensalt()).decode()

    def verify_password(
        self, plain_password: str | bytes, hashed_password: str | bytes
    ) -> bool:
        if isinstance(plain_password, str):
            plain_password = plain_password.encode()
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode()

        return bcrypt.checkpw(plain_password, hashed_password)
