FROM fedora

RUN yum install -y python3-cherrypy python3-configargparse python3-requests npm make graphviz && yum clean all

COPY . /opt/ 

RUN cd /opt/webui/ && npm install -g && make && mkdir /var/www/ && chmod 0777 /var/www/

USER 1001

ENTRYPOINT /opt/web.py --outputDirectoryLocal /var/www/
