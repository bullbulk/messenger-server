import bcrypt


def encrypt_password(pwd: str) -> str:
    hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def match_password(pwd: str, hashed_pwd: str) -> bool:
    return bcrypt.checkpw(pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))
