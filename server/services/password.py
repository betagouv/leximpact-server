from binascii import hexlify
from hashlib import sha512
from os import urandom
from scrypt import hash as encrypt  # type: ignore
from toolz.functoolz import pipe

SALT_SIZE = 128


def create_password(passphrase: str) -> str:
    """Create a password from a passphrase"""
    salt = create_salt()
    hashed = hash_passphrase(passphrase, salt)
    concat = salt + hashed
    return concat.decode("ascii")


def verify_password(password: str, passphrase: str):
    """Check actual password against expected human passphrase"""
    salt = password[:SALT_SIZE].encode("ascii")
    actual = password[SALT_SIZE:]
    expected = hash_passphrase(passphrase, salt).decode("ascii")
    return actual == expected


def create_salt() -> bytes:
    """Creates a salt hash to hash the password"""
    return pipe(SALT_SIZE, urandom, sha512).hexdigest().encode("ascii")


def hash_passphrase(passphrase: str, salt: bytes) -> bytes:
    """Hashes a human passphrase with a salt hash"""
    humanized = passphrase.encode("utf-8")
    encrypted = encrypt(humanized, salt)
    return hexlify(encrypted)
