FROM python:3.10-alpine
ENV PYTHONUNBUFFERED=1

RUN apk add curl git && \
    pip install --upgrade pip git+https://github.com/alexmon1989/russia_ddos.git

ENTRYPOINT ["dripper"]
