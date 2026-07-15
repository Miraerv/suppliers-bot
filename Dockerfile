# Latest stable on Docker Hub: 3.14.x (tag 3.14 / latest).
# 3.15-rc exists but is pre-release — keep slim for smaller image.
FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
