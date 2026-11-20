

FROM python:3.12-slim

# Install SSH client, Docker CLI, and system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    sshpass \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Ansible
RUN pip install --no-cache-dir ansible

# Create working directory
WORKDIR /ansible

# Default command
CMD ["ansible", "--version"]
