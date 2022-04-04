FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

COPY ./ /app
WORKDIR /app

RUN apk add curl git && \
    pip install --upgrade pip -e .

ENTRYPOINT ["dripper"]
