# Specify the parent image from which we build
# You can build an image with
# docker build  -t miles:v1 .

FROM ubuntu:22.04

# Set the working directory
WORKDIR /work

# Prepare all dependencies and clone the repo
RUN cd /work
RUN apt-get update
RUN apt-get install git curl -y
RUN git clone https://github.com/oloapinivad/MiLES.git
RUN curl -O https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh

ENV CONDA_DIR /opt/conda
RUN /bin/bash ./Miniconda3-py39_4.12.0-Linux-x86_64.sh -b -p /opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN conda install -c conda-forge R cdo
RUN conda install -c conda-forge r-ncdf4 r-maps r-akima r-mapproj r-pcict r-abind

WORKDIR /work/MiLES
COPY config_docker.sh config/config_docker.sh

# Run the application and print help
CMD ["./wrapper_miles.sh"]
