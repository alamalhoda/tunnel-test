# مستند راه‌اندازی GitHub Codespaces برای تست اسکریپت `tunnel.py`

## شرح مشکل
برنامه‌هایی مثل **Cursor** هنگام اتصال به سرورهایشان (مثل `api2.cursor.sh` یا `api.anthropic.com`) با خطای `HTTP 403 [permission_denied]` مواجه می‌شن، چون IP سرور بلاک شده. **تلگرام** برای پیام‌ها و دانلودها (TCP) و تماس‌های صوتی/تصویری (UDP) و **VSCode** برای افزونه‌ها و GitHub Copilot نیاز به IP تمیز دارن. ثبت‌نام در سرویس‌های VPS مثل Oracle Cloud برای کاربران ایرانی به دلیل نیاز به شماره تلفن و کارت اعتباری سخت شده. این مستند توضیح می‌ده چطور از **GitHub Codespaces** به‌عنوان سرور موقت SSH برای تست اسکریپت `tunnel.py` استفاده کنی.

## راه‌حل
GitHub Codespaces یه محیط توسعه ابری مبتنی بر Ubuntu ارائه می‌ده که می‌تونه به‌عنوان سرور SSH موقت عمل کنه. با ایجاد یه ریپوزیتوری GitHub شامل `Dockerfile`، `devcontainer.json`، و تنظیم SSH، می‌تونی `tunnel.py` رو تست کنی. این روش نیازی به شماره تلفن یا کارت اعتباری نداره و برای کاربران ایرانی مناسبه.

### قابلیت‌های اسکریپت `tunnel.py`
- هدایت ترافیک TCP و DNS از طریق Codespaces.
- پشتیبانی از حالت `all` (کل ترافیک) یا `custom` (دامنه‌های خاص مثل `api2.cursor.sh` و `api.anthropic.com`).
- مستثنی کردن شبکه محلی (مثل `192.168.1.0/24`) با `--exclude`.
- پایداری اتصال با `autossh`.
- ذخیره لاگ‌ها در `/tmp/sshuttle.log`.
- برای تماس‌های تلگرام (UDP)، نیاز به تونل SOCKS5 یا Socat جداگانه.

## پیش‌نیازها
### روی کلاینت (macOS)
- **سیستم‌عامل**: macOS (تست‌شده روی Ventura و بالاتر). لینوکس یا ویندوز (با WSL) هم کار می‌کنه.
- **ابزارها**:
  - `Python 3`: برای اجرای `tunnel.py`.
  - `sshuttle`: برای هدایت ترافیک.
  - `autossh`: برای پایداری اتصال SSH.
  - `dig` (اختیاری): برای پیدا کردن IP Codespace.
- **دسترسی ادمین**: برای اجرای اسکریپت با `sudo`.
- **حساب GitHub**: برای دسترسی به Codespaces (طرح رایگان: 120 هسته‌ساعت در ماه).

### روی سرور (GitHub Codespaces)
- **محیط**: Codespaces مبتنی بر Ubuntu.
- **ابزارها**:
  - `Python 3`: برای اجرای کد sshuttle.
  - `openssh-server`: برای فعال کردن SSH.
- **دسترسی SSH**: با کلید SSH که تولید می‌کنی.

## نحوه نصب پیش‌نیازها
### روی کلاینت (macOS)
1. **نصب Homebrew** (اگر نصب نیست):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **نصب Python، sshuttle، autossh، و dig**:
   ```bash
   brew install python3 sshuttle autossh bind-tools
   ```
3. **بررسی نصب**:
   ```bash
   python3 --version
   sshuttle --version
   autossh --version
   dig -v
   ```

### روی سرور (Codespaces)
پیش‌نیازها از طریق `Dockerfile` در ریپوزیتوری نصب می‌شن (در بخش راه‌اندازی).

