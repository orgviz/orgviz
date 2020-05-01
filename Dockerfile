FROM fedora

RUN yum install -y python3-cherrypy python3-configargparse npm make graphviz && yum clean all

COPY . /opt/ 

RUN cd /opt/webui/ && npm install -g && make && mkdir /var/www/

ENTRYPOINT /opt/web.py --outputDirectoryLocal /var/www/
