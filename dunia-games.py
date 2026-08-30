#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duniagames OTP Sender - SouGPT Edition
- Mengirim OTP ke nomor HP via API Duniagames.
- Mengembalikan authId (JWT) yang diperlukan untuk verifikasi.
- Endpoint: POST https://api.duniagames.co.id/api/user/api/v2/user/send-otp
"""

import requests
import json
import random
import string
import time
import sys

# ================= KONFIGURASI =================
BASE_URL = "https://api.duniagames.co.id/api/user/api/v2/user"
OTP_ENDPOINT = f"{BASE_URL}/send-otp"

# Header wajib (dari contoh request)
HEADERS = {
    "Accept-Language": "id",
    "x-device": "3c8c0a10-43fe-40d6-8881-6b8ebbd0ac55",  # bisa diganti random? tapi contoh pakai ini
    "Ciam-Type": "FR",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin": "https://www.duniagames.co.id",
    "Referer": "https://www.duniagames.co.id/"
}

# ================= FUNGSI GENERATE =================
def generate_device_id():
    """Bikin device ID random (UUID) kalau mau beda-beda"""
    return str(random.randint(10**11, 10**12 - 1))  # 12 digit, asal unik

# ================= KIRIM OTP =================
def send_otp(phone_number):
    """
    Kirim OTP ke nomor HP.
    phone_number harus format internasional, contoh: +6283131378366
    Return (success, authId, message)
    """
    # Bersihkan nomor: hapus spasi, strip leading 0, pastikan ada +62
    clean = phone_number.replace(" ", "").replace("-", "")
    if not clean.startswith("+"):
        if clean.startswith("0"):
            clean = "+62" + clean[1:]  # 08... -> +628...
        elif clean.startswith("62"):
            clean = "+" + clean
        else:
            clean = "+62" + clean  # fallback

    # userName = nomor tanpa + (contoh: 083131378366)
    # phoneNumber = dengan + (contoh: +6283131378366)
    payload = {
        "phoneNumber": clean,
        "userName": clean.replace("+", "")
    }

    print(f"[*] Mengirim OTP ke {clean} ...")
    try:
        resp = requests.post(OTP_ENDPOINT, headers=HEADERS, json=payload, timeout=10)
        print(f"[*] HTTP Status : {resp.status_code}")
        print(f"[*] Response    : {resp.text[:500]}")

        if resp.status_code == 200:
            data = resp.json()
            if data.get("status", {}).get("code") == 0:
                print("[+] OTP terkirim!")
                # Ambil authId dari response
                auth_id = data.get("data", {}).get("authId", "")
                if auth_id:
                    print(f"[+] authId: {auth_id[:60]}...")
                    return True, auth_id, data["status"]["message"]
                else:
                    print("[!] Tidak ada authId dalam response")
                    return True, None, data["status"]["message"]
            else:
                print(f"[-] Gagal: {data.get('status', {}).get('message', 'Unknown')}")
                return False, None, data.get("status", {}).get("message", "Unknown")
        else:
            print("[-] HTTP error")
            return False, None, f"HTTP {resp.status_code}"
    except Exception as e:
        print(f"[-] Exception: {e}")
        return False, None, str(e)

# ================= VERIFIKASI OTP (dummy, perlu endpoint) =================
def verify_otp(auth_id, otp_code):
    """
    Endpoint verifikasi belum diketahui. Ini hanya placeholder.
    Jika lo nemu endpoint verifikasi, ganti di sini.
    """
    verify_endpoint = f"{BASE_URL}/verify-otp"  # <-- GANTI dengan endpoint asli
    payload = {
        "authId": auth_id,
        "otp": otp_code
    }
    print(f"[*] Verifikasi OTP {otp_code} ...")
    try:
        resp = requests.post(verify_endpoint, headers=HEADERS, json=payload, timeout=10)
        print(f"[*] Verify Status : {resp.status_code}")
        print(f"[*] Verify Response: {resp.text[:500]}")
        if resp.status_code == 200:
            print("[+] Verifikasi sukses!")
            return True
        else:
            print("[-] Verifikasi gagal")
            return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

# ================= MAIN =================
if __name__ == "__main__":
    print("""
    ==========================================
      Duniagames OTP Sender - SouGPT
    ==========================================
    1. Kirim OTP (input nomor manual)
    2. Kirim OTP (nomor random - tidak disarankan)
    3. Verifikasi OTP (butuh authId + kode)
    """)
    choice = input("Pilih (1/2/3): ").strip()

    if choice == "1":
        phone = input("Masukkan nomor HP (contoh: 08123456789 atau +628123456789): ").strip()
        success, auth_id, msg = send_otp(phone)
        if success and auth_id:
            # Simpan authId ke file
            with open("duniagames_auth.txt", "a") as f:
                f.write(f"{phone} | {auth_id}\n")
            print(f"[*] authId disimpan ke duniagames_auth.txt")
    elif choice == "2":
        # Buat nomor random Indonesia
        phone = "+628" + ''.join(random.choices(string.digits, k=9))
        print(f"[!] Nomor random: {phone}")
        send_otp(phone)
    elif choice == "3":
        auth_id = input("Masukkan authId: ").strip()
        otp = input("Masukkan kode OTP: ").strip()
        verify_otp(auth_id, otp)
    else:
        print("Pilihan tidak valid.")
