FROM python:3.7-alpine
WORKDIR /message-microservice
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]