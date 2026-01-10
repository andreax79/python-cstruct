FROM i386/ubuntu

RUN apt-get update && \
    apt-get -y install \
    python3.7 \
    python3.7-dev \
    python3.7-distutils \
    curl \
    make && \
    rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://bootstrap.pypa.io/pip/3.7/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py
RUN pip install pytest
WORKDIR /app
