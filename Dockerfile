FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    libgomp1 \
    exiftool \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -o dji_thermal_sdk_v1.7_20241205.zip "https://terra-1-g.djicdn.com/2640963bcd8e45c0a4f0cb9829739d6b/TSDK/v1.7(12.0-WA345T)/dji_thermal_sdk_v1.7_20241205.zip"
RUN unzip dji_thermal_sdk_v1.7_20241205.zip -d dji && \
    mkdir /usr/lib/dji && \
    cp -r dji/tsdk-core/lib/linux/* /usr/lib/dji/

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY thermal_parser.py thermal_parser.py
COPY server.py server.py
COPY entrypoint.sh entrypoint.sh

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
