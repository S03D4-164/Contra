FROM honeynet/thug

#RUN useradd -g users -d /home/contra -m -s /sbin/nologin -u 1000 contra
RUN useradd -g users -d /home/contra -m -u 1000 contra 

COPY ["./files/", "/home/contra/files/"]

RUN mv /opt/thug/src/Logging /opt/thug/src/Logging.bk && mv /home/contra/files/Logging /opt/thug/src/

RUN chown -R contra:users /home/contra

RUN apt-get update && apt-get install -y --force-yes python-pyside xvfb xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic fonts-monapo && apt-get clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

USER contra
