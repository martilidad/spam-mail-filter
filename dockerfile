# Docker container with python & spamfilter
# loads settings from spamfilter.ini
# to use this container separately do:
# docker build -t spamfilter .
# docker run -it spamfilter
FROM python:3.8
ADD . ./
WORKDIR ./
VOLUME ./spamfilter.ini:/spamfilter.ini
VOLUME ./data/:/data/
RUN pip install -r requirements.txt
CMD python __main__.py
