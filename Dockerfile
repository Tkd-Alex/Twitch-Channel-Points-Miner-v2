FROM python:3.8-slim-buster

ARG BUILDX_QEMU_ENV

WORKDIR /usr/src/app

COPY ./requirements.txt ./

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN pip install --upgrade pip

ARG TARGETPLATFORM

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -qq -y --fix-missing --no-install-recommends \
    gcc \
    libffi-dev \
    rustc \
    zlib1g-dev \
    libjpeg-dev \
    libssl-dev \
    make \
    automake \
    g++ \
    subversion \
    python3-dev \
  && if [ "${BUILDX_QEMU_ENV}" = "true" ] && [ "$(getconf LONG_BIT)" = "32" ]; then \
        pip install -U cryptography==3.3.2; \
     fi \
  && if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
        apt-get -y install python3-pandas; \
        pip install pandas --no-build-isolation; \
     fi \
  && pip install -r requirements.txt \
  && pip cache purge \
  && apt-get remove -y gcc rustc \
  && apt-get autoremove -y \
  && apt-get autoclean -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc/*

ADD ./TwitchChannelPointsMiner ./TwitchChannelPointsMiner
ENTRYPOINT [ "python", "run.py" ]
