FROM python:3
WORKDIR /backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean

RUN pip install --upgrade pip
COPY ./requirements.txt /backend/requirements.txt
RUN pip install -r requirements.txt
COPY . /backend