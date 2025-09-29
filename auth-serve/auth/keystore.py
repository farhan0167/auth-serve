# auth_serve/keystore.py
from __future__ import annotations

import base64
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from models.auth import JWKSToken

KEYS_DIR = Path("./.keys")
PRIVATE_DIR = KEYS_DIR / "private"
PUBLIC_DIR = KEYS_DIR / "public"
CURRENT_KID = KEYS_DIR / "current_kid.txt"


def _b64url_uint(n: int) -> str:
    """Base64url-encode an unsigned integer (no padding)."""
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


class KeyStore:
    """Loads the current private key for signing and all public keys for JWKS."""

    def __init__(self) -> None:
        KEYS_DIR.mkdir(exist_ok=True)
        PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
        PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # ---------- Creation / Rotation ----------

    def _write_current_kid(self, kid: str) -> None:
        CURRENT_KID.write_text(kid)

    def _read_current_kid(self) -> str:
        return CURRENT_KID.read_text().strip()

    def create_keypair(self) -> str:
        """Generate a new RSA keypair and make it current. Returns kid."""
        kid = uuid.uuid4().hex

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        (PRIVATE_DIR / f"{kid}.pem").write_bytes(private_pem)
        (PUBLIC_DIR / f"{kid}.pem").write_bytes(public_pem)
        self._write_current_kid(kid)
        return kid

    def rotate(self) -> str:
        """Alias for create_keypair(). Keep old public keys so old tokens verify."""
        return self.create_keypair()

    # ---------- Loading keys ----------

    def get_current_signing_key(self) -> Tuple[str, bytes]:
        """Returns (kid, private_pem_bytes)."""
        kid = self._read_current_kid()
        pem = (PRIVATE_DIR / f"{kid}.pem").read_bytes()
        return kid, pem

    def list_public_keys(self) -> List[Tuple[str, bytes]]:
        """[(kid, public_pem_bytes), ...] sorted by filename for stability."""
        pairs: List[Tuple[str, bytes]] = []
        for pem_path in sorted(PUBLIC_DIR.glob("*.pem")):
            pairs.append((pem_path.stem, pem_path.read_bytes()))
        return pairs

    # ---------- JWKS ----------

    def _public_pem_to_jwk(self, kid: str, public_pem: bytes) -> JWKSToken:
        """Convert a PEM public key to a JWK dict for JWKS."""
        public_key = serialization.load_pem_public_key(public_pem)
        if not isinstance(public_key, rsa.RSAPublicKey):
            raise ValueError("Only RSA keys are supported")

        numbers = public_key.public_numbers()
        n = _b64url_uint(numbers.n)
        e = _b64url_uint(numbers.e)
        return JWKSToken(kid=kid, n=n, e=e)

    def jwks(self) -> Dict[str, List[Dict]]:
        keys = [
            self._public_pem_to_jwk(kid, pem).model_dump()
            for kid, pem in self.list_public_keys()
        ]
        return {"keys": keys}
