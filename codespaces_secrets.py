import os
import requests
from nacl import public, encoding
import json



GITHUB_API_URL = "https://api.github.com"

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypts a Unicode string value using a Base64-encoded public key."""
    public_key_bytes = public_key.encode("utf-8")
    sealed_box = public.SealedBox(public.PublicKey(public_key_bytes, encoder=encoding.Base64Encoder))
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return encoding.Base64Encoder.encode(encrypted).decode("utf-8")

def update_secret(SECRET_NAME, SECRET_VALUE):
    GITHUB_TOKEN = os.getenv("GH_TOKEN")
    GITHUB_REPO_OWNER = os.getenv("GH_REPO_OWNER")
    GITHUB_REPO_NAME = os.getenv("GH_REPO_NAME")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    public_key_url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/codespaces/secrets/public-key"

    response = requests.get(public_key_url, headers=headers)

    public_key_data = response.json()
    key_id = public_key_data["key_id"]
    key_value = public_key_data["key"]

    encrypted_value = encrypt_secret(key_value, SECRET_VALUE)

    update_secret_url = f"{GITHUB_API_URL}/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/codespaces/secrets/{SECRET_NAME}"

    payload = {
        "encrypted_value": encrypted_value,
        "key_id": key_id,
    }

    response = requests.put(update_secret_url, headers=headers, json=payload)