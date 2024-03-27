FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive

# install tools
RUN apt-get update \
        && apt-get upgrade -y \
        && apt-get install -y python3 python3-pip

RUN pip3 install faucet

ADD faucet-L2.yaml faucet-L2.yaml
ADD faucet-L3.yaml faucet-L3.yaml




CMD ["/bin/bash"]
