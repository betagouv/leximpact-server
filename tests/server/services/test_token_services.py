from server.services.token_services import (  # type: ignore
    create_nonce,
    create_token,
    decode_token,
    create_payload,
)


def test_decode_token():
    user = "richard@leximpact.pop"
    uuid = create_nonce().decode("ascii")
    iss = "Moi"
    aud = "Vous"
    payload = create_payload(user, uuid, iss, aud)
    secret = "asdf1234"
    algo = "HS256"
    token = create_token(payload, secret, algo)
    assert decode_token(token, secret, iss, aud, algo) == (user, uuid)
