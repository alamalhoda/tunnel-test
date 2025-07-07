#!/usr/bin/env python3

import subprocess
import os
import sys
import socket
import signal
import time

### 🧩 تنظیمات اولیه
CONFIG = {
    "SERVER_IP": "your-server-ip",  # آدرس سرور (مثل IP سرور Oracle Cloud)
    "SSH_USER": "ubuntu",           # کاربر SSH (ترجیحاً غیر root مثل ubuntu)
    "SSH_PORT": "22",               # پورت SSH
    "SSH_KEY": "~/.ssh/oracle_key", # مسیر کلید SSH
    "ROUTE_MODE": "custom",         # "all" یا "custom"
    "INCLUDE_DOMAINS": ["api2.cursor.sh", "api.anthropic.com"],  # مقصدهای تونل
    "LOCAL_NET": "192.168.1.0/24",  # شبکه محلی برای مستثنی کردن
    "LOG_FILE": "/tmp/sshuttle.log" # مسیر فایل لاگ
}

### 🚩 بررسی پیش‌نیازها
def check_prerequisites():
    print("⏳ بررسی پیش‌نیازها...")
    
    # بررسی نصب sshuttle
    if subprocess.run(["which", "sshuttle"], capture_output=True).returncode != 0:
        print("❗️ sshuttle نصب نیست. لطفاً نصب کنید: brew install sshuttle")
        sys.exit(1)
    
    # بررسی نصب autossh
    if subprocess.run(["which", "autossh"], capture_output=True).returncode != 0:
        print("❗️ autossh نصب نیست. لطفاً نصب کنید: brew install autossh")
        sys.exit(1)
    
    # بررسی دسترسی به سرور و نصب Python
    ssh_cmd = ["ssh", "-i", os.path.expanduser(CONFIG["SSH_KEY"]), "-p", CONFIG["SSH_PORT"],
               f"{CONFIG['SSH_USER']}@{CONFIG['SERVER_IP']}", "python3 --version"]
    try:
        subprocess.run(ssh_cmd, capture_output=True, check=True, timeout=10)
    except subprocess.SubprocessError:
        print("❗️ سرور در دسترس نیست یا Python نصب نیست! لطفاً سرور را بررسی کنید.")
        sys.exit(1)

### 🔧 رفع دامنه‌های پویا
def resolve_domains(domains):
    resolved = []
    for dest in domains:
        if dest.replace(".", "").isdigit():  # اگر IP است
            resolved.append(dest)
        else:  # اگر دامنه است
            try:
                ip = socket.gethostbyname(dest)
                resolved.append(ip)
            except socket.gaierror:
                print(f"❗️ نمی‌توان IP برای {dest} را پیدا کرد!")
                sys.exit(1)
    return resolved

### 🟢 اجرای sshuttle
def start_sshuttle():
    print(f"⏳ در حال اتصال به سرور {CONFIG['SERVER_IP']} ...")
    print(f"📝 لاگ‌ها در {CONFIG['LOG_FILE']} ذخیره می‌شوند.")

    ssh_cmd = f"autossh -M 0 -i {os.path.expanduser(CONFIG['SSH_KEY'])} -p {CONFIG['SSH_PORT']}"
    cmd = ["sshuttle", "-r", f"{CONFIG['SSH_USER']}@{CONFIG['SERVER_IP']}", 
           "--ssh-cmd", ssh_cmd, "--dns", "--exclude", CONFIG["LOCAL_NET"], 
           "--daemon", "--verbose"]

    if CONFIG["ROUTE_MODE"] == "all":
        cmd.append("0.0.0.0/0")
    else:
        resolved_domains = resolve_domains(CONFIG["INCLUDE_DOMAINS"])
        cmd.extend(resolved_domains)

    with open(CONFIG["LOG_FILE"], "a") as log_file:
        process = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
    
    time.sleep(2)  # منتظر می‌مونه تا پروسه شروع بشه
    if process.poll() is not None:
        print(f"❗️ خطا در راه‌اندازی sshuttle! لاگ‌ها را بررسی کنید: {CONFIG['LOG_FILE']}")
        sys.exit(1)
    
    print(f"✅ اتصال برقرار شد! (PID: {process.pid})")
    print(f"📜 برای بررسی لاگ‌ها: tail -f {CONFIG['LOG_FILE']}")
    print("🛑 برای قطع اتصال Ctrl+C را بزنید...")
    return process.pid

### 🔴 توقف sshuttle
def cleanup(signum=None, frame=None):
    print("\n⏹ توقف sshuttle و بازگردانی تنظیمات...")
    subprocess.run(["pkill", "-f", "sshuttle"])
    print("✅ پاکسازی انجام شد.")
    sys.exit(0)

### 🧼 مدیریت سیگنال‌ها
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

### ▶️ اجرای اصلی
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❗️ لطفاً اسکریپت را با sudo اجرا کنید: sudo python3 tunnel.py")
        sys.exit(1)
    
    check_prerequisites()
    pid = start_sshuttle()
    try:
        subprocess.run(["wait", str(pid)], check=True)
    except subprocess.SubprocessError:
        cleanup()