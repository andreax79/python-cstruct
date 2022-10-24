FROM i386/ubuntu

RUN apt-get update && \
    apt-get -y install \
    python3.6 \
    python3.6-dev \
    python3.6-distutils \
    curl \
    make && \
    rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py && \
    python3.6 get-pip.py
RUN pip install pytest
WORKDIR /app
