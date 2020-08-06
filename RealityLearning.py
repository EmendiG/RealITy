import pandas as pd
import numpy as np
import PostgreSQLModifier
import re
import gzip
import sys
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from time import time
from sklearn.preprocessing import StandardScaler, Normalizer, RobustScaler
from sklearn.compose import TransformedTargetRegressor
from sklearn.pipeline import FeatureUnion

class MachineLearningRealEstatePrices:
    def __init__(self, miasto, db_features='oferty_merged_features_featuresN'):
        self.miasto = miasto
        self.db_features = db_features

    def MLREP_getDataFrame(self):
        conn = PostgreSQLModifier.PostgreSQL_connectSQLalchemy()
        df_consolidated = pd.read_sql(sql=f"{self.db_features}", con=conn)
        return df_consolidated.loc[df_consolidated['Miasto'] == self.miasto]

    def MLREP_getDataFrame_adjustments(self):
        df_consolidated = self.MLREP_getDataFrame()

        ok_indeksy = []
        for index, row in df_consolidated.iterrows():
            if 6000 < row['Price_per_metr'] < 24000:
                ok_indeksy.append(index)
        df_consolidated = df_consolidated.iloc[df_consolidated.index.isin(ok_indeksy)]

        df_opis = df_consolidated.loc[:, ['Ident', 'Opis']]
        splitter = re.compile(r'[^ąąćęńłóóśśżżź\w]+')
        isnumber = re.compile(r'[0-9]')

        f = gzip.open('odm.txt.gz', 'rt', encoding='utf-8')
        dictionary = {}
        set_dict = set()

        for x in f:
            t = x.strip().split(',')
            tt = [x.strip().lower() for x in t]
            for w in tt:
                set_dict.add(w)
                dictionary[w] = tt[0]

        def lematize(w):
            w = w.replace('ą', 'ą')
            w = w.replace('ó', 'ó')
            w = w.replace('ę', 'ę')
            w = w.replace('ż', 'ż')
            return dictionary.get(w, w)

        opis1 = df_opis['Opis'][12]

        raw_corpus = []
        n = 0

        for i in df_opis.iterrows():
            n += 1
            l = list(splitter.split(i[1][1]))
            raw_corpus.append(l)

        all_words = []
        for t in raw_corpus:
            all_words[0:0] = t

        words = {}
        for w in all_words:
            rec = words.get(w.lower(), {'upper': 0, 'lower': 0})
            if w.lower() == w or w.upper() == w:
                rec['lower'] = rec['lower'] + 1
            else:
                rec['upper'] = rec['upper'] + 1
            words[w.lower()] = rec

        raw_stop_words = [x for x in words.keys() if words[x]['upper'] >= words[x]['lower'] * 4]

        set_raw_stop_words = set(raw_stop_words)

        def preprocessing(opis, filter_raw=True, filter_dict=True):
            opis = str(opis)
            tokenized = splitter.split(opis)
            l = list(tokenized)
            l = [x.lower() for x in l]
            l = [x for x in l if len(x) > 2]
            l = [x for x in l if x.find('_') < 0]
            l = [x for x in l if isnumber.search(x) is None]
            if filter_raw: l = [x for x in l if x not in set_raw_stop_words]
            if filter_dict: l = [x for x in l if x in set_dict]
            l = [lematize(x) for x in l]
            l = [x for x in l if len(x) > 2]
            return l

        df_opis["opisTT"] = df_opis['Opis'].apply(
            lambda x: ' '.join(preprocessing(x, filter_raw=True, filter_dict=True)))
        df_opis["opisTF"] = df_opis['Opis'].apply(
            lambda x: ' '.join(preprocessing(x, filter_raw=True, filter_dict=False)))
        df_opis["opisFT"] = df_opis['Opis'].apply(
            lambda x: ' '.join(preprocessing(x, filter_raw=False, filter_dict=True)))
        df_opis["opisFF"] = df_opis['Opis'].apply(
            lambda x: ' '.join(preprocessing(x, filter_raw=False, filter_dict=False)))


        df_merged = df_consolidated.drop(
                                            ['Leisure_Node',
                                             'Leisure_Rel',
                                             'Leisure_NodeOfWay',
                                             'Tourism_Node',
                                             'Public_transport_Node',
                                             'Shop_NodeOfWay',
                                             'Shop_Node',
                                             'Amenity_Node',
                                             'Leisure_Way',
                                             'Leisure_Node_Name',
                                             'Leisure_Rel_Name',
                                             'Leisure_NodeOfWay_Name',
                                             'Tourism_Node_Name',
                                             'Public_transport_Node_Name',
                                             'Shop_NodeOfWay_Name',
                                             'Shop_Node_Name',
                                             'Amenity_Node_Name',
                                             'Leisure_Way_Name'],
                                        axis=1)
        df_merged = df_merged.drop(['Opis', 'Ident', 'Link'], axis=1)
        df_rok_zabudowy = df_merged['Rok_zabudowy'].apply(lambda x: int(x) if (x != 'NaN') else None)
        df_rok_zabudowy.mean(skipna=True)
        df_merged['Rok_zabudowy'] = df_merged['Rok_zabudowy'].apply(
            lambda x: int(x) if (x != 'NaN') else int(round(df_rok_zabudowy.mean(skipna=True))))
        for row in df_merged.iterrows():
            if 'ponad' in row[1]['Liczba_pokoi'] or 'wiecej' in row[1]['Liczba_pokoi']:
                df_merged.loc[row[0], 'Liczba_pokoi'] = re.sub("[^0-9]", "", row[1]['Liczba_pokoi'])

        df_features = df_consolidated.loc[:,
                                              ['Leisure_Node_Name',
                                               'Leisure_Rel_Name',
                                               'Leisure_NodeOfWay_Name',
                                               'Tourism_Node_Name',
                                               'Public_transport_Node_Name',
                                               'Shop_NodeOfWay_Name',
                                               'Shop_Node_Name',
                                               'Amenity_Node_Name',
                                               'Leisure_Way_Name']
                                        ]
        df_new_features = pd.DataFrame(
            [df_features[col].apply(lambda x: x[1:-1].split(',') if x != '' else '') for col in df_features.columns])
        heywaitaminute = df_new_features.T
        def temp_performer(cell):
            temp_dict = {}
            temp_list = []

            for data in cell:
                if data not in temp_dict.keys():
                    temp_dict[data] = 1
                elif data in temp_dict.keys():
                    temp_dict[data] += 1
            for key, value in temp_dict.items():
                temp_list.append(str(key) + '_' + str(value))
            return temp_dict  # ' '.join(temp_list)
        transferred_df = pd.DataFrame([heywaitaminute[col].apply(lambda x: temp_performer(x) if x != '' else '')
                                       for col in df_features.columns]).T
        empty_df = pd.DataFrame(df_consolidated["Ident"])
        for colname in transferred_df.columns:
            all_KEYS = []
            print(colname)
            for row in transferred_df[colname]:
                if row != '':
                    for key in row.keys():
                        if key not in all_KEYS:
                            all_KEYS.append(key)
            for key in all_KEYS:
                empty_df[key] = 0
            for key in all_KEYS:
                for index, row in enumerate(transferred_df[colname]):
                    if row != '':
                        if key in row.keys():
                            if key not in empty_df.columns:  # transferred_df[key][transferred_df.index[index]]
                                empty_df.loc[transferred_df.index[index], key] = row[key]
                            elif key in empty_df.columns:
                                empty_df.loc[transferred_df.index[index], key] += row[key]
        empty_df = empty_df.drop("Ident", axis=1)

        dum_df = pd.get_dummies(df_merged, columns=['Pietro', 'Max_liczba_pieter', 'Typ_zabudowy', 'Parking', 'Kuchnia', 'Wlasnosc', 'Stan', 'Material', 'Okna', 'Rynek', 'Dzielnica' ])
        merged_df_new = dum_df.drop(["Miasto", "ExtractionTime"], axis=1)

        MERGED_tables = pd.concat([merged_df_new, empty_df], axis=1, join='inner')
        def clean_dataset(df):  # .drop(['opisFF', 'opisTF', 'opisFT', 'opisTT'], axis=1)
            assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
            df.dropna(inplace=True)
            indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
            return df[indices_to_keep].astype(np.float64)

        MERGED_tables = clean_dataset(MERGED_tables)
        MERGED_tables = MERGED_tables.dropna()
        indexes = MERGED_tables.index
        df_opis = df_opis.iloc[df_opis.index.isin(indexes)].drop(["Ident"], axis=1)
        MERGED_tables_2 = pd.concat([MERGED_tables, df_opis], axis=1, join='inner')

        class ItemSelector(BaseEstimator, TransformerMixin):
            def __init__(self, key=''):
                self.key = key

            def fit(self, x, y=None):
                return self

            def transform(self, data_dict):
                return data_dict[self.key]

        class ItemUnSelector(BaseEstimator, TransformerMixin):
            def __init__(self, keys=[]):
                self.keys = keys

            def fit(self, x, y=None):
                return self

            def transform(self, data_dict):
                return data_dict.drop(self.keys, axis=1)

        pipeline = Pipeline([
            ('union',
             FeatureUnion(
                 transformer_list=[
                     ('table',
                      Pipeline([
                          ('selector1', ItemUnSelector(keys=['Opis', 'opisTT', 'opisTF', 'opisFT', 'opisFF'])),
                          ('scaler1', 'passthrough')
                      ])
                      ),
                     ('description',
                      Pipeline([
                          ('selector2', ItemSelector()),
                          ('tfidf', TfidfVectorizer()),
                          ('best', TruncatedSVD()),
                          ('scaler2', 'passthrough')
                      ])
                      )
                 ]
             )

             ),
            ('regressor',
             TransformedTargetRegressor()
             )
        ])

        parameters = parameters = {
            'union__transformer_weights': [{'table': 1.0, 'description': 1.0}],

            'union__description__best__n_components': (700,),
            'union__description__tfidf__min_df': (3,),
            'union__description__tfidf__binary': (True,),
            'union__description__selector2__key': ['opisTT'],

            'union__table__scaler1': [RobustScaler()],
            'union__description__scaler2': [RobustScaler(with_centering=False)],

            'regressor': [GradientBoostingRegressor()],
        }

        grid_search = GridSearchCV(pipeline, parameters, verbose=1, cv=4, n_jobs=-1)

        y = MERGED_tables_2['Price_per_metr']
        X = MERGED_tables_2.drop(['Price_per_metr', 'Price'], axis=1)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

        t0 = time()
        grid_search.fit(X_train, y_train)
        print("done in %0.3fs" % (time() - t0))

        print(f'Best score: {grid_search.best_score_}')

        print("Best parameters set:")
        print()
        best_parameters = grid_search.best_estimator_.get_params()
        for param_name in sorted(parameters.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]))

        print('Test: ', grid_search.score(X_test, y_test))
















