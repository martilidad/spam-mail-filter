FROM python:3.8
ADD . ./
WORKDIR ./
RUN pip install -r requirements.txt
CMD python __main__.py
