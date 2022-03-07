FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

COPY DRipper.py ./ripper/* requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    rm -rf /app/requirements.txt

WORKDIR /app
ENTRYPOINT ["python", "DRipper.py"]
