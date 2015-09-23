FROM honeynet/thug

RUN useradd -g users -d /home/contra -m -s /sbin/nologin -u 1000 contra && \
mkdir -p /home/contra/artifacts && \
chown -R contra:users /home/contra

COPY ["./*.py", "/opt/thug/src/"]
COPY ["./ghost/", "/opt/thug/src/ghost/"]

RUN apt-get update && apt-get install -y --force-yes python-pyside xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic fonts-monapo

USER contra
