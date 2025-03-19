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
            "PYTHONUNBUFFERED=1",
            "LOGGING_LEVEL=DEBUG"
        ],
        "networks": ["testing_net"]
    }

    for i in range(1, n+1):
        services[f"client{i}"] = {
            "container_name": f"client{i}",
            "image": "client:latest",
            "entrypoint": "/client",
            "environment": [
                "CLI_ID=" + str(i),
                "CLI_LOG_LEVEL=DEBUG"
            ],
            "networks": ["testing_net"],
            "depends_on": ["server"]          
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
        print("Usar como: python3 generador-compose.py <nombre del archivo de salida> <cantidad de clientes>")
        sys.exit(1)
    else:
        filename = sys.argv[1]
        n = int(sys.argv[2])
        generate_compose(filename, n)

if __name__ == "__main__":
    main()