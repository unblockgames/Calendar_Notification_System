FROM python

RUN mkdir /home/app

COPY . /home/app

RUN apt-get update

RUN apt-get -y install vim

RUN apt-get -y install cron

RUN pip3 install -r /home/app/requirements.txt

# Copy hello-cron file to the cron.d directory
COPY default-cron /etc/cron.d/default-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/default-cron

# Apply cron job
RUN crontab /etc/cron.d/default-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

CMD ["cron", "-f"]