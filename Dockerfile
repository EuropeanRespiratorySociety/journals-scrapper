FROM python:3.6-alpine
LABEL maintainer="samuelpouyt@gmail.com"
LABEL version="0.0"
LABEL description="Initial image for ERS scrapers"

ENV RUNTIME_PACKAGES libxslt libxml2 jpeg tiff libpng zlib git \
                     curl libpq
ENV BUILD_PACKAGES   build-base libxslt-dev libxml2-dev libffi-dev jpeg-dev \
                     tiff-dev libpng-dev zlib-dev openssl-dev

ADD . /code
WORKDIR /code

VOLUME /code/data

RUN \
  apk add --no-cache ${RUNTIME_PACKAGES} ${BUILD_PACKAGES} && \
  pip install -r ./requirements.txt && \
  chmod +x start.sh
  # apk del ${BUILD_PACKAGES} && \
  # rm -rf /root/.cache

EXPOSE 6800

CMD ["./start.sh"]