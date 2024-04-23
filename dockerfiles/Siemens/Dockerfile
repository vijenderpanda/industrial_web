FROM python:3.11-slim


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
# dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY dockerfiles/Siemens/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
  
# copy all required requirements files
COPY requirements/base.txt /app/requirements/
COPY requirements/siemens.txt /app/requirements/

# Merge all requirements to one file
RUN cat /app/requirements/*.txt  > /app/requirements.txt

# Upgrade Pip 
RUN pip install --upgrade pip

# Install Dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app



