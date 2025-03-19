#!/bin/bash

# Chequeo de parametros
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <nombre_archivo> <cantidad_clientes>"
    exit 1
fi

filename=$1
num_clients=$2

# Chequeo de que el archivo no exista
if [ -f $filename ]; then
    echo "El archivo $filename ya existe. Por favor, elija otro nombre."
    exit 1
fi

# Chequeo de que la cantidad de clientes sea un numero
if ! [[ $num_clients =~ ^[0-9]+$ ]]; then
    echo "La cantidad de clientes debe ser un número entero."
    exit 1
fi

echo "Generando archivo docker compose..."
echo "Nombre del archivo de salida: $filename"
echo "Cantidad de clientes: $num_clients"

/usr/bin/python3 generador-compose.py $filename $num_clients
echo "Archivo generado con éxito."