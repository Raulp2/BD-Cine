import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from bs4 import BeautifulSoup
import pyodbc
import warnings
from urllib3.exceptions import InsecureRequestWarning

#URLs de las paginas web
FILMAFFINITY = "https://www.filmaffinity.com/es/film139117.html"
ICCA = "https://sede.mcu.gob.es/CatalogoICAA/Peliculas/Detalle?Pelicula=218023"

# conexion a base de datos
DB_PATH = r'C:\WorkSpace\ImpDataBDCine\BD.mdb'
CONN_STR = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=' + DB_PATH + ';')
# Header para parecer un navegador web
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "*/*"
}

# OBTENER DATOS HTML
# Eliminar los certificados para la pagina web del ministerio.
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,maxsize=maxsize,block=block,ssl_version=ssl.PROTOCOL_TLS,cert_reqs=ssl.CERT_NONE)

def configurar_sesion_ssl():
    session = requests.Session()
    session.mount('https://', SSLAdapter())
    warnings.simplefilter('ignore', InsecureRequestWarning)
    return session
session = configurar_sesion_ssl()

# Obtener HTML de filmaffinity
def obtener_htmlFa(url: str) -> str:
    res = requests.get(url, headers=HEADERS)
    res.encoding = 'utf-8'
    return res.text
htmlFa = obtener_htmlFa(FILMAFFINITY)

# Obtener HTML Icca
def obtener_htmlIcca(url: str) -> str:
    res = session.get(url, headers=HEADERS, verify=False)
    res.encoding = 'utf-8'
    return res.text
htmlIcca = obtener_htmlIcca(ICCA)

#Formatear los datos de recaudación y espectadores para que no haya errores en la base de datos
def formatear_numero(cantidad):
    # Reemplazar los puntos por un marcador temporal
    cantidad_temporal = cantidad.replace('.', 'TEMP')
    # Reemplazar las comas por puntos
    cantidad_temporal = cantidad_temporal.replace(',', '.')
    # Reemplazar el marcador temporal por comas
    cantidad_final = cantidad_temporal.replace('TEMP', ',')
    return cantidad_final

#Parsear Filmaffinity

def parsear_filmaffinity(htmlFa):
    soupFa = BeautifulSoup(htmlFa, 'lxml')
    #Titulo
    title_tag = soupFa.find(
        'h1', id='main-title')
    titulo_pelicula = title_tag.find(
        'span', itemprop='name').text.strip(
    ) if title_tag else "Título no encontrado"
    #Director y actores
    director_container = soupFa.find(
        'dd', class_='directors')
    nombre_directores = "D:" + ", ".join([link.text.strip() for link in director_container.find_all(
        'a')]) if director_container else "Director no encontrado" 
    # Actores
    actores_container = soupFa.find(
        'dd', class_='card-cast-debug')
    if actores_container:
        actores_links = actores_container.find_all(
            'li', itemprop="actor")[:3]  # Tomar solo los primeros 3 actores
        nombres_actores_sin_formato = [actor.find(
            'div', class_='name').text.strip()
                    for actor in actores_links]
        nombres_actores = " I:" + ", ".join(nombres_actores_sin_formato)
    else:
        nombres_actores = " I: Animación"
        print("Error al obtener actores o pelicula de animación")
    directores_actores = (nombre_directores) + (nombres_actores)
    # País
    pais_container = soupFa.find(
        'dt', string='País')
    if pais_container:
        pais = pais_container.find_next_sibling(
        'dd').text
        if "Estados Unidos" in pais:
            pais = "EEUU"
        if "Reino Unido" in pais:
            pais = "UK"    
    else:
        pais = ""
        print("Error al encontrar el país")
    # Genero
    genero_container = soupFa.find(
        'dd', class_='card-genres')
    if genero_container:
        primer_genero = genero_container.find('a')
        genero = primer_genero.text.strip()
    else:
        genero = ""
        print("Error en el genero o pendiente")
    # Nota
    nota_container = soupFa.find(
        'div', id='rat-avg-container')
    if nota_container:
        nota = nota_container.find(
            'div', id ='movie-rat-avg').text.strip()
    else:
        nota = "0"
        print("Error en la nota o sin calificación")
    
    return titulo_pelicula, directores_actores, pais, genero, nota

#Parsear Icaa

