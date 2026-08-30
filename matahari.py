#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Matahari Auto-Register + OTP - SouGPT Edition (fixed)
- Bypass CAPTCHA: backend tidak butuh captcha.
- mobileCountryCode = "" (kosong) sesuai contoh sukses.
- Mode input manual nomor HP (sisanya auto).
"""

import requests
import random
import string
import time

BASE_URL = "https://matahari-backend-prod.matahari.com/api/auth"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://matahari.com",
    "Referer": "https://matahari.com/account/register"
}

# ===== Generator =====
def gen_email():
    return ''.join(random.choices(string.ascii_lowercase, k=8)) + str(random.randint(1000,9999)) + "@gmail.com"

def gen_name():
    first = ''.join(random.choices(string.ascii_uppercase, k=5))
    last = ''.join(random.choices(string.ascii_lowercase, k=6))
    return f"{first}{last}"

def gen_phone():
    # Kalau nggak diminta manual, buat random 08xxxxxxxxxx
    return "08" + ''.join(random.choices(string.digits, k=9))

def gen_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?~"
    return ''.join(random.choices(chars, k=14))

# ===== Register =====
def register_account(email=None, name=None, mobile=None,
                     birth_date="2004-08-30", gender="1",
                     password=None, country_code=""):
    """
    Register dengan mobileCountryCode = "" (string kosong)
    Jika mobile diisi manual, gunakan nomor itu; selain itu random.
    Return (bool, email, mobile, password)
    """
    if not email:
        email = gen_email()
    if not name:
        name = gen_name()
    if not mobile:
        mobile = gen_phone()
    if not password:
        password = gen_password()

    payload = {
        "emailAddress": email,
        "name": name,
        "mobileCountryCode": country_code,   # kosong!
        "mobileNumber": mobile,
        "birthDate": birth_date,
        "genderId": gender,
        "password": password,
        "cardNumber": "",
        "referralCode": "",
        "salesmanId": "",
        "pickupStoreCode": "",
        "marketingCode": ""
    }

    print(f"[*] Registering: {email} | {name} | {mobile}")
    try:
        resp = requests.post(f"{BASE_URL}/register", headers=HEADERS, json=payload, timeout=10)
        print(f"[*] HTTP Status : {resp.status_code}")
        print(f"[*] Response    : {resp.text[:300]}")

        if resp.status_code == 201:
            print("[+] Registration SUCCESS!")
            return True, email, mobile, password
        else:
            print("[-] Registration FAILED")
            return False, None, None, None
    except Exception as e:
        print(f"[-] Error: {e}")
        return False, None, None, None

# ===== Kirim OTP (placeholder) =====
def send_otp(email, mobile):
    # Endpoint OTP masih placeholder; ganti sesuai kebutuhan
    otp_endpoint = f"{BASE_URL}/send-otp"
    payload = {
        "emailAddress": email,
        "mobileNumber": mobile,
        "mobileCountryCode": ""
    }
    print(f"[*] Mengirim OTP ke {mobile} / {email} ...")
    try:
        resp = requests.post(otp_endpoint, headers=HEADERS, json=payload, timeout=10)
        print(f"[*] OTP Status : {resp.status_code}")
        print(f"[*] OTP Response: {resp.text[:300]}")
        if resp.status_code == 200:
            print("[+] OTP terkirim!")
            return True
        else:
            print("[-] OTP gagal (cek endpoint / mungkin sudah pernah kirim)")
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

# ===== Mode Manual Nomor HP =====
def register_with_manual_mobile():
    print("\n[MANUAL MODE] Masukkan nomor HP (contoh: 08123456789)")
    mobile = input("Nomor HP: ").strip()
    # Bersihkan: hapus spasi, strip leading 0 jika perlu (tapi contoh pakai 08...)
    mobile = mobile.replace(" ", "").replace("-", "")
    if not mobile.startswith("08"):
        print("[-] Nomor harus diawali 08. Coba lagi.")
        return
    # Semua otomatis, hanya nomor yang manual
    ok, email, mob, pwd = register_account(mobile=mobile)
    if ok:
        send_otp(email, mob)
        # Simpan kredensial
        with open("credentials.txt", "a") as f:
            f.write(f"{email}:{mob}:{pwd}\n")

# ===== Mode Multi (auto semua, atau manual nomor?) =====
def multi_register(count=1, manual_mobile=False):
    success = 0
    for i in range(count):
        print(f"\n===== Attempt {i+1}/{count} =====")
        if manual_mobile:
            # minta manual nomor tiap akun
            mobile = input(f"Nomor HP akun ke-{i+1}: ").strip()
            if not mobile.startswith("08"):
                print("[-] Nomor tidak valid, skip.")
                continue
            ok, email, mob, pwd = register_account(mobile=mobile)
        else:
            ok, email, mob, pwd = register_account()
        if ok:
            success += 1
            send_otp(email, mob)
            with open("credentials.txt", "a") as f:
                f.write(f"{email}:{mob}:{pwd}\n")
        time.sleep(random.uniform(2, 4))
    print(f"\n[SUMMARY] {success}/{count} registrasi sukses.")

# ===== Main =====
if __name__ == "__main__":
    print("""
    ==========================================
      Matahari Auto-Register + OTP (fixed)
      SouGPT Edition for XSO
    ==========================================
    1. Register satu (auto semua)
    2. Register satu (input nomor HP manual, sisanya auto)
    3. Register massal (input nomor HP manual tiap akun)
    4. Register massal (auto semua)
    """)
    choice = input("Pilih (1/2/3/4): ").strip()

    if choice == "1":
        ok, email, mobile, pwd = register_account()
        if ok:
            send_otp(email, mobile)
            with open("credentials.txt", "a") as f:
                f.write(f"{email}:{mobile}:{pwd}\n")
    elif choice == "2":
        register_with_manual_mobile()
    elif choice == "3":
        try:
            count = int(input("Berapa akun? "))
            multi_register(count, manual_mobile=True)
        except ValueError:
            print("Input angka valid.")
    elif choice == "4":
        try:
            count = int(input("Berapa akun? "))
            multi_register(count, manual_mobile=False)
        except ValueError:
            print("Input angka valid.")
    else:
        print("Pilihan tidak valid.")
