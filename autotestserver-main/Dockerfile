FROM python:3.11-slim

ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless wget unzip curl \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.34.0/allure-commandline-2.34.0.zip -O /tmp/allure.zip \
    && unzip -q /tmp/allure.zip -d /opt \
    && rm /tmp/allure.zip \
    && ln -s /opt/allure-2.34.0/bin/allure /usr/local/bin/allure

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]
