FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    libgomp1

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY server.py server.py
COPY lib lib

ENV LD_LIBRARY_PATH="/usr/src/app/lib/dji_thermal_sdk_v1.7_lean:${LD_LIBRARY_PATH}"


CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8081"]
