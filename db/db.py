import sqlite3

def get_conexion():
    # Conectar a la base de datos (se crea si no existe)
    conexion = sqlite3.connect('db/db.db')
    return conexion


