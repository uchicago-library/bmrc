# Black Metropolis Research Consortium (BMRC)
Website for the Black Metropolis Research Consortium, a Chicago-based membership association of libraries, universities, and other archival institutions.

Mocks for approval process can be found at: [uchicago-library.github.io/bmrc](https://uchicago-library.github.io/bmrc/)

## Documents (Only viewable to UChicago folks)
- [Website Outline](https://docs.google.com/document/d/1_VEq3KSWbJupeK4teEwiOB22VByQfsOGfSR58NHVGEA/edit?usp=sharing)
- [Page type and fields spreadsheet](https://docs.google.com/spreadsheets/d/1XU3JF7Jg0Jmz4B1g-nnjS_5EVP10BqgrcqcazXWHzLM/edit?usp=sharing)

## Running an Instance of the Site
1. Start the dev environment from the root of the project directory: `vagrant up`
5. ssh to the guest machine: `vagrant ssh`
6. Activate the virualenv and navigate to the root directory: `source bmrc/bin/activate && cd /vagrant/`
7. Start the Django dev server: `./manage.py runserver 0.0.0.0:3000`

## Making Changes
- **Model Changes:** Run `python manage.py makemigrations`, then `python manage.py migrate` to update the database with your model changes. You must run the above commands each time you make changes to the model definition.
- **Other Errors:** Try running `pip install -r requirements.txt`
