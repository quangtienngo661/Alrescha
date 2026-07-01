FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BASE_URL={{BASE_URL}}

CMD ["python", "main.py"]