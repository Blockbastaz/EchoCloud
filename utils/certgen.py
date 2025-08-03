import os
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

def generate_self_signed_cert(cert_path: Path =Path("./config/cert.pem"), key_path: Path =Path("./config/key.pem"), host: str = u"localhost", cert_duration_days: int = 365):

    if cert_path.exists() and key_path.exists():
        return str(cert_path), str(key_path)

    # Key generieren
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"DE"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"EchoCloud"),
        x509.NameAttribute(NameOID.COMMON_NAME, host),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=cert_duration_days))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(host)]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    return str(cert_path), str(key_path)
