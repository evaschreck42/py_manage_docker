# docker run --rm -d -p 8888:8888 --name notebook -v /Users/eva/workspace/notebooks/nb_test/:/home/jovyan/work jupyter/minimal-notebook start-notebook.sh
# docker logs --tail 3 notebook

import re
import socket

import docker

nb_cont_name = 'notebook'
image = 'jupyter/minimal-notebook'
command = 'start-notebook.sh'
dest_folder = '/home/jovyan/work'
local_folder = './notebooks/nb_test/'
port_inside = 8888
port_outside = 8888


def get_nb_url(cont):
    if cont:
        line = cont.logs().decode()
        search = re.search(r'http://127.*', line)
        if search:
            return search.group()
        else:
            return 'no URL found'


def get_containers(docker_client):
    docker_containers = docker_client.containers.list()

    for container in docker_containers:
        print(container.name)


def check_local_port(port_number):
    localhost = '127.0.0.1'
    net_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = net_socket.connect_ex((localhost, port_number))
    if result == 0:
        return True
    else:
        return False


if __name__ == '__main__':
    client = docker.from_env()

    if not check_local_port(port_outside):

        get_containers(client)

        try:
            nb_container = client.containers.get(nb_cont_name)
        except Exception:
            nb_container = client.containers.run(image=image,
                                                 command=command,
                                                 name=nb_cont_name,
                                                 detach=True,
                                                 remove=True,
                                                 ports={port_inside: port_outside},
                                                 volumes={local_folder: {'bind': dest_folder, 'mode': 'rw'}}
                                                 )

        print(get_nb_url(nb_container))

    else:
        print('port %d already in use' % (port_outside, ))
