# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  # https://app.vagrantup.com/ubuntu/boxes/jammy64
  config.vm.box = "ubuntu/jammy64"
  config.vm.box_version = "20230720.0.0"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # NOTE: This will enable public access to the opened port
  config.vm.network "forwarded_port", guest: 3000, host: 3000

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine and only allow access
  # via 127.0.0.1 to disable public access
  # config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
    # Customize the amount of memory on the VM:
    vb.memory = "4096"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

    PROJECT_DIR=/vagrant
    VIRTUALENV_DIR=/home/vagrant/bmrc
    PYTHON=$VIRTUALENV_DIR/bin/python
    VAGRANT_HOME=/home/vagrant

    # Create the django error log
    echo ""
    echo "=========== Creating /var/log/django-errors.log ==========="
    touch /var/log/django-errors.log
    chown vagrant /var/log/django-errors.log
    chgrp vagrant /var/log/django-errors.log

    # Install dependencies
    echo ""
    echo "=========== Installing dependencies ===========" 
    apt-get update
    apt-get install -y postgresql libpq-dev python3-pip python3.10-dev python3.10-distutils python3.10-venv

    # Create a Postgres user and database
    su - postgres -c "createuser -s vagrant"
    sudo -u postgres createdb -O vagrant bmrc_dev

    # Create a Python virtualenv
    echo ""
    echo "=========== Creating a Python virtualenv ==========="
    echo "..."
    cd /home/vagrant && python3 -m venv bmrc

    echo ""
    echo "============== Installing linting and dev tools =============="
    apt-get install -y vim git curl gettext build-essential
    mkdir -p $VAGRANT_HOME/.vim/pack/git-plugins/start
    git clone --depth 1 https://github.com/dense-analysis/ale.git $VAGRANT_HOME/.vim/pack/git-plugins/start/ale
    apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libllvm11
    apt-get install -y postgresql libpq-dev
    touch $VAGRANT_HOME/.vimrc
    echo "let g:ale_linters_explicit = 1" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_linters = { 'python': ['flake8'], 'javascript': ['eslint'] }" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_python_flake8_options = '--ignore=D100,D101,D202,D204,D205,D400,D401,E303,E501,W503,N805,N806'" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_fixers = { 'python': ['isort', 'autopep8', 'black'], 'javascript': ['eslint'] }" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_python_black_options = '--skip-string-normalization'" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_python_isort_options = '--profile black'" >> $VAGRANT_HOME/.vimrc


    # Pip install project dependencies
    echo ""
    echo "=========== Pip installing project dependencies ==========="
    source bmrc/bin/activate && cd /vagrant/ && pip install -r requirements.txt && pip install -r requirements-dev.txt

    # Run migrations, load the dev db and build a search index
    echo ""
    echo "=========== Running django migrations and loading the dev database ==========="
    su - vagrant -c "$PYTHON $PROJECT_DIR/manage.py migrate --noinput && \
                     $PYTHON $PROJECT_DIR/manage.py loaddata /vagrant/home/fixtures/dev.json"

    # Add some dev sweetness
    echo ""
    echo "============== Simplicity for developers =============="
    echo "..."
    echo "source bmrc/bin/activate" >> /home/vagrant/.bashrc
    echo "cd /vagrant/" >> /home/vagrant/.bashrc
  SHELL
end
