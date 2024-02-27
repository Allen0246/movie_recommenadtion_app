FROM nginx:1.17.4-alpine


ADD certs/certificate.crt /etc/nginx/certificate.crt
ADD certs/privatekey.key /etc/nginx/privatekey.key

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
