## To implement
FROM python:3.8-slim
RUN pip install pipenv
ENV PROJECT_DIR /usr/local/src/oxygencs-grp1-eq10
WORKDIR ${PROJECT_DIR}
COPY Pipfile Pipfile.lock ${PROJECT_DIR}/
RUN pipenv install --system --deploy