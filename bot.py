import requests
from bs4 import BeautifulSoup

filmaffinity = "https://www.filmaffinity.com/es/film932361.html"

# Confirmar que somos humanos

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "*/*"
}


def obtener_html(url: str) -> str:
    res = requests.get(url, headers=HEADERS)
    return res.text

html = obtener_html(filmaffinity)

soup = BeautifulSoup(html, 'lxml')

title_tag = soup.find('h1', id='main-title')
if title_tag:
    movie_title = title_tag.find('span', itemprop='name').text.strip()
    print("El título de la película es:", movie_title)
else:
    print("Título de la película no encontrado.")

