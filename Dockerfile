from ubuntu:22.04


# install build dependencies
RUN apt-get update -y && apt-get install -y python3-pip python3 locales python3-venv \
    && apt-get clean && rm -f /var/lib/apt/lists/*_*

# Set the locale
RUN echo 'en_US.UTF-8 UTF-8' >>/etc/locale.gen && locale-gen

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR /code

copy ./requirements.txt /code/requirements.txt
# RUN dd if=/dev/urandom of=/code/largefile bs=1M count=478

RUN python3 -mvenv env
RUN env/bin/pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./app /code/app

CMD ["env/bin/uvicorn",  "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
