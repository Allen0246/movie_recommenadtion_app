FROM python:3.8.0-alpine

ENV FLASK_APP=/app/project
ENV FLASK_PATH=/app/project
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
ENV TZ="Europe/Budapest"

# install dependencies
RUN pip install --upgrade pip
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev \
    && apk add build-base \
    && apk add -U tzdata 

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .

EXPOSE 5000
ENTRYPOINT ["./start.sh"]
