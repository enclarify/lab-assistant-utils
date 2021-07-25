FROM python:3.6-slim

COPY . /opt/lab-assistant-utils
WORKDIR /opt/lab-assistant-utils
RUN pip install --upgrade build \
    && python -m build