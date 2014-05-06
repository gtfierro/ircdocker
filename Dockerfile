#FROM stackbrew/ubuntu:13.10
FROM mubuntu

RUN apt-get install -y ircd-hybrid vim less irssi libreadline-dev

RUN pip install supervisor

RUN mkdir -p /var/run/sshd
RUN mkdir -p /var/log/supervisor
RUN mkdir -p /etc/supervisor/conf.d
ADD supervisord.conf /etc/supervisord.conf
ADD ircd.conf /etc/ircd-hybrid/ircd.conf
#RUN /etc/init.d/ircd-hybrid restart
EXPOSE 6665 6666 6667 6668 6669 6670
CMD /usr/local/bin/supervisord
#ENTRYPOINT ["/usr/sbin/ircd-hybrid","-foreground"]
#CMD []
