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

    # Get Polygons  = districts wihin a city (miasto) and draw it on a map
    def OLD_DONT_USE(self):
        responseCity = self.get_districts_osmApi()
        dlugosc = len(list({dis['id']: dis for dis in responseCity['elements']}.values()))
        features = []
        for dzielnice in range(0, dlugosc):
            coords = []
            toMatchList = []
            # check if first value in json is node or way
            if responseCity['elements'][dzielnice]['members'][0]['type'] == 'node':
                # if first is node then whole program start from 1
                start_n = 1
            else:
                start_n = 0
            star_n = []
            for numcio, start in enumerate(responseCity['elements'][dzielnice]['members']):
                if start['type'] == 'way':
                    star_n.append(numcio)
            start_n = star_n[0]

            for num, ref in enumerate(responseCity['elements'][dzielnice]['members']):
                # append first openstreetmap/way (that is start for future appendings)
                if ref['role'] == 'outer' and num == start_n:
                    if ref['geometry'][len(ref['geometry']) - 1] == \
                            responseCity['elements'][dzielnice]['members'][num + 1]['geometry'][0]:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in ref['geometry']]
                    else:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in ref['geometry'][::-1]]

                if ref['role'] == 'outer' and num > start_n:
                    toMatchList.append(ref['geometry'])

            # because, many ways are not properly arranged (one after the other) and way's last coordinates are
            # not always identical to the next coordinates, it is necessary to rearrange them, one by one
            matchingCounter = len(toMatchList)
            while matchingCounter > 0:
                for nmb, geometry in enumerate(toMatchList):
                    koordynat_0 = coords[-1][0]
                    koordynat_1 = coords[-1][1]
                    if koordynat_0 == geometry[0]['lon'] and koordynat_1 == geometry[0]['lat']:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry]
                        matchingCounter -= 1
                    elif koordynat_0 == geometry[len(geometry) - 1]['lon'] and koordynat_1 == \
                            geometry[len(geometry) - 1]['lat']:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry[::-1]]
                        matchingCounter -= 1

            # many multi and single polygons wrapped, cuz folium reads min  3x[]
            multi1 = MultiPolygon(coords)
            poly1 = Polygon(multi1)
            multi2 = MultiPolygon(poly1)
            features.append(Feature(geometry=multi2))

        with open('test_cord.geojson', 'w', encoding='utf-8') as file:
            feature_collection = FeatureCollection(features)
            dump(feature_collection, file)
        coordynat = [coords[0][1], coords[0][0]]

        map = folium.Map(
            location=coordynat,
            zoom_start=10
        )

        folium.GeoJson('test_cord.geojson').add_to(map)
        folium.LayerControl().add_to(map)
        map.save(f"{self.miasto}.html")
        return map

    def mapDistrictPolygons(self):
        responseCity = self.get_districts_osmApi()
        dlugosc = len(list({dis['id']: dis for dis in responseCity['elements']}.values()))

        # set up base coordinates for folium.Map.__init__ befor appending gjson
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

        for dzielnice in range(0, dlugosc):
            odpowiedz = []
            for num, ref in enumerate(responseCity['elements'][dzielnice]['members']):
                if ref['role'] == 'outer' and ref['type'] == 'way':
                    odpowiedz.append(ref)
            coords = self.getCoordinatesFromOSM_Districts(odpowiedz)

            district = 'lol'
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
        map.save(f"districts/{self.miasto}.html")

    def getCoordinatesFromOSM_Districts(self, odpowiedz):

        #features = []
        #for dzielnice in range(0, dlugosc):
        #odpowiedz = []
        #coords = []
        #for num, ref in enumerate(responseCity['elements'][dzielnice]['members']):
        #    if ref['role'] == 'outer' and ref['type'] == 'way':
        #        odpowiedz.append(ref)
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
                    if koordynat_0 == odpowiedz[nmb]['geometry'][0]['lon'] and koordynat_1 == \
                            odpowiedz[nmb]['geometry'][0]['lat']:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry['geometry']]
                        matchingCounter -= 1
                    elif koordynat_0 == odpowiedz[nmb]['geometry'][len(odpowiedz[nmb]['geometry']) - 1][
                        'lon'] and koordynat_1 == \
                            odpowiedz[nmb]['geometry'][len(odpowiedz[nmb]['geometry']) - 1]['lat']:
                        coords += [(float(geom['lon']), float(geom['lat'])) for geom in geometry['geometry'][::-1]]
                        matchingCounter -= 1

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
        return coords




