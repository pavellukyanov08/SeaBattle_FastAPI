FROM python:3.12.11-slim

WORKDIR /seabattle

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:proj_app", "--host", "0.0.0.0", "--port", "8000"]