## نحوه راه‌اندازی و اجرا
### 1. ایجاد ریپوزیتوری GitHub
1. به [GitHub](https://github.com) برو و یه حساب بساز (یا وارد شو).
2. یه ریپوزیتوری جدید (مثل `tunnel-test`) بساز.
3. ساختار زیر رو ایجاد کن:
   ```
   tunnel-test/
   ├── .devcontainer/
   │   ├── Dockerfile
   │   ├── devcontainer.json
   │   ├── authorized_keys
   ├── tunnel.py
   ```

#### `Dockerfile`
```dockerfile
FROM ubuntu:22.04

# نصب پیش‌نیازها
RUN apt-get update && apt-get install -y \
    python3 \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# تنظیم SSH
RUN mkdir /var/run/sshd
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
RUN echo 'Port 2222' >> /etc/ssh/sshd_config

# تولید کلیدهای SSH برای سرور
RUN ssh-keygen -A

# کپی کلید عمومی کاربر
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
COPY authorized_keys /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# باز کردن پورت SSH
EXPOSE 2222

# اجرای سرور SSH
CMD ["/usr/sbin/sshd", "-D", "-p", "2222"]
```

#### `.devcontainer/devcontainer.json`
```json
{
  "name": "Tunnel Test",
  "build": {
    "dockerfile": "Dockerfile",
    "context": "."
  },
  "forwardPorts": [2222],
  "postCreateCommand": "echo 'Codespace آماده است!' && /usr/sbin/sshd -p 2222",
  "runArgs": ["--cap-add=NET_ADMIN", "--security-opt", "seccomp=unconfined"]
}
```
**توضیحات**:
- `"dockerfile": "Dockerfile"`: به Codespaces می‌گه از `Dockerfile` توی `.devcontainer` استفاده کنه.
- `"forwardPorts": [2222]`: پورت 2222 رو برای SSH باز می‌کنه.
- `"postCreateCommand"`: بعد از build، سرور SSH رو اجرا می‌کنه.
- `"runArgs"`: دسترسی‌های لازم برای sshuttle (NET_ADMIN) و اجرای بدون محدودیت seccomp.

#### `authorized_keys`
1. کلید SSH تولید کن:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/codespace_key
   ```
2. محتوای `~/.ssh/codespace_key.pub` رو کپی کن:
   ```bash
   cat ~/.ssh/codespace_key.pub
   ```
3. یه فایل `authorized_keys` توی `.devcontainer` بساز و محتوای کلید عمومی رو توش بذار.

#### `tunnel.py`
فایل `tunnel.py` رو از مستند قبلی کپی کن و تنظیمات `CONFIG` رو ویرایش کن:
```python
CONFIG = {
    "SERVER_IP": "your-codespace-ip",  # بعداً با IP Codespace جایگزین می‌شه
    "SSH_USER": "root",                # کاربر root برای سادگی
    "SSH_PORT": "2222",                # پورت SSH
    "SSH_KEY": "~/.ssh/codespace_key", # مسیر کلید SSH
    "ROUTE_MODE": "custom",
    "INCLUDE_DOMAINS": ["api2.cursor.sh", "api.anthropic.com"],
    "LOCAL_NET": "192.168.1.0/24",
    "LOG_FILE": "/tmp/sshuttle.log"
}
```

4. فایل‌ها رو commit و push کن:
   ```bash
   git add .
   git commit -m "Setup Codespaces for tunnel.py"
   git push origin main
   ```

### 2. راه‌اندازی Codespaces
1. تو GitHub، به ریپوزیتوری برو.
2. روی **Code** کلیک کن و تب **Codespaces** رو انتخاب کن.
3. روی **Create Codespace on main** کلیک کن.
4. صبر کن تا Codespace ساخته بشه (چند دقیقه طول می‌کشه).

### 3. تنظیم SSH در Codespaces
1. تو Codespace، چک کن که `sshd` اجرا شده:
   ```bash
   ps aux | grep sshd
   ```
2. اگه اجرا نشده، دستی راه‌اندازیش کن:
   ```bash
   sudo /usr/sbin/sshd -p 2222
   ```
3. IP عمومی Codespace رو پیدا کن:
   - تو VS Code، تب **Ports** رو باز کن.
   - آدرس پورت 2222 (مثل `x-x-x-x-2222.app.github.dev`) رو کپی کن.
   - IP رو با `dig` پیدا کن:
     ```bash
     dig +short x-x-x-x-2222.app.github.dev
     ```
     (مثلاً `185.199.x.x`).

### 4. ویرایش و اجرای `tunnel.py`
1. تو سیستم خودت (macOS)، `SERVER_IP` رو در `tunnel.py` با IP Codespace جایگزین کن:
   ```python
   "SERVER_IP": "185.199.x.x"
   ```
2. اسکریپت رو اجرا کن:
   ```bash
   chmod +x tunnel.py
   sudo python3 tunnel.py
   ```

### 5. تست
- **Cursor**:
  - قابلیت هوش مصنوعی رو تست کن:
    ```bash
    open -a Cursor
    # در Cursor: Help > Toggle Developer Tools > Console
    ```
- **تلگرام**:
  - پیام‌ها و دانلودها رو تست کن (TCP).
  - برای تماس‌های صوتی/تصویری (UDP):
    ```bash
    autossh -M 0 -D 1080 root@your-codespace-ip -p 2222 -i ~/.ssh/codespace_key
    sudo socat UDP4-LISTEN:8443,fork,range=127.0.0.1/32 PROXY:127.0.0.1:127.0.0.1:443,proxyport=1080
    ```
    در تلگرام، پراکسی رو به `127.0.0.1:8443` تنظیم کن.
- **VSCode**:
  - افزونه‌ها و Copilot رو تست کن.
- **IP**:
  ```bash
  curl https://ifconfig.me
  ```
  باید IP Codespace رو نشون بده.
- **API Cursor**:
  ```bash
  curl https://api2.cursor.sh
  ```
- **لاگ‌ها**:
  ```bash
  tail -f /tmp/sshuttle.log
  ```

## نحوه خطایابی
1. **خطای build در Codespaces**:
   - **مشکل**: `Dockerfile not found` یا `Failed to build container`.
   - **راه‌حل**: مطمئن شو `Dockerfile` توی `.devcontainer`ه و تو `devcontainer.json` درست اشاره شده:
     ```json
     "dockerfile": "Dockerfile"
     ```
   - لاگ‌های build رو تو VS Code (تب Output) یا GitHub (Actions) چک کن.
2. **مشکل نصب پکیج‌ها**:
   - **مشکل**: خطاهایی مثل `E: Unable to locate package`.
   - **راه‌حل**: مطمئن شو `apt-get update` قبل از `apt-get install` تو `Dockerfile`ه.
3. **مشکل SSH**:
   - **مشکل**: `Connection refused` یا `Permission denied`.
   - **راه‌حل**:
     - چک کن `sshd` اجرا شده:
       ```bash
       ps aux | grep sshd
       ```
     - مطمئن شو فایل `authorized_keys` درست کپی شده و دسترسی‌ها تنظیمه:
       ```bash
       ls -l /root/.ssh/authorized_keys
       ```
     - تست اتصال SSH:
       ```bash
       ssh -i ~/.ssh/codespace_key -p 2222 root@your-codespace-ip
       ```
4. **خطای 403 در Cursor**:
   - لاگ‌های Cursor رو چک کن:
     ```bash
     open -a Cursor
     # در Cursor: Help > Toggle Developer Tools > Console
     ```
   - تست با `curl`:
     ```bash
     curl https://api2.cursor.sh
     ```
     اگر 403 گرفتی، Codespace جدید بساز تا IP جدید بگیری.
5. **خطای sshuttle**:
   - لاگ‌ها رو چک کن:
     ```bash
     tail -f /tmp/sshuttle.log
     ```
   - تست دستی:
     ```bash
     sudo sshuttle -vvv -r root@your-codespace-ip:2222 0.0.0.0/0
     ```

## نحوه توقف
1. **توقف اسکریپت**:
   - Ctrl+C بزن تا تابع `cleanup` در `tunnel.py` اجرا بشه.
2. **توقف دستی**:
   ```bash
   sudo pkill -f sshuttle
   ```
3. **توقف Codespace**:
   - تو GitHub، به تب **Codespaces** برو و **Stop Codespace** رو بزن.
   - یا تو VS Code، از منوی Codespaces گزینه **Stop** رو انتخاب کن.

## نکات اضافی
- **IP پویا**: IP Codespaces با هر بار راه‌اندازی تغییر می‌کنه. بعد از هر استارت، IP رو با `dig` به‌روز کن.
- **محدودیت‌های Codespaces**:
  - برای تست کوتاه‌مدت عالیه، ولی برای استفاده دائمی، VPSهایی مثل Google Cloud یا Hetzner پایدارترن.
  - طرح رایگان تا 120 هسته‌ساعت در ماه کافیه.
- **تماس‌های تلگرام**: برای UDP، از Socat/SOCKS5 جداگانه استفاده کن.
- **امنیت**: کلید SSH رو امن نگه دار و پورت 2222 رو فقط برای خودت باز نگه دار.