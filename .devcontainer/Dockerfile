FROM ubuntu:22.04

# نصب پیش‌نیازها
RUN apt-get update && apt-get install -y \
    python3 \
    openssh-server \
    net-tools \
    rsyslog \
    && rm -rf /var/lib/apt/lists/*

# تنظیم SSH
RUN mkdir -p /var/run/sshd && chmod 755 /var/run/sshd
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config
RUN echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config
RUN echo 'Port 2222' >> /etc/ssh/sshd_config

# تولید کلیدهای SSH برای سرور
RUN ssh-keygen -A

# کپی کلید عمومی کاربر
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
COPY authorized_keys /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

# فعال کردن rsyslog برای لاگ‌ها
RUN service rsyslog start

# باز کردن پورت SSH
EXPOSE 2222

# اجرای سرور SSH
CMD ["/usr/sbin/sshd", "-D", "-p", "2222"]