FROM fedora

RUN dnf -y update && \
    dnf -y install graphviz python3-configargparse && \
    dnf clean all

COPY orgviz.py /usr/local/bin/orgviz

ENTRYPOINT ["/usr/local/bin/orgviz"]
