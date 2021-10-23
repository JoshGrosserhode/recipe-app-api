FROM python:3.10-alpine3.14
LABEL maintainer="Josh Grosserhode"

ENV PYTHONUNBUFFERED=1

# Copies from the adjacent directory to the docker image
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
# starting location when running image
WORKDIR /app
COPY ./app /app

# create user to run docker image, -D is a user that does not have a directory, but only runs image
RUN adduser -D user
# switch to new user, this is for security and prevents the root account user from running application
USER user

# run cmd: docker build .


