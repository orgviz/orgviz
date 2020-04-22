FROM fedora

RUN yum install python3-configargparse python3-httplib2 python3-oauth2client python3-google-api-client.noarch python3-cherrypy.noarch python3-google-auth python3-pip -y && yum clean all
RUN pip3 install google-auth-oauthlib

COPY *.py /opt/

USER 1001

ENTRYPOINT /opt/web.py
