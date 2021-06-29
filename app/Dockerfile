FROM python:3.9.5-slim-buster

RUN apt-get update ##[edited]
RUN apt-get install wget -y
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN apt-get install poppler-utils -y
RUN apt-get install tesseract-ocr -y

COPY . .

ENV TESSDATA_PREFIX="/usr/local/share/tessdata"
RUN chmod +x ./tessdata

RUN mkdir -p "/usr/local/share/tessdata/rus"
RUN ./tessdata rus --best

RUN mkdir -p "/usr/local/share/tessdata/eng"
RUN ./tessdata eng --best

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
