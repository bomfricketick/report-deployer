FROM python:3.12-slim

RUN pip install --no-cache-dir pip-tools

COPY . /app
WORKDIR /app

RUN pip-compile pyproject.toml

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "/app/report_deployer/app.py"]
