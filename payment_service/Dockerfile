FROM python:3.11-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt ngrok
RUN apt-get update && apt-get install -y wget unzip && \
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz && \
    tar -xvzf ngrok-v3-stable-linux-amd64.tgz && \
    mv ngrok /usr/local/bin && \
    rm ngrok-v3-stable-linux-amd64.tgz


COPY . .

EXPOSE 8000

RUN ngrok config add-authtoken 2gxiPiSc8N3UVqRWlGZh7Pj4Wvw_64zk23ENkvvG3yUHr6UNi

# Chạy cả Django và ngrok song song
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]