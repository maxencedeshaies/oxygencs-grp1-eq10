FROM python:3.8-alpine
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && \
    pipenv install && \
    pip uninstall pipenv -y
COPY . /app
CMD ["python", "app.py"]