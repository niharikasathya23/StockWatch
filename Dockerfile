FROM python:3.7

ADD short-sample-request.py /
COPY data /
RUN pip3 install --upgrade minio redis jsonpickle requests

CMD mkdir /sample
WORKDIR /sample

COPY . /sample
CMD cd /sample && \
python3 short-sample-request.py