def parsear_Icaa(htmlIcca):
    soupIcca = BeautifulSoup(htmlIcca, 'lxml')
    #Titulo
    titulo_container = soupIcca.find(
        'h2', class_='custom-detail-title')
    if titulo_container:
        titulo_icaa=titulo_container.text.strip()
    else:
        titulo_icaa = "Pendiente"
        print("Error titulo icca")
    # Fecha estreno
    fecha_estreno_container = soupIcca.find(
        'label', class_='mcu-text-details-text-b', string="Release date:")
    if fecha_estreno_container:
        fecha_estreno = fecha_estreno_container.find_next(
            'label', class_='custom-simple-label').text
    else:
        fecha_estreno = "01/01/1001"
        print("pendiente de fecha de estreno")
    # Duración
    duracion_container = soupIcca.find(
        'label', class_='mcu-text-details-text-b', string="Runtime:")
    if duracion_container:
        duracion_total = duracion_container.find_next(
            'label', class_='custom-simple-label').text
        duracion = ''.join(filter(str.isdigit, duracion_total))
        if len(duracion) == 0:
            duracion = "0"
    else:
        duracion = "1"
        print("Error en la duración o pendiente")
    # Calificación
    calificacion_container = soupIcca.find(
        'label', class_='mcu-text-details-text-b', string="Film Rating")
    if calificacion_container:
        texto_calificacion = calificacion_container.find_next(
            'label', class_='custom-simple-label').text
        if "7" in texto_calificacion:
            calificacion = "7"
        if "12" in texto_calificacion:
            calificacion = "12"
        if "16" in texto_calificacion:
            calificacion = "16"
        if "18" in texto_calificacion:
            calificacion = "18"
        if "General Audiences and Especially recommended for Children" in texto_calificacion:
            calificacion = "TOL INFANTIL"
        if "General Audiences" in texto_calificacion:
            calificacion = "TOL"
    else:
        calificacion = "PENDIENTE"
        print("Error en la calificacion o pendiente")
    # Recaudación
    recaudacion_container = soupIcca.find(
        'label', class_='mcu-text-details-text-b', string="Box Office / Gross Spain: ")
    if recaudacion_container:
        recaudacion = recaudacion_container.find_next(
            'label', class_='custom-simple-label').text
        recaudacion=formatear_numero(recaudacion)
    else:
        recaudacion = "0 €"
        print("Error en la recauacion o pendiente de estreno")
    # Espectadores
    espectadores_container = soupIcca.find(
        'label', class_='mcu-text-details-text-b', string="Admissions:")
    if espectadores_container:
        espectadores = espectadores_container.find_next(
            'label', class_='custom-simple-label').text
        espectadores = formatear_numero(espectadores)
    else:
        espectadores = 0
        print("Error en los espectadores o pendiente de estreno")
    # ExpedienteICCA
    expIcaa_container = soupIcca.find(
        'label', class_='mcu-text-details-text-b', string="ICAA File:")
    if expIcaa_container:
        expIcaa = expIcaa_container.find_next(
            'label', class_='custom-simple-label').text
    else:
        expIcaa = "ERROR ICCA"
        print("ERROR EN CODIGO ICAA")
    

    return titulo_icaa, fecha_estreno, duracion, calificacion, recaudacion, espectadores, expIcaa



titulo_pelicula, directores_actores, pais, genero, nota = parsear_filmaffinity(htmlFa)
titulo_icaa, fecha_estreno, duracion, calificacion, recaudacion, espectadores, expIcaa = parsear_Icaa(htmlIcca)

print("Titulo FA: " + titulo_pelicula)
print("Titulo Icaa: "+ titulo_icaa)
print("Codigo Icaa: " + expIcaa)
# INSERCION EN LA BASE DE DATOS

conn = pyodbc.connect(CONN_STR)
cursor = conn.cursor()
try:
    sql_insert = "INSERT INTO [LISTA DE TITULOS  FESCINAL] (TITULO, DIRECTOR, PAIS, DURACION, CALIFICACION, Genero, ESTRENO, NOTA, RECAUDACION, ESPECTADORES, ExpICAA) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(sql_insert, (titulo_pelicula.upper(), directores_actores, pais.upper(), duracion, calificacion, genero.upper(), fecha_estreno, nota, recaudacion, espectadores, expIcaa))
    conn.commit()
    print("Inserción exitosa.")
except pyodbc.Error as e:
    print("Error al insertar en la base de datos:", e)


# Cerrar conexión
cursor.close()
conn.close()
