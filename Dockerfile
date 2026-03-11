from python:3.14-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "fastapi_clean.main:app", "--host", "0.0.0.0", "--port", "8000"]