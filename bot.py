import requests

filmaffinity = "https://www.filmaffinity.com/es/film932361.html"

# Confirmar que somos humanos

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
  "Accept": "*/*"
}

# Donde guardamos el contenido 

def guardar(contenido: str, nombre: str ="res.html") -> None:
    with open(nombre, "w") as f:
        f.write(contenido)

# Obtenci�n y guardado del html del enlace

def obtener_html(url: str) -> str:
    res = requests.get(url, headers=HEADERS)
    return res.text

html = obtener_html(filmaffinity)
guardar(html)