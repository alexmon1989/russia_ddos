FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

COPY DRipper.py requirements.txt /app/
COPY ripper /app/ripper

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    rm -rf /app/requirements.txt

WORKDIR /app
ENTRYPOINT ["python", "DRipper.py"]
