# This builds an image suitable for C++ development
FROM mcr.microsoft.com/vscode/devcontainers/cpp:dev-buster
RUN echo "deb http://apt.llvm.org/buster/ llvm-toolchain-buster-12 main"     >> /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/buster/ llvm-toolchain-buster-12 main" >> /etc/apt/sources.list
RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
RUN apt-get update
RUN apt-get -y install --no-install-recommends clangd-12 python3-jsmin
COPY setup-container.py /usr/local/bin/setup-container.py
