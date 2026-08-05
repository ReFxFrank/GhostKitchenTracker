FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Raw snapshots land in /data (bind-mounted from ../data in compose).
ENV SEANCE_DATA_DIR=/data
CMD ["python", "cli.py", "--help"]
