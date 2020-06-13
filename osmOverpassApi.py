import overpass
import folium
import numpy as np
from geojson import Point, Feature, FeatureCollection, Polygon, MultiPolygon, dump


class District:
    def __init__(self, miasto):
        self.miasto = miasto

    def get_districts_osmApi(self):
        api = overpass.API(timeout=60)
        QUERY = f"""area[name="{self.miasto}"][type="boundary"]->.city; 
        rel(area.city)[admin_level=9];
        out geom;"""
        responseCity = api.get(QUERY, responseformat='json')
        return responseCity

    # Get Coordinates from OSM == only WAYS !!
    def getCoordinatesFromOSM_ways_districts(self, odpowiedz):
        matchingCounter = len(odpowiedz) - 1
        coords = []
        for nmb, geometry in enumerate(odpowiedz):
            if nmb == 0:
                coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry['geometry']]
        while matchingCounter > 0:
            for nmb, geometry in enumerate(odpowiedz):
                if nmb > 0:
                    koordynat_0 = coords[-1][0]
                    koordynat_1 = coords[-1][1]
                    # check if last coordinates in osm.way are similar to first coordinates in next osm.way
                    if koordynat_0 == odpowiedz[nmb]['geometry'][0]['lon'] and koordynat_1 == \
                            odpowiedz[nmb]['geometry'][0]['lat']:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry['geometry']]
                        matchingCounter -= 1
                    # check reverse osm.way if first condition is not true
                    elif koordynat_0 == odpowiedz[nmb]['geometry'][len(odpowiedz[nmb]['geometry']) - 1][
                        'lon'] and koordynat_1 == \
                            odpowiedz[nmb]['geometry'][len(odpowiedz[nmb]['geometry']) - 1]['lat']:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry['geometry'][::-1]]
                        matchingCounter -= 1
        return coords


    # Get Polygons  = districts wihin a city (miasto) and draw it on a map
    def mapDistrictsPolygons(self):
        responseCity = self.get_districts_osmApi()
        dlugosc = len(list({dis['id']: dis for dis in responseCity['elements']}.values()))

        # set up base coordinates for folium.Map.__init__ before appending polygons to gjson
        coordynatLat = []
        coordynatLon = []
        for dzielnice in range(0, dlugosc):
            for cLatLon in responseCity['elements'][dzielnice]['members']:
                if 'geometry' in cLatLon:
                    coordynatLat.append(cLatLon['geometry'][0]['lat'])
                    coordynatLon.append(cLatLon['geometry'][0]['lon'])
        coordynat = (np.mean(coordynatLat), np.mean(coordynatLon))

        map = folium.Map(
            location=coordynat,
            zoom_start=11
        )

        # append polygons to gjson and then to map
        for dzielnice in range(0, dlugosc):
            odpowiedz = []
            for num, ref in enumerate(responseCity['elements'][dzielnice]['members']):
                if ref['role'] == 'outer' and ref['type'] == 'way':
                    odpowiedz.append(ref)
            coords = self.getCoordinatesFromOSM_ways_districts(odpowiedz)

            district = responseCity['elements'][dzielnice]['tags']['name']
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "name": district,
                            "coordinates": [[[d[0], d[1]] for d in coords]],
                        },
                        "properties": {'name': district},
                    }]
            }
            folium.GeoJson(geojson).add_to(map)
            #folium.FeatureGroup(name=district).add_to(map)
        folium.LayerControl().add_to(map)
        map.save(f"districts/{self.miasto}.html")






        #multi1 = MultiPolygon(coords)
        #poly1 = Polygon(multi1)
        #multi2 = MultiPolygon(poly1)
        #features.append(Feature(geometry=multi2))

        #with open('test_cord.geojson', 'w', encoding='utf-8') as file:
        #    feature_collection = FeatureCollection(features)
        #    dump(feature_collection, file)

        #coordynat = [coords[0][1], coords[0][0]]
        #map = folium.Map(
        #    location=coordynat,
        #    zoom_start=10
        #)

        #folium.GeoJson('test_cord.geojson').add_to(map)
        #folium.LayerControl().add_to(map)
        #map.save(f"districts/{self.miasto}.html")
        #return map
