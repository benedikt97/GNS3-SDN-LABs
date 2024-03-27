FROM ubuntu:22.04
ENV DEBIAN_FRONTEND noninteractive

# install tools
RUN apt-get update \
        && apt-get upgrade -y \
        && apt-get install -y python3 python3-pip

RUN pip3 install p4runtime-shell




CMD ["/bin/bash"]
