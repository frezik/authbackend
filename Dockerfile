# sudo docker build -t authbackend .

# To run flask debugger
# sudo docker run --rm -it  --entrypoint /bin/bash authbackend

# To run w/ gunicorn proxy (and a proxy path)
# docker run -it  -p 5000:5000   --env AUTHIT_PROXY_PATH=authit authbackend

FROM python:3.8-slim-buster as flaskbase

MAINTAINER Brad Goodman "brad@bradgoodman.com"

WORKDIR /authserver

RUN pip3 install flask
RUN pip3 install slack_sdk 
RUN pip3 install --upgrade cryptography
RUN pip3 install testresources
RUN pip3 install flask_login
RUN pip3 install flask_user
RUN pip3 install flask_dance
RUN pip3 install stripe
RUN pip3 install apiclient
RUN pip3 install google-api-python-client
RUN pip3 install paho-mqtt
RUN pip3 install pytz
RUN pip3 install boto3
RUN pip3 install oauth2client
RUN pip3 install google-oauth
RUN pip3 install sqlalchemy_utils
RUN pip3 install email_validator
#RUN pip3 install pycurl
RUN pip3 install configparser
RUN pip3 install gunicorn
#RUN pip3 install functools 
#RUN pip3 install slackclient (OLD - SHOULDN'T NEED)


FROM flaskbase  as pycurl

RUN apt-get update
#RUN apt-get -y install curl
RUN apt-get install -y gcc
RUN apt-get install -y libssl-dev libcurl4-openssl-dev python3-dev

RUN pip3 install pycurl

FROM pycurl as ical
run pip3 install icalendar

FROM ical  as sqlite3

RUN apt-get update
RUN apt-get install -y sqlite3
RUN apt-get install -y bash

FROM sqlite3
COPY . . 

ENTRYPOINT ["/bin/bash"]

CMD [ "dockerentry.sh" ]
