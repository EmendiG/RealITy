import overpass
import folium
import numpy as np
import geopandas as gpd
import pandas as pd
import os
from geojson import Point, Feature, FeatureCollection, Polygon, MultiPolygon, dump

miastaDict = {'warszawa':'Warszawa', 'krakow':'Kraków', 'lodz':'Łódź', 'wroclaw':'Wrocław', 'poznan':'Poznań',
              'gdansk':'Gdańsk', 'szczecin':'Szczecin', 'bydgoszcz':'Bydgoszcz', 'lublin':'Lublin', 'bialystok':'Białystok'}

class District:
    def __init__(self, miasto):
        self.miasto = miasto
        self.responseCity = self.osmApi_getDistricts()

    def osmApi_getDistricts(self):
        api = overpass.API(timeout=60)
        QUERY = f"""area[name="{self.miasto}"][type="boundary"]->.city; 
        rel(area.city)[admin_level=9];
        out geom;"""
        responseCity = api.get(QUERY, responseformat='json')
        return responseCity


    def osmApi_getDistricts_getCoordinatesOfWays(self, odpowiedz):
        # Get Coordinates from OSM == only WAYS !!
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

    def osmApi_getDistricts_returnGeoDataFrame(self):

        dlugosc = len(list({dis['id']: dis for dis in self.responseCity['elements']}.values()))
        coordinates = []
        districts = []
        # append polygons and district names to proper lists
        for dzielnice in range(0, dlugosc):
            district = self.responseCity['elements'][dzielnice]['tags']['name']
            odpowiedz = []
            for num, ref in enumerate(self.responseCity['elements'][dzielnice]['members']):
                if ref['role'] == 'outer' and ref['type'] == 'way':
                    odpowiedz.append(ref)
            coords = self.osmApi_getDistricts_getCoordinatesOfWays(odpowiedz)
            coordinates.append(coords)
            districts.append(district)

        # make geojsons from lists of coordinates and names of districts, to be viable by the GeoPandas
        def coordinates_toGeoJson(coordinates, districts):
            geojson = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "name": district,
                            "coordinates": [coordinates[n]],
                        },
                        "properties": {'name': district},
                    } for n, district in enumerate(districts)]
            }
            return geojson

        geojson = coordinates_toGeoJson(coordinates, districts)
        gdf = gpd.GeoDataFrame.from_features(geojson)
        return  gdf


    def osmApi_getDistricts_mapPolygons(self):
        # Get Polygons  = districts wihin a city (miasto) and draw it on a map

        dlugosc = len(list({dis['id']: dis for dis in self.responseCity['elements']}.values()))
        # set up base coordinates for folium.Map.__init__ before appending polygons to gjson
        coordynatLat = []
        coordynatLon = []
        for dzielnice in range(0, dlugosc):
            for cLatLon in self.responseCity['elements'][dzielnice]['members']:
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
            for num, ref in enumerate(self.responseCity['elements'][dzielnice]['members']):
                if ref['role'] == 'outer' and ref['type'] == 'way':
                    odpowiedz.append(ref)
            coords = self.osmApi_getDistricts_getCoordinatesOfWays(odpowiedz)

            district = self.responseCity['elements'][dzielnice]['tags']['name']
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

        current_directory = os.getcwd()
        target_directory = os.path.join(current_directory, r'districts')
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        map.save(f"districts/{self.miasto}.html")


