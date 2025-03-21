#!/bin/bash

network_name="tp0_testing_net"
test_message="Testing echo server"

server_ip="server"
server_port=12345

# Creamos un contenedor temporal de alpine, le instalamos netcat y le hablamos al servidor
docker run --rm --network $network_name alpine sh -c "
    apk add --no-cache netcat-openbsd
    
    response=\$(echo $test_message | nc $server_ip $server_port)

    if
        [ \"\$response\" != \"$test_message\" ];
    then
        exit 1
    else
        exit 0
    fi
"

# Si la ejecución del contenedor fue exitosa, entonces el servidor está funcionando correctamente
if [ $? -eq 0 ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi