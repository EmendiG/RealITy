import overpass
import folium
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import PostgreSQLModifier
from shapely.geometry import Polygon, MultiPolygon

miastaDict = {'warszawa': 'Warszawa', 'krakow': 'Kraków', 'lodz': 'Łódź', 'wroclaw': 'Wrocław', 'poznan': 'Poznań',
              'gdansk': 'Gdańsk', 'szczecin': 'Szczecin', 'bydgoszcz': 'Bydgoszcz', 'lublin': 'Lublin',
              'bialystok': 'Białystok'}


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

    def osmApi_getDistricts_returnGeoDataFrame_getCoordinatesOfWays(self, odpowiedz):
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
            coords = self.osmApi_getDistricts_returnGeoDataFrame_getCoordinatesOfWays(odpowiedz)
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
        return gdf

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
            coords = self.osmApi_getDistricts_returnGeoDataFrame_getCoordinatesOfWays(odpowiedz)

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

            # folium.FeatureGroup(name=district).add_to(map)

        folium.LayerControl().add_to(map)

        current_directory = os.getcwd()
        target_directory = os.path.join(current_directory, r'districts')
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)
        map.save(f"districts/{self.miasto}.html")


class MapFeatures:
    def __init__(self, miasto, feature, type, autoselection):
        self.miastoDict = miastaDict[miasto]
        self.miasto = miasto
        self.feature = feature
        self.type = type
        self.typeLower = type.lower()
        self.featureLower = feature.lower()
        self.getFeature = self.osmApi_getFeature()
        self.autoselection = autoselection

    def osmApi_getFeature(self):
        try:
            api = overpass.API(timeout=60)
            QUERY = f"""area[name="{self.miastoDict}"][type="boundary"]->.city; 
            {self.typeLower}(area.city)["{self.featureLower}"];
            out geom;"""
            return api.get(QUERY, responseformat='json')
        except overpass.errors.MultipleRequestsError:
            api = overpass.API(timeout=60, url='//overpass.openstreetmap.fr/api/')
            QUERY = f"""area[name="{self.miastoDict}"][type="boundary"]->.city; 
                        {self.typeLower}(area.city)["{self.featureLower}"];
                        out geom;"""
            return api.get(QUERY, responseformat='json')

    def osmApi_getFeature_showFeatures(self):
        featureDict = {}
        for element in self.getFeature['elements']:
            if element['tags'][self.featureLower] not in featureDict.keys():
                featureDict[element['tags'][self.featureLower]] = 1
            elif element['tags'][self.featureLower] in featureDict.keys():
                featureDict[element['tags'][self.featureLower]] += 1
        sortedfeatureDict = {k: v for k, v in sorted(featureDict.items(), key=lambda item: item[1], reverse=True)}
        return sortedfeatureDict


    def osmApi_getAmenities_parseToDataFrame_nodes(self):

        amenities_df = pd.DataFrame(columns=['Ident', 'Amenity', 'Longitude', 'Latitude', 'Name', 'Miasto'])
        if self.autoselection == True:
            if self.feature == 'Amenity':
                amenities_CHOSEN = ['bar', 'pub', 'restaurant', 'fast_food', 'cafe', 'nightclub', 'pharmacy',
                                    'hospital', 'doctors', 'dentist', 'clinic', 'bank', 'bicycle_rental', 'post_office',
                                    'kindergarten', 'school', 'library', 'university', 'college', 'theatre',
                                    'arts_centre', 'cinema', 'police']
                # Two types of amenities has special json properties
                amenities_CHOSEN_exception = ['vending_machine', 'atm']
        else:
            print(self.osmApi_getFeature_showFeatures())
            amenities__INPUT = input('Enter a list of features separated by space = ')
            amenities_CHOSEN = amenities__INPUT.split()

        # Check if amenities don't overwrite itself with SQL server data
        amenities_df_IDENTS = PostgreSQLModifier.osmApi_DataFrame_FromSQL(self.feature, self.type)
        amenities_NUMBER = len(self.getFeature['elements'])

        for n, amenity in enumerate(self.getFeature['elements']):
            if n % 1000 == 0:
                print("%.0f" % round(n / amenities_NUMBER * 100, 0), '%')
            for CHOSEN in amenities_CHOSEN:
                if amenity['tags']['amenity'] == CHOSEN and amenity['id'] not in amenities_df_IDENTS:
                    if 'name' in amenity['tags']:
                        name = amenity['tags']['name']
                    elif 'name:en' in amenity['tags'] and 'name' not in amenity['tags']:
                        name = amenity['tags']['name:en']
                    else:
                        name = 'NaN'
                    amenities_df_IDENTS.append(amenity['id'])
                    amenities_df = amenities_df.append(
                        {'Ident': amenity['id'],
                         'Amenity': CHOSEN,
                         'Latitude': round(amenity['lat'], 5),
                         'Longitude': round(amenity['lon'], 5),
                         'Name': name,
                         'Miasto': self.miasto}, ignore_index=True)

            if amenity['tags']['amenity'] == amenities_CHOSEN_exception[0] and amenity['id'] not in amenities_df_IDENTS:
                if 'vending' in amenity['tags']:
                    if 'parcel_pickup' in amenity['tags']['vending']:
                        try:
                            name = amenity['tags']['operator']
                        except:
                            try:
                                name = amenity['tags']['name']
                            except:
                                name = 'NaN'
                        amenities_df_IDENTS.append(amenity['id'])
                        amenities_df = amenities_df.append(
                            {'Ident': amenity['id'],
                             'Amenity': amenities_CHOSEN_exception[0],
                             'Latitude': round(amenity['lat'], 5),
                             'Longitude': round(amenity['lon'], 5),
                             'Name': name,
                             'Miasto': self.miasto},
                            ignore_index=True)
            elif amenity['tags']['amenity'] == amenities_CHOSEN_exception[1] and amenity[
                'id'] not in amenities_df_IDENTS:
                try:
                    name = amenity['tags']['operator']
                except:
                    try:
                        name = amenity['tags']['name']
                    except:
                        name = 'NaN'
                amenities_df_IDENTS.append(amenity['id'])
                amenities_df = amenities_df.append(
                    {'Ident': amenity['id'],
                     'Amenity': amenities_CHOSEN_exception[1],
                     'Latitude': round(amenity['lat'], 5),
                     'Longitude': round(amenity['lon'], 5),
                     'Name': name,
                     'Miasto': self.miasto}, ignore_index=True)
        return amenities_df

    def osmApi_getFeature_parseToDataFrame_nodes(self):
        # Function dedicated to features other than Amenities such as Tourism or Leisure (IMPORTANT = ONLY NODES)
        feature_df = pd.DataFrame(columns=['Ident', self.feature, 'Longitude', 'Latitude', 'Name', 'Miasto'])
        # Chosen types of amenities by importance

        if self.autoselection == True:
            if self.feature == 'Tourism':
                feature__CHOSEN = ['attraction', 'hotel', 'viewpoint', 'museum', 'artwork']
            elif self.feature == 'Leisure':
                feature__CHOSEN = ['playground', 'sports_centre', 'fitness_centre']
        else:
            print(self.osmApi_getFeature_showFeatures())
            feature__INPUT = input('Enter a list of features separated by space = ')
            feature__CHOSEN = feature__INPUT.split()


        feature_NUMBER = len(self.getFeature['elements'])
        # Check if amenities don't overwrite itself with SQL server data
        feature_df_IDENTS = PostgreSQLModifier.osmApi_DataFrame_FromSQL(self.feature, self.type)

        for n, featur in enumerate(self.getFeature['elements']):
            if n % 100 == 0:
                print("%.0f" % round(n / feature_NUMBER * 100, 0), '%')
            # noinspection PyUnboundLocalVariable
            for CHOSEN in feature__CHOSEN:
                if featur['tags'][f'{self.featureLower}'] == CHOSEN and featur['id'] not in feature_df_IDENTS:
                    if 'name' in featur['tags']:
                        name = featur['tags']['name']
                    elif 'name:en' in featur['tags'] and 'name' not in featur['tags']:
                        name = featur['tags']['name:en']
                    else:
                        name = 'NaN'
                    feature_df_IDENTS.append(featur['id'])
                    feature_df = feature_df.append(
                        {'Ident': featur['id'],
                         f'{self.feature}': CHOSEN,
                         'Latitude': round(featur['lat'], 5),
                         'Longitude': round(featur['lon'], 5),
                         'Name': name,
                         'Miasto': self.miasto}, ignore_index=True)
        return feature_df

    def osmApi_getFeature_parseToDataFrame_ways(self):
        # Function dedicated to features other than Amenities such as Tourism or Leisure (IMPORTANT = ONLY NODES)
        feature_df = pd.DataFrame(columns=['Ident', self.feature, 'Longitude', 'Latitude', 'Name', 'Miasto'])

        if self.autoselection == True:
            if self.feature == 'Leisure':
                feature__CHOSEN = ['playground']
        else:
            print(self.osmApi_getFeature_showFeatures())
            feature__INPUT = input('Enter a list of features separated by space = ')
            feature__CHOSEN = feature__INPUT.split()

        feature_NUMBER = len(self.getFeature['elements'])
        # Check if amenities don't overwrite itself with SQL server data
        feature_df_IDENTS = PostgreSQLModifier.osmApi_DataFrame_FromSQL(self.feature, self.type)

        for n, featur in enumerate(self.getFeature['elements']):
            if n % 100 == 0:
                print("%.0f" % round(n / feature_NUMBER * 100, 0), '%')
            # noinspection PyUnboundLocalVariable
            for CHOSEN in feature__CHOSEN:
                if featur['tags'][f'{self.featureLower}'] == CHOSEN and featur['id'] not in feature_df_IDENTS:
                    if 'name' in featur['tags']:
                        name = featur['tags']['name']
                    elif 'name:en' in featur['tags'] and 'name' not in featur['tags']:
                        name = featur['tags']['name:en']
                    else:
                        name = 'NaN'
                    feature_df_IDENTS.append(featur['id'])
                    feature_df = feature_df.append(
                        {'Ident': featur['id'],
                         f'{self.feature}': CHOSEN,
                         'Latitude': round(featur['geometry'][0]['lat'], 5),
                         'Longitude': round(featur['geometry'][0]['lon'], 5),
                         'Name': name,
                         'Miasto': self.miasto}, ignore_index=True)  # first lat/lon value is enough, those are small objects
        return feature_df

    def osmApi_getFeature_parseToDataFrame_rels(self):

        if self.autoselection == True:
            if self.feature == 'Leisure':
                feature__CHOSEN = ['park', 'nature_reserve']
        else:
            print(self.osmApi_getFeature_showFeatures())
            feature__INPUT = input('Enter a list of features separated by space = ')
            feature__CHOSEN = feature__INPUT.split()
        #feature_df_IDENTS = PostgreSQLModifier.osmApi_DataFrame_FromSQL(self.feature, self.type)
        feature_df_IDENTS = []

        arr_base = np.empty((0, 5), float)
        for feature in self.getFeature['elements']:
            for CHOSEN in feature__CHOSEN:
                if feature['tags']['leisure'] == CHOSEN and feature['id'] not in feature_df_IDENTS:
                    for member in feature['members']:
                        koords = []
                        if member['role'] == 'outer' and feature['tags'][
                            'type'] == 'multipolygon' and 'geometry' in member:
                            if len(member['geometry']) > 3:
                                if 'name' in feature['tags']:
                                    name = feature['tags']['name']
                                else:
                                    name = 'NaN'
                                koords += [(elem['lon'], elem['lat']) for elem in member['geometry']]
                                arr_base = np.concatenate(
                                    (arr_base, [[feature['id'], CHOSEN, MultiPolygon([Polygon(koords)]), name, self.miasto]]),
                                    axis=0)

        arr_final = np.array(['Ident', 'Leisure', 'Geometry', 'Name', 'Miasto'])
        for n, identyfikator in enumerate(arr_base):
            if n < len(arr_base) - 1:
                if arr_base[n][0] == arr_base[n + 1][0]:
                    arr_base[n + 1][2] = arr_base[n][2].union(arr_base[n + 1][2])
                else:
                    arr_final = np.vstack((arr_final, arr_base[n]))
            else:
                arr_final = np.vstack((arr_final, arr_base[n]))
        feature_df = pd.DataFrame(data=arr_final[1:, 0:],  columns=arr_final[0,0:])
        return gpd.GeoDataFrame(feature_df, crs="EPSG:4326", geometry='Geometry')



# TODO: Ogarnac koordynaty amenities z Openmaps i Geoportal
