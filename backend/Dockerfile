FROM python:3.14

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "fastapi" , "run", "main.py", "--port", "80"]


