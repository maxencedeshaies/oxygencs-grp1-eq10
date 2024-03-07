FROM python:3.8-alpine

ARG HOST
ARG TOKEN
ARG T_MAX
ARG T_MIN
ARG DATABASE_URL

ENV HOST=${HOST}
ENV TOKEN=${TOKEN}
ENV T_MAX=${T_MAX}
ENV T_MIN=${T_MIN}
ENV DATABASE_URL=${DATABASE_URL}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir micropipenv[toml] && \
    micropipenv install --deploy && \
    pip uninstall micropipenv[toml] -y && \
    pip cache purge
COPY src .
CMD ["python3", "main.py"]