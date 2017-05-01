Python 3.4, PostgreSQL 9.4+

Designed for hosting in AWS Elastic Beanstalk

## Local setup ##
TODO just run setup script
* `pip install -r requirements.txt`
* Install PostgreSQL, run `psql`:
    * `create user photo with password 'xxxx';`
    * `create database photo with owner photo;`
* Store password in POSTGRES_PHOTO_PASSWORD environmental variable
    * bash$ `export POSTGRES_PHOTO_PASSWORD='xxxx'`
* `python manage.py migrate`
* `python manage.py createsuperuser`
* `python manage.py runserver
`

    