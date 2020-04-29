FROM fedora

RUN yum install -y python3-cherrypy python3-configargparse npm make && yum clean all

COPY . /opt/ 

RUN cd /opt/webui/ && npm install -g && make

ENTRYPOINT /opt/web.py
