FROM amazonlinux:2

RUN yum update -y && \
    amazon-linux-extras install epel -y && \
    rpm -Uvh https://download.postgresql.org/pub/repos/yum/14/redhat/rhel-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm && \
    yum install -y postgresql14 && \
    yum clean all

ENV PATH="/usr/pgsql-14/bin:${PATH}"