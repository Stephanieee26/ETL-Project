FROM apache/airflow:2.7.1

WORKDIR /airflow_docker

ADD . /airflow_docker

COPY pyproject.toml poetry.lock /airflow_docker/

# Install poetry and project dependencies
RUN pip install --user --upgrade pip \
    && pip install --user poetry \
    && mkdir -p /home/airflow/.cache/pypoetry/virtualenvs \
    && poetry config virtualenvs.in-project true \
    && poetry config virtualenvs.path /home/airflow/.cache/pypoetry/virtualenvs \
    && poetry install --no-root --no-dev --no-interaction --no-ansi


RUN mkdir downloads
# Installing the GCP CLI in the container
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

USER 0
ARG CLOUD_SDK_VERSION=322.0.0
ENV GCLOUD_HOME=/home/google-cloud-sdk
ENV PYTHONPATH=$PYTHONPATH:${AIRFLOW_USER_HOME}
ENV PATH="${GCLOUD_HOME}/bin/:${PATH}"

# Install Python 3.9 (or another version you need)
RUN apt-get update \
    && apt-get install -y python3.9 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 \
    && update-alternatives --config python3 \
    && rm -rf /var/lib/apt/lists/*

# Continue with the rest of your Dockerfile...
RUN DOWNLOAD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${CLOUD_SDK_VERSION}-linux-x86_64.tar.gz" \
    && TMP_DIR="$(mktemp -d)" \
    && curl -fL "${DOWNLOAD_URL}" --output "${TMP_DIR}/google-cloud-sdk.tar.gz" \
    && mkdir -p "${GCLOUD_HOME}" \
    && tar xzf "${TMP_DIR}/google-cloud-sdk.tar.gz" -C "${GCLOUD_HOME}" --strip-components=1 \
    && "${GCLOUD_HOME}/install.sh" \
    --bash-completion=false \
    --path-update=false \
    --usage-reporting=false \
    --quiet \
    && rm -rf "${TMP_DIR}" \
    && gcloud --version
