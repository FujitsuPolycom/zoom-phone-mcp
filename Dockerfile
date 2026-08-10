FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY README.md .

RUN pip install --no-cache-dir .

EXPOSE 8767

CMD ["python", "-m", "zoom_phone_mcp.server"]
