FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
ENV DJANGO_SETTINGS_MODULE=bmrc.settings.docker

# Set working directory
WORKDIR /app

# Create django error log (mirrors the Vagrant provisioner)
RUN touch /var/log/django-errors.log && \
    chmod 666 /var/log/django-errors.log

# Update repos and install base dependencies
RUN rm -rf /var/lib/apt/lists/partial && \
    apt-get update -y -o Acquire::CompressionTypes::Order::=gz && \
    apt-get install -y software-properties-common

# Install Python 3.11 (Jammy ships with Python 3.10; we need 3.11 to match Vagrant)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y python3.11 python3.11-distutils python3-pip python3.11-dev python3.11-venv

# Install project system dependencies and dev tools
RUN apt-get install -y \
    vim git curl gettext build-essential \
    libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libllvm11 \
    postgresql postgresql-client libpq-dev

# Setup vim with ALE for developers who haven't configured linting locally
RUN mkdir -p /root/.vim/pack/git-plugins/start && \
    git clone --depth 1 https://github.com/dense-analysis/ale.git /root/.vim/pack/git-plugins/start/ale && \
    echo "let g:ale_linters_explicit = 1" >> /root/.vimrc && \
    echo "let g:ale_linters = { 'python': ['flake8'], 'javascript': ['eslint'] }" >> /root/.vimrc && \
    echo "let g:ale_python_flake8_options = '--ignore=D100,D101,D202,D204,D205,D400,D401,E303,E501,W503,N805,N806'" >> /root/.vimrc && \
    echo "let g:ale_fixers = { 'python': ['isort', 'autopep8', 'black'], 'javascript': ['eslint'] }" >> /root/.vimrc && \
    echo "let g:ale_python_black_options = '--skip-string-normalization'" >> /root/.vimrc && \
    echo "let g:ale_python_isort_options = '--profile black'" >> /root/.vimrc

# Configure PostgreSQL to trust local connections for dev convenience
RUN sed -i 's/^local\s\+all\s\+all\s\+peer/local all all trust/' /etc/postgresql/14/main/pg_hba.conf && \
    sed -i 's/^host\s\+all\s\+all\s\+127.0.0.1\/32\s\+scram-sha-256/host all all 127.0.0.1\/32 trust/' /etc/postgresql/14/main/pg_hba.conf && \
    sed -i 's/^host\s\+all\s\+all\s\+::1\/128\s\+scram-sha-256/host all all ::1\/128 trust/' /etc/postgresql/14/main/pg_hba.conf

# Create the Python virtual environment
RUN python3.11 -m venv /venv

# Auto-activate venv and cd into /app on shell login (mirrors Vagrantfile)
RUN echo 'source /venv/bin/activate' >> /root/.bashrc && \
    echo 'cd /app' >> /root/.bashrc

# Clean up apt caches
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements files and install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN . /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["bash"]
