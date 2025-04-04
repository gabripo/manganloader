FROM python:3.13.2

RUN apt-get install -y wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get -y install google-chrome-stable

ENV DockerHOME=/home/manganloader
RUN mkdir -p ${DockerHOME}
WORKDIR ${DockerHOME}
RUN git clone --recurse-submodules https://github.com/gabripo/manganloader.git ${DockerHOME}

RUN pip install -r requirements.txt
RUN git submodule update --init --recursive
RUN pip install gunicorn

ENV TargetPort=3000
EXPOSE ${TargetPort}/udp
EXPOSE ${TargetPort}/tcp

ENV APP_IN_DOCKER=Yes

# ensure Python prints are catched when created - and not buffered
ENV PYTHONUNBUFFERED=TRUE

# entrypoint with Flask only - no gunicorn
# ENTRYPOINT [ "python" ]
# CMD ["flask_app.py"]

# entrypoint with gunicorn
ENTRYPOINT gunicorn --bind 0.0.0.0:${TargetPort} flask_app:app