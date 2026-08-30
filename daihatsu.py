#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astra Daihatsu OTP Auto - SouGPT Edition
Hanya butuh input nomor HP, sisanya otomatis.
"""

import requests
import re
import random
import string
import sys
import time

BASE = "https://www.astra-daihatsu.id"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": BASE,
    "Referer": BASE + "/register",
    "X-Requested-With": "XMLHttpRequest"
}

def get_csrf_token(session):
    """Ambil CSRF token dari halaman /register"""
    try:
        r = session.get(BASE + "/register", headers=HEADERS, timeout=10)
        html = r.text
        # Meta tag csrf-token
        m = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', html, re.I)
        if m:
            return m.group(1)
        # Input hidden name="CSRFToken"
        m = re.search(r'name="CSRFToken"\s+value="([^"]+)"', html, re.I)
        if m:
            return m.group(1)
        # Cookie XSRF-TOKEN (URL-encoded)
        if 'XSRF-TOKEN' in session.cookies.get_dict():
            from urllib.parse import unquote
            return unquote(session.cookies.get('XSRF-TOKEN'))
        return None
    except Exception as e:
        print(f"[-] Gagal ambil CSRF: {e}")
        return None

def generate_email():
    """Bikin email random"""
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}{random.randint(1000,9999)}@gmail.com"

def normalize_phone(phone):
    """Normalisasi nomor HP"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        phone_no = phone.replace("+", "")
        phone_full = phone
    elif phone.startswith("62"):
        phone_no = phone
        phone_full = "+" + phone
    elif phone.startswith("0"):
        phone_no = "62" + phone[1:]
        phone_full = "+62" + phone[1:]
    else:
        phone_no = "62" + phone
        phone_full = "+62" + phone
    return phone_full, phone_no

def validate_pre_register(session, email, phone, csrf):
    data = {
        "email": email,
        "phoneNumber": phone,
        "CSRFToken": csrf
    }
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    try:
        r = session.post(BASE + "/register/validate-pre-register",
                         data=data,
                         headers=headers,
                         timeout=10)
        return r
    except Exception as e:
        print(f"[-] Error validate: {e}")
        return None

def generate_otp(session, phone_no, csrf):
    payload = {"phoneNo": phone_no}
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json; charset=utf-8"
    headers["CSRFToken"] = csrf
    try:
        r = session.post(BASE + "/otp/whatsapp/generate",
                         json=payload,
                         headers=headers,
                         timeout=10)
        return r
    except Exception as e:
        print(f"[-] Error OTP: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("  Astra Daihatsu OTP Auto - SouGPT")
    print("=" * 50)
    
    # 1. Ambil CSRF token
    session = requests.Session()
    csrf = get_csrf_token(session)
    if not csrf:
        print("[-] Tidak dapat CSRF token otomatis. Coba buka situs dan ambil manual.")
        sys.exit(1)
    print(f"[+] CSRF token: {csrf}")

    # 2. Input nomor HP
    phone_input = input("Masukkan nomor HP (08/62/+62): ").strip()
    phone_full, phone_no = normalize_phone(phone_input)
    print(f"[*] Nomor full : {phone_full}")
    print(f"[*] Nomor OTP  : {phone_no}")

    # 3. Generate email random
    email = generate_email()
    print(f"[*] Email      : {email}")

    # 4. Validasi pre-register
    print("\n[1] Validasi pre-register...")
    r = validate_pre_register(session, email, phone_full, csrf)
    if not r or r.status_code != 200:
        print("[-] Validasi gagal, berhenti.")
        sys.exit(1)
    resp = r.json()
    if resp.get("errorMessage"):
        print(f"[-] Error: {resp['errorMessage']}")
        sys.exit(1)
    print("[+] Validasi sukses.")

    # 5. Generate OTP
    print("\n[2] Generate OTP...")
    r = generate_otp(session, phone_no, csrf)
    if not r or r.status_code != 200:
        print("[-] Generate OTP gagal.")
        sys.exit(1)
    data = r.json()
    if data.get("acknowledge") == 1:
        print("\n[+] OTP BERHASIL DIKIRIM!")
        print(f"    Message : {data.get('message')}")
        print(f"    Sisa percobaan: {data.get('remainingAttempt')}")
    else:
        print("\n[!] Response tidak sesuai, cek manual.")
        print(f"    {r.text[:300]}")

    print("\nSelesai.")
