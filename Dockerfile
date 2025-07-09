FROM --platform=linux/amd64 python:3.11.9-slim

# ENV PYTHONUNBUFFERED=1

# Update the system and install packages
RUN apt-get update -y \
    && pip install --upgrade pip \
    # dependencies for building Python packages
    && pip install --upgrade setuptools \
    && apt-get install -y build-essential \
    # install dependencies manager
    && pip install pipenv watchdog \
    # cleaning up unused files
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y default-libmysqlclient-dev build-essential pkg-config

# RUN pip install mysqlclient==2.2.0


# Install project dependencies
COPY ./Pipfile ./Pipfile.lock /
RUN pipenv sync --system

# TODO: Investigate
# RUN pip install psycopg[binary]

# cd /app (get or create)
WORKDIR /app
COPY ./ ./
# RUN python support/manage.py runserver
# CMD python support/manage.py runserver

EXPOSE 8000
ENTRYPOINT [ "python" ]
CMD ["src/manage.py", "runserver", "0.0.0.0:8000"]

# RUN echo "Hello from hillel" >> test.txt

# CMD ["/bin/bash"]
