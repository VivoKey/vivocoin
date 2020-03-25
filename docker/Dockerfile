# Build Python extensions requiring gcc and dev libraries
FROM python:3.7-alpine3.8 as build

RUN apk add libc-dev gcc postgresql-dev libffi-dev linux-headers

COPY requirements.txt /tmp

RUN pip install virtualenv
RUN virtualenv /virtualenv
RUN /virtualenv/bin/pip install -r /tmp/requirements.txt

# Copy the built virtualenv across to the final container
FROM python:3.7-alpine3.8
RUN apk add postgresql-client openssl stunnel
COPY --from=build /virtualenv/ /virtualenv
