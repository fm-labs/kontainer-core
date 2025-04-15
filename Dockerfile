FROM python:3.13-slim

ENV KONTAINER_HOST=0.0.0.0
ENV KONTAINER_PORT=5000

# Update package list and install necessary dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    ca-certificates \
    nginx \
    redis-server \
    supervisor \
    openssl

# Add Docker's official GPG key:
RUN install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository to Apt sources:
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/archives/*

# Verify Docker installation
#RUN which docker && docker --version

WORKDIR /app

# Install python dependencies
COPY ./pyproject.toml ./poetry.lock /app/
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# Copy the rest of the code
COPY ./src /app/src
COPY ./agent.py /app/agent.py
COPY ./celery_worker.sh /app/celery_worker.sh

# Configure Nginx
COPY ./docker/nginx/conf.d/ /etc/nginx/conf.d/
COPY ./docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./docker/nginx/site.default.conf /etc/nginx/sites-available/default

# Configure Supervisor
COPY docker/supervisor/celery_worker.ini /etc/supervisor/conf.d/celery_worker.conf

# Entry point
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN ["chmod", "+x", "/entrypoint.sh"]
ENTRYPOINT ["/entrypoint.sh"]
CMD ["devserver"]

# Health check
HEALTHCHECK --interval=60s --timeout=3s --retries=3 \
 CMD curl --fail http://localhost:${KONTAINER_PORT}/ || exit 1


EXPOSE ${KONTAINER_PORT}
EXPOSE 80
EXPOSE 443