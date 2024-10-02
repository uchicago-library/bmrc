# Black Metropolis Research Consortium (BMRC)
Website for the Black Metropolis Research Consortium, a Chicago-based membership association of libraries, universities, and other archival institutions.

Mocks for approval process can be found at: [uchicago-library.github.io/bmrc](https://uchicago-library.github.io/bmrc/)

## Documents (Only viewable to UChicago folks)
- [Website Outline](https://docs.google.com/document/d/1_VEq3KSWbJupeK4teEwiOB22VByQfsOGfSR58NHVGEA/edit?usp=sharing)
- [Page type and fields spreadsheet](https://docs.google.com/spreadsheets/d/1XU3JF7Jg0Jmz4B1g-nnjS_5EVP10BqgrcqcazXWHzLM/edit?usp=sharing)

## Running an Instance of the Site
1. Start the dev environment from the root of the project directory: `vagrant up`
2. ssh to the guest machine: `vagrant ssh`. The virualenv will automatically be activated and you will be dropped into the working directory.
3. Start the Django dev server: `./manage.py runserver 0.0.0.0:3000`

## Making Changes
- **Model Changes:** Run `python manage.py makemigrations`, then `python manage.py migrate` to update the database with your model changes. You must run the above commands each time you make changes to the model definition.
- **CSS and JS Changes:** Kill the server, `./manage.py collectstatic`, restart server
- **Other Errors:** Try running `pip install -r requirements.txt`
- **If running vagrant on local:** Installing pip packages & upgrades require adding package to requirements.txt, `vagrant destroy`, and `vagrant up` rather than the regular pip install method.

## Pushing to Production
- ssh to aerie
- `cd /data/aerie/ ; source venv3.9/bin/activate ; cd sites/bmrc/bmrc`
- `git remote update`
- `git status`
- `git pull origin master`
- `./manage.py migrate` _only needed if made migrations_
- `./manage.py compress`
- `./manage.py collectstatic`
- `sudo service apache24 restart`

## Pushing to the Test Site
The test instance should mirror the production site, less any features being tested at the time. The test server is bmrc-test ; it is hosted on crib
- ssh to crib
- `cd /data/crib/ ; source venv3.9/bin/activate ; cd sites/bmrc-test/bmrc`
- `git remote update`
- `git status`
- `git checkout {{ branch-name }}`
- `git pull origin {{ branch-name }}`
- `./manage.py migrate` _only needed if made migrations_
- `./manage.py compress`
- `./manage.py collectstatic`
- `sudo service apache24 restart`

### Caching Issues
If your changes aren't loading into production, try:
- Compress, collectstatic, and restart apache again
- Clear the Wagtail cache in Wagtail settings
- Clear the Django cache manually
```
./manage.py shell
from django.core.cache import cache
cache.clear()
```

### Making changes to the dev database
The dev database is loaded when the Vagrant image builds. If you need to create a new page and you want it to persist in the dev database, just generate fixtures and check them in:

```
./manage.py dumpdata > home/fixtures/dev.json
```

### Fixed Pages

The following URLs are hardcoded in templates. In cases where these URLs point
to editable Page objects, moving these pages will result in 404 errors.

- /news/
- /news/newsletter-signup/
- /news/support-bmrc/
- /portal/
- /portal/about/
- /portal/browse/
- /portal/curated/
- /portal/help/
- /portal/search/
- /portal/view/

# Search Portal

Site visitors can search and browse member finding aids using the website.
Currently the site accepts EAD 2002 finding aids only. Documents that do not
use the EAD namespace will be converted to a form that uses the namespace
when they're ingested. EAD 3 is currently not supported.

To facilitate browsing, the site uses MarkLogic Collections. Collections are
represented by URIs, e.g. https://bmrc.lib.uchicago.edu/topics/Jazz, and each
collection contains one or more finding aids. To browse all collections and
finding aids currently on the site, use the following management command:

```console
python manage.py browse https://bmrc.lib.uchicago.edu/
```

## MarkLogic Settings

See your local settings for database connection configuration.

### Connecting to our MarkLogic server from a dev machine

If you're running the site on a development machine, you'll need to set up a
tunnel for SSH connections. Run a command like the one below in a new console
window:

```console
ssh -D 9090 -q -C -N <cnetid>@<staff-host>.lib.uchicago.edu
```

### Loading new finding aids

Get the definitive locations of finding aids on disk from CB, the systems administrators, 
or BMRC staff. Note that this procedure will make the production site unusable for approximately
10 minutes. You should test this procedure in a test MarkLogic database before doing this on 
the production system. Coordinate an appropriate time to update production with BMRC staff. 

Copy all finding aids to a temporary location. Here, <finding_aid_dir> will contain a sequence
of subdirectories, one for each member institution. Each of those subdirectories will contain 
XML finding aids. 

```console
cp -R <finding_aid_dir> <temporary_finding_aid_dir>
```

Remove all non-xml files from that directory and use xmllint
--noout to confirm that all finding aids are well-formed XML.

Create a local directory of regularized finding aids (i.e., run
the regularize.xsl transform before loading.)

```console
python manage.py regularize_finding_aids <temporary_finding_aid_dir> <regularized_finding_aid_dir>
```

Delete all finding aids in the MarkLogic database:

```console
python manage.py delete-all-finding-aids
```

Then create browse indexes based on regularized finding aids and upload
everything to the server (this step takes a few minutes.)

```console
python manage.py load-finding-aids <regularized_finding_aid_dir>
```

## Portal Homepage

The portal homepage includes several content areas that change.

### Curated Topics and Featured Curated Topic

The featured curated topic changes automatically every week. To add new featured curated topics, add new child pages under /portal/curated/ in the Wagtail admin. To chnage the image that appears on the portal homepage for a specific curated
topic, edit the curated topic page.

### Exhibits and Featured Exhibit

The featured exhibit is set manually- to change it, log into the Wagtail admin and edit the portal home page. To add new featured exhibits, add child pages to /portal/exhibits/. To change the image that appears on the portal homepage for a specific featured
exhibit, edit the exhibit page.

### Topics and Featured Topic

The featured topic changes every time the portal homepage is reloaded. Featured topics are extracted from the database itself. To see how different EAD tags translate into specific topics, see the source code behind the load-finding-aids management command. The image that appears on the portal homepage is editable. Log into the Wagtail admin and look for images with the rollowing filenames:

- homepage_facet_image_decades.jpg
- homepage_facet_image_organizations.jpg
- hoempage_facet_image_people.jpg
- homepage_facet_image_places.jpg
- homepage_facet_image_topics.jpg

### Featured Archive
The portal homepage includes a featured archive which rotates automatically
once a month. Archives are editable in the Wagtail admin- see the "Archives"
section of the Wagtail admin sidebar. To change the rotation order, see the
order attribute of each object in the admin interface. The lowest order index
appears/appeared as the featured archive in February 2022. To see a report
of order indexes for all archives, see the following management command:

```console
python manage.py report-member-highlight-monthly-display