class Amenities:
    def __init__(self, miasto):
        self.miastoDict = miastaDict[miasto]
        self.miasto = miasto
        self.amenitiesInCity = self.osmApi_getAmmenities()
        self.tourismInCity = self.osmApi_getTourism()       # to chyba nie tu?

    def osmApi_getAmmenities(self):
        api = overpass.API(timeout=60)
        QUERY = f"""area[name="{self.miastoDict}"][type="boundary"]->.city; 
        node(area.city)["amenity"];
        out geom;"""
        return api.get(QUERY, responseformat='json')

    def osmApi_getTourism(self):
        api = overpass.API(timeout=60)
        QUERY = f"""area[name="{self.miastoDict}"][type="boundary"]->.city; 
        node(area.city)["tourism"];
        out geom;"""
        return api.get(QUERY, responseformat='json')

    def osmApi_getAmmenities_parseDataToDataFrame(self):

        amenities_df = pd.DataFrame(columns = ['Ident', 'Amenity', 'Longitude', 'Latitude', 'Name', 'Miasto'])
        # Chosen types of amenities by importance
        amenities_CHOSEN = ['bar', 'pub', 'restaurant', 'fast_food', 'cafe', 'nightclub', 'pharmacy', 'hospital',
                            'doctors','dentist', 'clinic', 'bank', 'bicycle_rental', 'post_office', 'kindergarten',
                            'school', 'library', 'university', 'college', 'theatre', 'arts_centre', 'cinema', 'police']

        # Two types of amenities has special json properties
        amenities_CHOSEN_exception = ['vending_machine', 'atm']
        # Check if amenities don't overwrite itself with SQL server data
        amenities_df_IDENTS = [ident for ident in amenities_df['Ident']] # TODO: Add sql import
        amenities_NUMBER = len(self.amenitiesInCity['elements'])

        for n, amenity in enumerate(self.amenitiesInCity['elements']):
            if n%1000 == 0:
                print("%.0f" % round(n/amenities_NUMBER*100, 0), '%')
            for CHOSEN in amenities_CHOSEN:
                if amenity['tags']['amenity'] == CHOSEN and amenity['id'] not in amenities_df_IDENTS:
                    if 'name' in amenity['tags']:
                        amenities_df = amenities_df.append(
                            {'Ident': amenity['id'],
                             'Amenity': CHOSEN,
                             'Latitude': round(amenity['lat'], 5),
                             'Longitude': round(amenity['lon'], 5),
                             'Name': amenity['tags']['name'],
                             'Miasto':self.miasto}, ignore_index=True)
                    elif 'name:en' in amenity['tags'] and 'name' not in amenity['tags']:
                        amenities_df = amenities_df.append(
                            {'Ident': amenity['id'],
                             'Amenity': CHOSEN,
                             'Latitude': round(amenity['lat'], 5),
                             'Longitude': round(amenity['lon'], 5),
                             'Name': amenity['tags']['name:en'],
                             'Miasto':self.miasto}, ignore_index=True)
                    else:
                        amenities_df = amenities_df.append(
                            {'Ident': amenity['id'],
                             'Amenity': CHOSEN,
                             'Latitude': round(amenity['lat'], 5),
                             'Longitude': round(amenity['lon'], 5),
                             'Name': 'NaN',
                             'Miasto':self.miasto}, ignore_index=True)

            if amenity['tags']['amenity'] == amenities_CHOSEN_exception[0] and amenity['id'] not in amenities_df_IDENTS:
                if 'vending' in amenity['tags']:
                    if 'parcel_pickup' in amenity['tags']['vending']:
                        try:
                            amenities_df = amenities_df.append(
                                {'Ident': amenity['id'],
                                 'Amenity': amenities_CHOSEN_exception[0],
                                 'Latitude': round(amenity['lat'], 5),
                                 'Longitude': round(amenity['lon'], 5),
                                 'Name': amenity['tags']['operator'] ,
                                 'Miasto':self.miasto}, ignore_index=True)
                        except:
                            try:
                                amenities_df = amenities_df.append(
                                    {'Ident': amenity['id'],
                                     'Amenity': amenities_CHOSEN_exception[0],
                                     'Latitude': round(amenity['lat'], 5),
                                     'Longitude': round(amenity['lon'], 5),
                                     'Name': amenity['tags']['name'],
                                     'Miasto':self.miasto}, ignore_index=True)
                            except:
                                amenities_df = amenities_df.append(
                                    {'Ident': amenity['id'],
                                     'Amenity': amenities_CHOSEN_exception[0],
                                     'Latitude': round(amenity['lat'], 5),
                                     'Longitude': round(amenity['lon'], 5),
                                     'Name': 'NaN',
                                     'Miasto':self.miasto},
                                    ignore_index=True)
            elif amenity['tags']['amenity'] == amenities_CHOSEN_exception[1] and amenity['id'] not in amenities_df_IDENTS:
                try:
                    amenities_df = amenities_df.append(
                        {'Ident': amenity['id'],
                         'Amenity': amenities_CHOSEN_exception[1],
                         'Latitude': round(amenity['lat'], 5),
                         'Longitude': round(amenity['lon'], 5),
                         'Name': amenity['tags']['operator'],
                         'Miasto':self.miasto}, ignore_index=True)
                except:
                    try:
                        amenities_df = amenities_df.append(
                            {'Ident': amenity['id'],
                             'Amenity': amenities_CHOSEN_exception[1],
                             'Latitude': round(amenity['lat'], 5),
                             'Longitude': round(amenity['lon'], 5),
                             'Name': amenity['tags']['name'],
                             'Miasto':self.miasto}, ignore_index=True)
                    except:
                        amenities_df = amenities_df.append(
                            {'Ident': amenity['id'],
                             'Amenity': amenities_CHOSEN_exception[1],
                             'Latitude': round(amenity['lat'], 5),
                             'Longitude': round(amenity['lon'], 5),
                             'Name': 'NaN',
                             'Miasto':self.miasto}, ignore_index=True)
        return amenities_df


# TODO: Ogarnac koordynaty amenities z Openmaps i Geoportal
