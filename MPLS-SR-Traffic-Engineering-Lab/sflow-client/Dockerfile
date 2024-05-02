FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive



RUN apt update
RUN apt install -y default-jre wget
RUN wget https://inmon.com/products/sFlow-RT/sflow-rt_3.0-1702.deb
RUN dpkg -i sflow-rt_3.0-1702.deb
RUN systemctl enable sflow-rt

RUN /usr/local/sflow-rt/get-app.sh sflow-rt browse-flows
RUN /usr/local/sflow-rt/get-app.sh sflow-rt browse-metrics
RUN /usr/local/sflow-rt/get-app.sh sflow-rt topology
RUN /usr/local/sflow-rt/get-app.sh sflow-rt sflow-test










