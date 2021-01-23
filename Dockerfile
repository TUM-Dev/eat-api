FROM python:3.6

RUN apt-get update \
  && apt-get install --yes --no-install-recommends \
    tree \
    poppler-utils \
  && apt-get autoclean \
  && apt-get --purge --yes autoremove \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH src/

CMD ["pytest"]
