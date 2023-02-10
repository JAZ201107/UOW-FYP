FROM python:3.7.16

# Create a Work Directory
RUN mkdir -p /home/uow_fyp
WORKDIR /home/uow_fyp

ENV PYTHONUNBUFFERED=1

# COPY Files
COPY ./requirements.txt /home/uow_fyp/requirements.txt

EXPOSE 8000

RUN apt-get install -y default-libmysqlclient-dev
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /home/uow_fyp/requirements.txt

ENV PATH="/py/bin:$PATH"



