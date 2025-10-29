FROM python:3.10-alpine

WORKDIR /app

COPY logger.py .

RUN pip install flask

VOLUME ["/logs"]

EXPOSE 4000

CMD ["python", "logger.py"]
