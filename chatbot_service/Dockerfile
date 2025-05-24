FROM python:3.9.13

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . /app/

EXPOSE 5005

CMD ["python", "main.py"]