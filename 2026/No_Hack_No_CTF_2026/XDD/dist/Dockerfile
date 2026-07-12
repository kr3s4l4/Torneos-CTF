FROM php:8.3-apache-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        firefox-esr \
        supervisor \
        python3 \
        procps \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's/^Listen 80$/#Listen 80/' /etc/apache2/ports.conf

COPY app/ext/folio/prebuilt/folio.so /tmp/folio.so
RUN extdir="$(php -r 'echo ini_get("extension_dir");')" \
    && cp /tmp/folio.so "$extdir/folio.so" \
    && echo 'extension=folio.so' > /usr/local/etc/php/conf.d/docker-php-ext-folio.ini \
    && rm /tmp/folio.so

COPY apache/000-default.conf /etc/apache2/sites-available/000-default.conf
COPY php.ini /usr/local/etc/php/conf.d/folio.ini
COPY app/public /var/www/html/public
COPY app/src /var/www/html/src
COPY reviewer /opt/reviewer
COPY private_service /opt/private_service
COPY supervisord.conf /etc/supervisor/conf.d/folio.conf

RUN mkdir -p /tmp/folio-notes /tmp/folio-drops \
    && chown -R www-data:www-data /tmp/folio-notes /tmp/folio-drops /var/www/html

EXPOSE 8080 8081

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/folio.conf"]
