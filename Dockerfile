FROM python:3.11-slim

WORKDIR /app

## Install Docker and Docker Compose
#RUN apt-get update && \
#    apt-get install -y \
#    docker.io \
#    curl \
#    && curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose \
#    && chmod +x /usr/local/bin/docker-compose

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install necessary dependencies
RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    ca-certificates

# Add Docker's official GPG key:
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify the installations
RUN which docker && docker --version

# Install dependencies
COPY ./pyproject.toml ./poetry.lock /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main --no-root

# Copy the rest of the code
COPY ./src /app/src
COPY ./README.md /app/README.md
COPY ./docker-http.py /app/docker-http.py

CMD ["python", "/app/docker-http.py"]

EXPOSE 5000