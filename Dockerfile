FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install core dependencies
RUN apt-get update && \
    apt-get install -y \
    python3.10 \
    python3-pip \
    postgresql \
    postgresql-contrib \
    openssh-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Configure SSH
RUN mkdir /var/run/sshd && \
    echo 'root:password' | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd && \
    ssh-keygen -A

# Prepare Flask app
RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt
COPY app /app

EXPOSE 22 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
