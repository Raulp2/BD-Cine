import requests
from bs4 import BeautifulSoup
import pyodbc

# CONECTARSE A LA BASE DE DATOS
# Ruta al archivo de la base de datos Access
db_path = r'C:\WorkSpace\ImpDataBDCine\BD.mdb'
# Conexión
conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
            r'DBQ=' + db_path + ';')
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

#OBTENER DATOS HTML
filmaffinity = "https://www.filmaffinity.com/es/film932361.html"

# Header para parecer un navegador web
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "*/*"
}

def obtener_html(url: str) -> str:
    res = requests.get(url, headers=HEADERS)
    res.encoding='utf-8'
    return res.text

html = obtener_html(filmaffinity)

soup = BeautifulSoup(html, 'lxml')

# MANEJO DE DATOS 

# Titulo de la pelicula.
title_tag = soup.find('h1', id='main-title')
titulo_pelicula = title_tag.find('span', itemprop='name').text.strip() if title_tag else "Título no encontrado"

# Director y actores de la pelicula.
director_container = soup.find('dd', class_='directors')
nombre_directores = "D: " + ", ".join([link.text.strip() for link in director_container.find_all('a')]) if director_container else "Director no encontrado"

# INSERCION EN LA BASE DE DATOS

try:
    sql_insert = "INSERT INTO [LISTA DE TITULOS  FESCINAL] (TITULO, DIRECTOR) VALUES (?, ?)"
    cursor.execute(sql_insert, (titulo_pelicula, nombre_directores))
    conn.commit()
    print("Inserción exitosa.")
except pyodbc.Error as e:
    print("Error al insertar en la base de datos:", e)
# Confirmar cambios
conn.commit()
# Cerrar conexión
cursor.close()
conn.close()