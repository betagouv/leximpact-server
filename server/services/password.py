from hashlib import sha3_512
from secrets import randbelow, token_bytes
from scrypt import hash as encrypt  # type: ignore
from toolz.functoolz import pipe


def create_salt() -> bytes:
    """Creates a 64 bytes salt hash to hash the password"""
    return pipe(512, randbelow, token_bytes, sha3_512).digest()


def create_password(passphrase: str, salt: bytes) -> bytes:
    """Create a password from a passphrase"""
    return encrypt(passphrase, salt)


def verify_password(password: bytes, passphrase: str, salt: bytes) -> bool:
    """Check actual password against expected human passphrase"""
    return password == create_password(passphrase, salt)
