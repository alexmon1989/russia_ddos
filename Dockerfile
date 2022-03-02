FROM python:3.9-slim-buster
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y dnsutils

COPY DRipper.py headers.txt useragents.txt /app/

WORKDIR /app
ENTRYPOINT ["python", "DRipper.py"]
