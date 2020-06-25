FROM python:3.8-alpine

RUN apk update && apk add --no-cache --virtual \
    build-deps gcc python3-dev musl-dev libffi-dev py-cryptography openssl-dev

COPY compose/proxy/entrypoint /entrypoint
COPY compose/proxy/start-proxy /start-proxy
COPY compose/proxy/start-tests /start-tests

RUN sed -i 's/\r//' /entrypoint && chmod +x /entrypoint \
    && sed -i 's/\r//' /start-proxy && chmod +x /start-proxy \
    && sed -i 's/\r//' /start-tests && chmod +x /start-tests

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

EXPOSE 8080
ENTRYPOINT ["/entrypoint"]
