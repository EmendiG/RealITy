# RealITy

- Get data from otodom.pl "real estate / flat / sale"
- Get data from gratka.pl "real estate / flat / sale"
- Merge filtered data into one database, dmbs= PostgreSQL
- Added OpenStreetMap API to get Districts (Polygons), Amenities, Tourism, Leisture (Nodes, Ways, Rels)
- Possible to send geometry to PostgreSQL (needed PostGIS extension - installed manualy)
- Machine Learning alorithms predict price per square meter based on processed data (testing accuracy 70-74%, evaluations are based on a offer price NOT transaction price!)
