FROM python:3.14

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY ./requirements.txt .

RUN uv sync --frozen

COPY . .

CMD ["fastapi" , "run", "main.py", "--port", "80"]


