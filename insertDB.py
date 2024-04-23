import os
import requests
import pyodbc
# Conexion a base de datos
print(pyodbc.drivers())
DB_PATH = f'{os.getcwd()}{os.sep}BD.mdb'
#CONN_STR = (r'DRIVER={' + pyodbc.drivers()[0] + '};DBQ=' + DB_PATH + ';')
CONN_STR = (r'DBQ=' + DB_PATH + ';')
# Endpoints y otros datos
URL_ENDPOINT='/api/pelicula/'
URL_LOGIN='/tpv/auth/'
final_url=None
login_url=None
url=None
user=None
password=None
token=None

def getToken(username, password):
      userData = {"username": username, "password": password}
      resp = requests.post(login_url, json=userData)
      token = resp.json().get('token', None)
    
def pushPelicula(recordPelicula):
      peliculaData={}
      resp = requests.post(final_url, json=peliculaData, headers={'Authorization': ''.join(['Token ', token])})
      print(resp.json())

# INSERCION EN LA BASE DE DATOS
def main():
        try:
            with pyodbc.connect(CONN_STR) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM [LISTA DE TITULOS  FESCINAL]")
                    for row in cursor.fetchall():
                        print(row)
                        pushPelicula(row)
        except pyodbc.Error as e:
            print("Error al acceder a la base de datos:", e)



if __name__ == "__main__":
    print("Url del servicio: ")
    url = input()
    print("Usuario Administrador del servicio: ")
    user = input()
    print("Password del Administrador: ")
    password = input()
    final_url = ''.join([url, URL_ENDPOINT])
    login_url = ''.join([url, URL_LOGIN])
    getToken(username=user, password=password)
    main()