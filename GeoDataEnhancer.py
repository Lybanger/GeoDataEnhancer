from geopy.geocoders import Nominatim
from opencage.geocoder import OpenCageGeocode
from geopy import exc
import geopy
import pandas as pd


def format_coord(row):
    lat = row["Latitude"]
    lon = row["Longitude"]
    if pd.isna(lat) and pd.isna(lon):
        return ""
    return str(lat) + ', ' + str(lon)


def opencage(api_key, origen_destino):
    try:
        geocoder = OpenCageGeocode(api_key)
        df1 = pd.read_csv(origen_destino)
        df1["Coordenadas"] = df1.apply(format_coord, axis=1)  # Concatena las columnas longitud y latitud
        df1.to_csv(origen_destino, index=False, encoding='utf-8-sig')
        df = pd.read_csv(origen_destino)
        for index, row in df.iterrows():  # Itera entre las filas
            try:
                try:
                    result = geocoder.reverse_geocode(str(row['Latitude']), str(row['Longitude']))
                    try:
                        df.loc[index, 'Estado'] = result[0]['components']['state']
                    except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                        df.loc[index, 'Estado'] = result[0]['components']['city']
                except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                    df.loc[index, 'Estado'] = ""
            except AttributeError:  # Si no se encuentra coincidencia en el JSON pasa
                df.loc[index, 'Estado'] = ""
            except (AttributeError, KeyError, ValueError):
                df.loc[index, 'Estado'] = ""
        for index, row in df.iterrows():
            try:
                result = geocoder.reverse_geocode(str(row['Latitude']), str(row['Longitude']))
                try:
                    if 'Mexico City' in row['Estado']:
                        df.loc[index, 'Ciudad'] = result[0]['components']['neighbourhood']
                    else:
                        df.loc[index, 'Ciudad'] = result[0]['components']['city']
                except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                    try:
                        df.loc[index, 'Ciudad'] = result[0]['components']['village']
                    except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                        try:
                            df.loc[index, 'Ciudad'] = result[0]['components']['county']
                        except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                            df.loc[index, 'Ciudad'] = result[0]['components']['road']
            except (AttributeError, KeyError, ValueError, TypeError):
                df.loc[index, 'Ciudad'] = ""
        for index, row in df.iterrows():
            try:
                result = geocoder.reverse_geocode(str(row['Latitude']), str(row['Longitude']))
                df.loc[index, 'Pais'] = result[0]['components']['country']
            except (AttributeError, KeyError, ValueError, TypeError):
                df.loc[index, 'Pais'] = ""
        df.to_csv(origen_destino, index=False, encoding='utf-8-sig')
    except geopy.exc.GeocoderQuotaExceeded:
        print("Se ha excedido el límite, cambia de api_key")
    except geopy.exc.GeocoderUnavailable:
        print("El servicio de OpenCage no está disponible en este momento")
    except geopy.exc.GeocoderServiceError:
        print("El servicio de OpenCage no está disponible en este momento")


def nominatim(origen_destino):
    try:
        locator = Nominatim(user_agent="osdafpjj", timeout=20)  # objeto localizador con tiempo máximo de 10´s
        df1 = pd.read_csv(origen_destino)
        df1["Coordenadas"] = df1.apply(format_coord, axis=1)  # Concatena las columnas longitud y latitud
        df1.to_csv(origen_destino, index=False, encoding='utf-8-sig')
        df = pd.read_csv(origen_destino)
        for index, row in df.iterrows():  # Itera entre las filas
            try:
                try:
                    location = locator.reverse(row['Coordenadas'])
                    try:
                        df.loc[index, 'Estado'] = location.raw['address']['state']
                    except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                        df.loc[index, 'Estado'] = location.raw['address']['city']
                except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                    pass
            except AttributeError:  # Si no se encuentra coincidencia en el JSON pasa
                pass
            except (AttributeError, KeyError, ValueError):
                pass
        for index, row in df.iterrows():
            try:
                location = locator.reverse(row['Coordenadas'])
                try:
                    if 'Ciudad de México' in row['Estado']:
                        df.loc[index, 'Ciudad'] = location.raw['address']['neighbourhood']
                    else:
                        df.loc[index, 'Ciudad'] = location.raw['address']['city']
                except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                    try:
                        df.loc[index, 'Ciudad'] = location.raw['address']['town']
                    except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                        try:
                            df.loc[index, 'Ciudad'] = location.raw['address']['county']
                        except KeyError:  # Si no se encuentra coincidencia en el JSON pasa
                            pass
            except TypeError:  # Si no se encuentra coincidencia en el JSON pasa
                pass
            except (AttributeError, KeyError, ValueError):
                pass
        for index, row in df.iterrows():
            try:
                location = locator.reverse(row['Coordenadas'])
                df.loc[index, 'Pais'] = location.raw['address']['country']
            except AttributeError:  # Si no se encuentra coincidencia en el JSON pasa
                pass
            except (AttributeError, KeyError, ValueError):
                pass
        df.to_csv(origen_destino, index=False, encoding='utf-8-sig')
    except geopy.exc.GeocoderServiceError:
        print("Nominatim no funciona en este momento :(")
