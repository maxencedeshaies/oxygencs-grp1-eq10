FROM python:3.8-slim
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && \
    pipenv install
COPY . /app
CMD ["python", "app.py"]