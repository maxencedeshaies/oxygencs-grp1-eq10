#FROM python:3.8-alpine
#WORKDIR /app
#COPY Pipfile Pipfile.lock /app/
#RUN pip install --no-cache-dir micropipenv[toml] && \
#    micropipenv install --deploy
#COPY . /app
#CMD ["python", "app.py"]

#FROM python:3.8-slim
#WORKDIR /app
#COPY Pipfile Pipfile.lock ./
#RUN pip install pipenv && \
#    pipenv install --deploy --system
#COPY . /app
#CMD ["python", "main.py"]

FROM python:3.8-alpine
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir micropipenv[toml] && \
    micropipenv install --deploy && \
    pip uninstall micropipenv -y
COPY src .
CMD ["python3", "main.py"]