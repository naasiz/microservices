# Use a lightweight Nginx image
FROM nginx:alpine

# Remove the default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy our dashboard files to the nginx served folder
COPY . /usr/share/nginx/html

# Expose the default Nginx port
EXPOSE 80
