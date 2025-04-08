FROM python:3
LABEL maintainer="nzirak@my.bcit.ca"
RUN mkdir /app
RUN mkdir /app/data
# We copy just the requirements.txt first to leverage Docker cache
# on `pip install`
COPY ./requirements.txt /app/requirements.txt
# Set the working directory
WORKDIR /app
# Install dependencies
RUN pip3 install -r requirements.txt
# Copy the source code
# COPY ../config/processing_config.yml /app/app_conf.yml
# COPY ../config/log_config.yml /app/conf_log.yml
COPY . /app
# Change permissions and become a non-privileged user
RUN chown -R nobody:nogroup /app
RUN chmod +666 /app/data
USER nobody
# Tells on which port the service listens in the container
EXPOSE 8100
# Entrypoint = run Python
ENTRYPOINT [ "python3" ]
# Default = run app.py
CMD [ "app.py" ]
