# Docker container with python & spamfilter
# loads settings from spamfilter.ini
# to use this container separately do:
# docker build -t spamfilter .
# docker run spamfilter
FROM python:3.8
ADD . ./
WORKDIR ./
RUN pip install -r requirements.txt
VOLUME ./spamfilter.ini:/spamfilter.ini
CMD python __main__.py
