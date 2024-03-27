FROM debian:buster
ENV DEBIAN_FRONTEND noninteractive

ADD stratum_bmv2_deb.deb stratum_bmv2_deb.deb 
# install tools
RUN apt-get update \
        && apt-get upgrade -y \
        && apt-get install -y /stratum_bmv2_deb.deb

ADD chassis_config.pb.txt /etc/stratum/chassis_config.pb.txt
RUN mkdir /var/log/stratum
RUN chmod 777 /var/log/stratum

ADD run_switch.sh run_switch.sh
RUN chmod +x run_switch.sh
ADD reset_switch.sh reset_switch.sh
RUN chmod +x reset_switch.sh


CMD ["/bin/bash"]
