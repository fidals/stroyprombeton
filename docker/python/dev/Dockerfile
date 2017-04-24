FROM python:latest

RUN apt-get update
RUN apt-get install -y wkhtmltopdf xvfb

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /usr/app/src/
