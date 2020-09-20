# RealITy

- Get data from otodom.pl "real estate / flat / sale"
- Get data from gratka.pl  ==||==
- Get data from morizon.pl ==||==
- Merge filtered data into one database, dmbs= PostgreSQL
- Added OpenStreetMap API to get Districts (Polygons), Amenities, Tourism, Leisture (Nodes, Ways, Rels)
- Possible to send geometry to PostgreSQL (needed PostGIS installed inside docker db container)
- Machine Learning alorithms predict price per square meter based on processed data (testing accuracy 72-80%, evaluations are based on a offer price NOT transaction price!)
- Django framework + Docker


  Docker commands:
> docker build --force-rm -t realityweb:latest . <br/>
> docker-compose up -d --remove-orphans <br/>
> docker-compose run website python manage.py makemigrations <br/>
> (when setting up for first time, volumes should reloaded because of .sql file that is sourced)
