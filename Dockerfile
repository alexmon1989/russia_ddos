FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

COPY ./ /app
WORKDIR /app

RUN apk add --update \
    curl git \
    gcc libc-dev fortify-headers linux-headers && \
    rm -rf /var/cache/apk/*
RUN pip install --upgrade pip -e .

ENTRYPOINT ["dripper"]
