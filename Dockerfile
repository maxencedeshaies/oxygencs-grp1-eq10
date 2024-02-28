FROM python:3.8-alpine
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir micropipenv[toml] && \
    micropipenv install --deploy && \
    pip uninstall micropipenv[toml] -y
COPY src .
CMD ["python3", "main.py"]