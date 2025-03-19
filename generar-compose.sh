#!/bin/bash
echo "Nombre del archivo docker compose de salida: $1"
echo "Cantidad de clientes a ejecutar: $2"

/usr/bin/python3 generador-compose.py $1 $2