import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from bs4 import BeautifulSoup
import pyodbc

filmaffinity = "https://www.filmaffinity.com/es/film932361.html"
icca= "https://sede.mcu.gob.es/CatalogoICAA/Peliculas/Detalle?Pelicula=4324"
# CONECTARSE A LA BASE DE DATOS
# Ruta al archivo de la base de datos Access
db_path = r'C:\WorkSpace\ImpDataBDCine\BD.mdb'
# Conexión
conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + db_path + ';')
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# OBTENER DATOS HTML
# Eliminar los certificados para la pagina web del ministerio.
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                    maxsize=maxsize,
                                    block=block,
                                    ssl_version=ssl.PROTOCOL_TLS,
                                    cert_reqs=ssl.CERT_NONE)
session = requests.Session()
session.mount('https://', SSLAdapter())

#Header para parecer un navegador web
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "*/*"
}
#Obtener HTML de filmaffinity
def obtener_htmlFa(url: str) -> str:
    res = requests.get(url, headers=HEADERS)
    res.encoding='utf-8'
    return res.text
htmlFa = obtener_htmlFa(filmaffinity)
#Obtener HTML Icca
def obtener_htmlIcca(url: str) -> str:
    res = session.get(url, headers=HEADERS, verify=False)
    res.encoding = 'utf-8'
    return res.text
htmlIcca = obtener_htmlIcca(icca)

def guardar(contenido: str, nombre: str ="res.html") -> None:
    with open(nombre, "w", encoding ='utf-8') as f:
        f.write(contenido)
html = obtener_htmlIcca(icca)
guardar(html)
soupFa = BeautifulSoup(htmlFa, 'lxml')
soupIcca = BeautifulSoup(htmlIcca, 'lxml')

#MANEJO DE DATOS
#Titulo de la pelicula.
title_tag = soupFa.find('h1', id='main-title')
titulo_pelicula = title_tag.find('span', itemprop='name').text.strip() if title_tag else "Título no encontrado"
print (titulo_pelicula)

#Director y actores de la pelicula.
    #Director
director_container = soupFa.find('dd', class_='directors')
nombre_directores = "D:" + ", ".join([link.text.strip() for link in director_container.find_all('a')]) if director_container else "Director no encontrado"
print (nombre_directores)

    #Actores
actores_container = soupFa.find('dd', class_='card-cast-debug')
if actores_container:
    actores_links = actores_container.find_all('li', itemprop="actor")[:3]  # Tomar solo los primeros 3 actores
    nombres_actores = [actor.find('div', class_='name').text.strip() for actor in actores_links]
    nombres_actores_formato = " I:" +", ".join(nombres_actores)
    print (nombres_actores_formato)
else:
    nombres_actores_formato = "Actores no encontrados"
directores_actores = (nombre_directores) + (nombres_actores_formato)
print (directores_actores)

#Fecha estreno
fecha_estreno_container = soupIcca.find('label', class_='mcu-text-details-text-b', string="Release date:")
if fecha_estreno_container:
    fecha_estreno = fecha_estreno_container.find_next('label', class_='custom-simple-label').text
else:
    fecha_estreno = "Pendiente"
print(fecha_estreno)

#País/Año

#Duración
duracion_container = soupIcca.find('label', class_='mcu-text-details-text-b', string="Runtime:")
if duracion_container:
    duracion_total = duracion_container.find_next('label', class_='custom-simple-label').text
    duracion = ''.join(filter(str.isdigit, duracion_total))
else:
    duracion = 0
print(duracion)

#Calificación
calificacion_container = soupIcca.find('label', class_='mcu-text-details-text-b', string="Film Rating")
if calificacion_container:
    calificacion = calificacion_container.find_next('label', class_='custom-simple-label').text
    
else:
    calificacion = "Pendiente"
#Genero

#Nota

#Recaudación

#Espectadores

#ExpedienteICCA

# INSERCION EN LA BASE DE DATOS
# try:
#     sql_insert = "INSERT INTO [LISTA DE TITULOS  FESCINAL] (TITULO, DIRECTOR) VALUES (?, ?)"
#     cursor.execute(sql_insert, (titulo_pelicula, directores_actores))
#     conn.commit()
#     print("Inserción exitosa.")
# except pyodbc.Error as e:
#     print("Error al insertar en la base de datos:", e)

# Confirmar cambios
conn.commit()
# Cerrar conexión
cursor.close()
conn.close()