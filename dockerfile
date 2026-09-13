FROM python:3.12

WORKDIR /qdrantvdb/fastapiendpoints.py

COPY requirements.txt .

RUN pip insatll requirements.txt

COPY . . 

EXPOSE 5000

