# Script para generar un archivo docker-compose, con cantidad de clientes parametrizada.

import sys
import yaml

def generate_compose(filename, n):
    services = {}

    services["server"] = {
        "container_name": "server",
        "image": "server:latest",
        "entrypoint": "python3 /main.py",
        "environment": [
            "PYTHONUNBUFFERED=1"
        ],
        "networks": ["testing_net"],
        "volumes": [
            "./server/config.ini:/config.ini"
        ]
    }

    for i in range(1, n+1):
        services[f"client{i}"] = {
            "container_name": f"client{i}",
            "image": "client:latest",
            "entrypoint": "/client",
            "environment": [
                "CLI_ID=" + str(i)
            ],
            "networks": ["testing_net"],
            "depends_on": ["server"],
            "volumes": [
                "./client/config.yaml:/config.yaml",
                f"./.data/agency-{i}.csv:/dataset.csv"
            ]
        }

    compose = {
        "name": "tp0",
        "services": services,
        "networks": {
            "testing_net": {
                "ipam": {
                    "driver": "default",
                    "config": [
                        {
                            "subnet": "172.25.125.0/24"
                        }
                    ]
                }
            }
        }            
    }

    with open(filename, "w") as f:
        yaml.dump(compose, f)

def main():
    if len(sys.argv) != 3:
        print("Usar como: python3 generador-compose.py <nombre_archivo> <cantidad_clientes>")
        sys.exit(1)
    else:
        filename = sys.argv[1]
        n = int(sys.argv[2])
        generate_compose(filename, n)

if __name__ == "__main__":
    main()