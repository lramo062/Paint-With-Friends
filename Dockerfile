# build docker
# sudo docker build -t lester/dev-environment .

# run docker with command:
# docker run -i -t -v /home/lester:/home/lester/local lester/dev-environment /bin/zsh

FROM ubuntu:latest

# Locales
ENV LANGUAGE=en_US.UTF-8
ENV LANG=en_US.UTF-8
RUN apt-get -y update && apt-get install -y locales && locale-gen en_US.UTF-8
RUN DEBIAN_FRONTEND=noninteractive


RUN apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Common packages
RUN apt-get -y update && apt-get install -y \
      build-essential \
      python3-tk \
      python3-pil \
      autoconf \
      automake \
      cmake \
      g++ \
      libtool \
      libtool-bin \
      pkg-config \
      python3 \
      python3-pip

WORKDIR /usr/local/bin/paint-with-friends
COPY server.py .

EXPOSE 10000:10000/udp

CMD ["python3", "server.py"]
