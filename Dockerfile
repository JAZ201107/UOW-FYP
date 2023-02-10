FROM python:3.7.16

# Create a Work Directory
RUN mkdir -p /home/uow_fyp
WORKDIR /home/uow_fyp

# COPY Files
COPY ./apps /home/uow_fyp/apps
COPY ./Final_Proj /home/uow_fyp/Final_Proj
COPY ./models /home/uow_fyp/models
COPY ./static /home/uow_fyp/static
COPY ./templates /home/uow_fyp/templates
COPY ./utils /home/uow_fyp/utils
COPY ./Yolo /home/uow_fyp/Yolo
COPY ./manage.py /home/uow_fyp/manage.py
COPY ./requirements.txt /home/uow_fyp/requirements.txt

EXPOSE 8000

RUN apt-get install -y default-libmysqlclient-dev && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /home/uow_fyp/requirements.txt && \

ENV PATH="/py/bin:$PATH"



