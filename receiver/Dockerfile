FROM python:3
LABEL maintainer="nzirak@my.bcit.ca"
RUN mkdir /app
# We copy just the requirements.txt first to leverage Docker cache
# on `pip install`
COPY ./requirements.txt /app/requirements.txt
# Set the working directory
WORKDIR /app
# Install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt
# Copy the source code
# COPY ../config/receiver_config.yml /app/receiver_config.yml
# COPY ../config/log_config.yml /app/log_config.yml
COPY . /app
# Change permissions and become a non-privileged user
RUN chown -R nobody:nogroup /app
USER nobody
# Tells on which port the service listens in the container
EXPOSE 8080
# Entrypoint = run Python
ENTRYPOINT [ "python3" ]
# Default = run app.py
CMD [ "app.py" ]
