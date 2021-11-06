# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-alpine3.14

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# copy pip requirements
COPY ./requirements.txt /requirements.txt
# install postgres-cleint
RUN apk add --update --no-cache postgresql-client
# install temporary dependencies needed for all pip requirements
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
# install pip requirements
RUN python -m pip install -r requirements.txt
# remove temporary dependencies folder
RUN apk del .tmp-build-deps

# set working directory to images /app folder
WORKDIR /app
# copy from the local ./app folder to the image /app folder
COPY ./app /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# File wsgi.py was not found in subfolder: 'recipe-app-api'. Please enter the Python path to wsgi file.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi"]
