FROM python:3.10.0

RUN apt-get update \
  && apt-get install --yes --no-install-recommends \
    tree \
    poppler-utils \
  && apt-get autoclean \
  && apt-get --purge --yes autoremove \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry==1.1.11 && poetry install --no-interaction --no-ansi

COPY . .

ENV PYTHONPATH src/

CMD ["pytest"]
