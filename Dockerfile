FROM nvidia/cuda:12.4.1-base-ubuntu24.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV GRADIO_ANALYTICS_ENABLED=False
ENV HF_HUB_DISABLE_TELEMETRY=1
ENV DO_NOT_TRACK=1
ENV CMDARGS="--listen --disable-analytics --disable-metadata"

RUN apt-get update -y -o Acquire::Retries=3 && \
	apt-get install -y --no-install-recommends curl libgl1 libglib2.0-0 python3-pip python-is-python3 git && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

COPY requirements_docker.txt requirements_versions.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements_docker.txt -r /tmp/requirements_versions.txt && \
	rm -f /tmp/requirements_docker.txt /tmp/requirements_versions.txt

RUN adduser --disabled-password --gecos '' user && \
	mkdir -p /content/app /content/data/models /content/data/outputs

COPY entrypoint.sh /content/entrypoint.sh
RUN chmod 755 /content/entrypoint.sh

COPY . /content/app
RUN mv /content/app/models /content/app/models.org && \
	ln -s /content/data/models /content/app/models && \
	ln -s /content/data/outputs /content/app/outputs && \
	chown -R root:root /content/app && \
	chmod -R a+rX,go-w /content/app && \
	chown -R user:user /content/data

WORKDIR /content
USER user

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
	CMD curl -fsS http://127.0.0.1:7865/ >/dev/null || exit 1

CMD [ "sh", "-c", "exec /content/entrypoint.sh ${CMDARGS}" ]
