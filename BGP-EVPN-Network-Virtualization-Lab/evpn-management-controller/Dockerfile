FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive

# install tools
RUN apt-get update \
        && apt-get upgrade -y \
        && apt-get install -y python3 python3-pip iputils vi nano ssh sshpass

 
RUN pip3 install pandas
RUN pip3 install paramiko
RUN pip3 install scp
RUN pip3 install tabulate

ADD BGP_EVPN_LAB /BGP_EVPN_LAB

CMD ["/bin/bash"]
