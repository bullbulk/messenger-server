import hashlib


def encrypt_password(pwd: str) -> str:
    hash_ = hashlib.md5(pwd.encode('utf-8')).hexdigest()
    return hash_
