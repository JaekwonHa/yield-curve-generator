FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y wget
RUN apt-get install -y cron
RUN apt-get install -y tzdata

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime
RUN echo "Asia/Seoul" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

WORKDIR /home/root/
ADD *.py /home/root/yield-curve-generator/
ADD requirements.txt /home/root/yield-curve-generator/
ADD credentials.json /home/root/yield-curve-generator/
ADD token.pickle /home/root/yield-curve-generator/

RUN pip install -r /home/root/yield-curve-generator/requirements.txt

ADD crontab /etc/cron.d/yield-curve-generator-cron

RUN chmod 0644 /etc/cron.d/yield-curve-generator-cron

RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log