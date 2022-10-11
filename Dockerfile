FROM python:3

WORKDIR /fastapi_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./app ./app

CMD ["python", "./app/main.py"]
# CMD [ "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1" ]