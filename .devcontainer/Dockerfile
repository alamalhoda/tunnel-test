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
RUN echo 'Port 2222' >> /etc/ssh/sshd_config

# تنظیم پسورد برای کاربر root
RUN echo 'root:!MySecPass123' | chpasswd  # جای your_secure_password پسورد امن بذار

# تولید کلیدهای SSH برای سرور
RUN ssh-keygen -A

# باز کردن پورت SSH
EXPOSE 2222

# اجرای سرور SSH
CMD ["/usr/sbin/sshd", "-D", "-p", "2222"]