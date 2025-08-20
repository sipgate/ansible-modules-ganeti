FROM debian:12

RUN apt update && apt install --no-install-recommends -y python3 python3-pip python3-setuptools python3-pycurl python3-simplejson docker.io curl && apt clean
RUN pip3 install --break-system-packages pytest pytest-mock ansible

ADD run-tests.sh /run-tests.sh

CMD ["/run-tests.sh", "/workdir"]
