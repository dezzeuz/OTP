#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kredit Pintar OTP Sender - SouGPT Edition
Endpoint:
  - POST /api/auth/login-type
  - POST /api/auth/send-code
"""

import requests
import json
import random
import string
import sys
import uuid

BASE_URL = "https://go.kreditpintar.com/api/auth"

# Headers statis dari contoh
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Accept-Language": "id",
    "x-user-agent": "Pintar-ID-Cash (WebAndroid;;;id) uuid/{} version/0.1.0",
    "x-adv-market-channel": "OfficialWebsite",
    "x-app-version": "APPVERSION_NAME(9999)",
    "x-os-type": "WEB",
    "x-adv-uuid": ""
}

def generate_uuid():
    """Bikin UUID v4 random"""
    return str(uuid.uuid4())

def normalize_phone(raw):
    """Bersihkan nomor HP: hapus spasi, strip leading +, dll"""
    raw = raw.strip().replace(" ", "").replace("-", "")
    return raw

def login_type(session, mobile_raw, uuid_val):
    """POST /login-type"""
    url = f"{BASE_URL}/login-type?channel=OFFICIAL2021&lang=id"
    payload = {
        "captcha": "",
        "mobileNumber": mobile_raw
    }
    headers = HEADERS.copy()
    headers["x-user-agent"] = headers["x-user-agent"].format(uuid_val)
    headers["x-adv-uuid"] = uuid_val

    try:
        r = session.post(url, headers=headers, json=payload, timeout=10)
        print(f"[*] Login-type Status: {r.status_code}")
        print(f"[*] Login-type Response: {r.text[:300]}")
        return r
    except Exception as e:
        print(f"[-] Error login-type: {e}")
        return None

def send_code(session, mobile_raw, uuid_val):
    """POST /send-code"""
    url = f"{BASE_URL}/send-code?channel=OFFICIAL2021&lang=id"
    # Format nomor untuk send-code: +62 + nomor asli (termasuk 0 di depan)
    mobile_with_prefix = "+62" + mobile_raw  # contoh: +62083131378366
    payload = {
        "mobileNumber": mobile_with_prefix,
        "type": "SMS"
    }
    headers = HEADERS.copy()
    headers["x-user-agent"] = headers["x-user-agent"].format(uuid_val)
    headers["x-adv-uuid"] = uuid_val

    try:
        r = session.post(url, headers=headers, json=payload, timeout=10)
        print(f"[*] Send-code Status: {r.status_code}")
        print(f"[*] Send-code Response: {r.text[:300]}")
        return r
    except Exception as e:
        print(f"[-] Error send-code: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("  Kredit Pintar OTP Sender - SouGPT")
    print("=" * 50)

    # Input nomor HP (contoh: 083131378366)
    phone = input("Masukkan nomor HP (format 08...): ").strip()
    phone = normalize_phone(phone)
    if not phone:
        print("[-] Nomor kosong.")
        sys.exit(1)

    # Generate UUID random
    uuid_val = generate_uuid()
    print(f"[*] UUID: {uuid_val}")

    # Sesi
    session = requests.Session()

    # Langkah 1: Login-type
    print("\n[1] Login-type...")
    r1 = login_type(session, phone, uuid_val)
    if not r1 or r1.status_code != 200:
        print("[-] Login-type gagal, berhenti.")
        sys.exit(1)

    # Cek response sukses
    try:
        data = r1.json()
        if data.get("success") is True and data.get("code") == "SUCCESS":
            print("[+] Login-type sukses.")
        else:
            print(f"[-] Login-type gagal: {data}")
            sys.exit(1)
    except:
        print("[-] Response bukan JSON valid.")
        sys.exit(1)

    # Langkah 2: Send-code
    print("\n[2] Send-code...")
    r2 = send_code(session, phone, uuid_val)
    if not r2 or r2.status_code != 200:
        print("[-] Send-code gagal, berhenti.")
        sys.exit(1)

    try:
        data2 = r2.json()
        if "batchNo" in data2:
            print("\n[+] OTP BERHASIL DIKIRIM!")
            print(f"    BatchNo: {data2['batchNo']}")
        else:
            print(f"\n[!] Response tidak sesuai: {r2.text[:300]}")
    except:
        print(f"\n[!] Response bukan JSON, tapi status 200: {r2.text[:300]}")

    print("\nSelesai.")
