FROM python:3.8-slim as lab_assistant_utils_build

COPY . /opt/lab-assistant-utils
WORKDIR /opt/lab-assistant-utils
RUN pip install --upgrade build \
    && python -m build

FROM python:3.8-slim
COPY --from=lab_assistant_utils_build /opt/lab-assistant-utils/dist/lab_assistant_utils-1.0.0-py3-none-any.whl /tmp
RUN pip install --upgrade pip \
    && pip install /tmp/lab_assistant_utils-1.0.0-py3-none-any.whl
ENTRYPOINT ["lab"]
CMD ["--help"]