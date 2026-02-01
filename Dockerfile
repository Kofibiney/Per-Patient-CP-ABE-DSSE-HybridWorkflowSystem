FROM python:3.9-slim

# Install System Dependencies (will be removed later)
RUN apt-get update && apt-get install -y \
    build-essential \
    flex \
    bison \
    libgmp-dev \
    libssl-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# COMPILE PBC LIBRARY FROM SOURCE
WORKDIR /tmp
RUN wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz \
    && tar -xvf pbc-0.5.14.tar.gz \
    && cd pbc-0.5.14 \
    && ./configure \
    && make \
    && make install \
    && ldconfig \
    && cd /tmp \
    && rm -rf pbc-0.5.14 pbc-0.5.14.tar.gz

# Install Python Dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir pycryptodome pandas numpy pyparsing kagglehub psutil

# MANUAL INSTALL OF CHARM-CRYPTO (Clone -> Configure -> Install)
WORKDIR /tmp
RUN git clone https://github.com/JHUISI/charm.git \
    && cd charm \
    && ./configure.sh \
    && make \
    && make install \
    && cd /tmp \
    && rm -rf charm

# Clean up build dependencies to reduce image size
RUN apt-get purge -y --auto-remove \
    build-essential \
    flex \
    bison \
    git \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# Keep only runtime dependencies
RUN apt-get update && apt-get install -y \
    libgmp10 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Setup App
WORKDIR /app

# Copy only necessary files (src code, not data)
COPY src/ /app/src/
COPY thesis_experiments.py /app/
COPY requirements.txt /app/

# Note: Dataset should be mounted as a volume at runtime
# docker run -v $(pwd)/synthea/output/csv:/app/data ...

CMD ["python", "thesis_experiments.py"]
