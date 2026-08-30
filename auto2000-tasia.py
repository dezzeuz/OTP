#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto2000 OTP Generator - SouGPT Edition
Endpoint:
  - POST /api/customer/v1/saphybris/whatsapp/generate-otp
  - GET  /api/system-authentication
"""

import requests
import sys
import json

BASE = "https://auto2000.co.id"

# Headers umum
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

def get_system_token(session):
    """Ambil token dari /api/system-authentication"""
    try:
        r = session.get(BASE + "/api/system-authentication", headers=HEADERS, timeout=10)
        print(f"[*] System-auth Status: {r.status_code}")
        print(f"[*] System-auth Response: {r.text[:300]}")
        if r.status_code == 200:
            data = r.json()
            return data.get("token", "")
        return ""
    except Exception as e:
        print(f"[-] Error getting system token: {e}")
        return ""

def generate_otp(session, phone, is_login):
    """Kirim OTP ke WhatsApp"""
    url = BASE + "/api/customer/v1/saphybris/whatsapp/generate-otp"
    
    # Payload sesuai contoh
    payload = {
        "phoneNumber": phone,
        "isCheckOtpLimit": True,
        "uniqueID": phone,
        "isLogin": is_login
    }
    # Saat login=true, ada field dacUnicode (bisa kosong)
    if is_login:
        payload["dacUnicode"] = ""
    
    headers = HEADERS.copy()
    # Opsional: sertakan token jika didapat
    token = get_system_token(session)
    if token:
        headers["Authorization"] = f"Bearer {token}"  # Bisa jadi tidak perlu, tapi kita coba

    try:
        r = session.post(url, headers=headers, json=payload, timeout=10)
        print(f"[*] OTP Status: {r.status_code}")
        print(f"[*] OTP Response: {r.text[:300]}")
        return r
    except Exception as e:
        print(f"[-] Error generating OTP: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("  Auto2000 OTP Generator - SouGPT")
    print("=" * 50)
    
    session = requests.Session()
    
    # Input nomor HP
    phone = input("Masukkan nomor HP (format 08...): ").strip()
    if not phone:
        print("[-] Nomor kosong.")
        sys.exit(1)
    
    # Pilih mode
    print("\nPilih mode:")
    print("1. Login (isLogin=true)")
    print("2. Registrasi (isLogin=false)")
    mode = input("Pilih (1/2): ").strip()
    is_login = True if mode == "1" else False
    
    # Generate OTP
    print(f"\n[+] Mengirim OTP untuk {phone} (isLogin={is_login})...")
    r = generate_otp(session, phone, is_login)
    if not r:
        print("[-] Gagal, tidak ada respons.")
        sys.exit(1)
    
    try:
        data = r.json()
        if data.get("acknowledge") == 1:
            print("\n[+] OTP BERHASIL DIKIRIM!")
            print(f"    Message: {data.get('message')}")
            print(f"    nextValidAttempt (detik): {data.get('nextValidAttempt')}")
        elif data.get("message") == "Customer doesn't exist":
            print("\n[!] Customer tidak ditemukan. Coba mode registrasi (isLogin=false).")
        else:
            print(f"\n[!] Response tidak sesuai: {r.text[:300]}")
    except:
        print(f"\n[!] Response bukan JSON: {r.text[:300]}")
    
    print("\nSelesai.")
