FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

RUN pip install colorama

COPY DRipper.py headers.txt useragents.txt /app/

WORKDIR /app
ENTRYPOINT ["python", "DRipper.py"]
