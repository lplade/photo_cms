## Requirements ##
* [Python 3.4](https://www.python.org/downloads/release/python-346/)
* [PostgreSQL 9.4+](https://www.postgresql.org/download/) In Debian and 
derivatives, make sure postgresql-contrib is installed, it contains hstore
support
* Pillow dependencies:
    * [libjpeg-dev](http://libjpeg.sourceforge.net/)
    * [libtiff-dev](http://www.libtiff.org/)
    * [zlib1g-dev](http://zlib.net/)
    * [lcms2-dev](http://www.littlecms.com/)
    * [libfreetype6-dev](https://www.freetype.org/)

Designed for hosting in AWS Elastic Beanstalk

## Local setup ##
TODO just run setup script
* `pip install -r requirements.txt`
* Install PostgreSQL, run `psql`:
    * `create user photo with password 'xxxx';`
    * `create database photo with owner photo;`
    * `\c photo`
    * `create extension if not exists hstore;`
* Store password in POSTGRES_PHOTO_PASSWORD environmental variable
    * bash$ `export POSTGRES_PHOTO_PASSWORD='xxxx'`
* `python manage.py migrate`
* `python manage.py collectstatic`
* `python manage.py createsuperuser`
* `python manage.py runserver
`

    