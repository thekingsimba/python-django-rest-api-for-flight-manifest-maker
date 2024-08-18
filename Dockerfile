FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env ./

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "flight_manifest_maker_api.wsgi:application"]
