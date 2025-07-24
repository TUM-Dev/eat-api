FROM python:3.14.0rc1

RUN apt-get update \
  && apt-get install --yes --no-install-recommends \
    tree \
    poppler-utils \
  && apt-get autoclean \
  && apt-get --purge --yes autoremove \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src/app

COPY pyproject.toml uv.lock ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY . .

ENV PYTHONPATH src/

CMD ["uv run pytest"]
