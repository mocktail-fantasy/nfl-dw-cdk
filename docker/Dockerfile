FROM amazonlinux:2

RUN yum update -y && \
    yum install -y amazon-linux-extras && \
    amazon-linux-extras enable postgresql15 && \
    yum install -y postgresql postgresql-libs && \
    yum clean all