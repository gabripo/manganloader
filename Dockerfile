FROM python:3.13.2

RUN apt-get install -y wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN apt-get update
RUN apt-get -y install google-chrome-stable

ENV DockerHOME=/home/manganloader
RUN mkdir -p ${DockerHOME}
WORKDIR ${DockerHOME}
COPY . $DockerHOME

RUN pip install -r requirements.txt
RUN git submodule update --init --recursive

RUN pip install gunicorn

ENV TargetPort=3000
EXPOSE ${TargetPort}/udp
EXPOSE ${TargetPort}/tcp

ENTRYPOINT [ "python" ]
CMD ["flask_app.py"]
# ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:${TargetPort}", "flask_app:app"]