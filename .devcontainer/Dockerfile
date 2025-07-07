FROM ubuntu:22.04

# نصب پیش‌نیازها
RUN apt-get update && apt-get install -y \
    python3 \
    openssh-server \
    net-tools \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

# تنظیم SSH
RUN mkdir -p /var/run/sshd && chmod 755 /var/run/sshd
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
RUN echo 'Port 1080' >> /etc/ssh/sshd_config

# تنظیم پسورد برای کاربر root
RUN echo 'root:MySecurePass123!' | chpasswd  # جای MySecurePass123! پسورد امن خودت رو بذار

# تولید کلیدهای SSH برای سرور
RUN ssh-keygen -A

# باز کردن پورت SSH
EXPOSE 1080

# اجرای سرور SSH
CMD ["/usr/sbin/sshd", "-D", "-p", "1080"]