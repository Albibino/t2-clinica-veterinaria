FROM nginx:alpine

LABEL maintainer="Clínica Veterinária"
LABEL description="Frontend HTML/CSS/JS servido pelo Nginx"

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY static/ /usr/share/nginx/html/static/
COPY static/*.html /usr/share/nginx/html/

RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
