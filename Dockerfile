FROM alpine:latest


RUN apk add py3-pip
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python", "run.py"]
