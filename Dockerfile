FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install .

EXPOSE 8000

CMD ["meshnode", "start"]
