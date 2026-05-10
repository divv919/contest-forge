FROM python:3.14

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . .

CMD ["fastapi" , "run", "main.py", "--port", "80"]


