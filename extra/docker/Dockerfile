FROM python:3.7-stretch
MAINTAINER Andrew Halberstadt <ahal@mozilla.com>

RUN mkdir /builds
RUN useradd -d /builds/worker -s /bin/bash -m worker
WORKDIR /builds/worker
ADD VERSION .

VOLUME /builds/worker/.cache
VOLUME /builds/worker/checkouts

ENV PATH="/builds/worker/bin:${PATH}"
ENV SHELL="bash"

RUN mkdir /builds/worker/bin
ADD run-adr /builds/worker/bin

RUN mkdir /setup
COPY dot-files/hgrc /root/.hgrc
ADD system-setup.sh /setup
ADD requirements.txt /setup
ADD robustcheckout.py /setup

RUN bash /setup/system-setup.sh
