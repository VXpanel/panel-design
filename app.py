#!/usr/bin/python
import uvicorn, os
from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.responses import Response

import os
import zipfile
import subprocess
import ports
import pathlib
import json
import docker

from time_db import global_init, Server, create_session

global_init('database.db')

# Create server
app = FastAPI()
templates = Jinja2Templates('templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

path = pathlib.Path(__file__).parent.resolve()

# Server home page
@app.get('/')
def home_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

@app.get('/{server}')
def panel_page(request: Request, server, password='password'):
    session = create_session()
    server = session.query(Server).filter(Server.name==server).first()
    server_data = ''

    if password == server.password:
        server_data = {
            "id": server.id,
            "name": server.name,
            "ports": json.loads(server.ports),
        }
    else:
        return 'Unvalid password'
    return templates.TemplateResponse('index.html', {'request': request, 'server': server_data})

@app.get('/{server}/logs')
def logs_page(request: Request, server):
    return templates.TemplateResponse('logs.html', {'request': request})

# create server
@app.get('/create_server/{user}/{server_name}/{pre_install}')
def create_server(request: Request, user, server_name, pre_install):
    client = docker.from_env()
    try:
        os.mkdir(f'./files/{user}')
        os.mkdir(f'./files/{user}/{server_name}')
    except:
        pass

    if pre_install == 'wp':
        wp = zipfile.ZipFile('./pre_install/wordpress.zip')
        wp.extractall(f'./files/{user}/{server_name}/')
        wp.close()
    elif pre_install == 'python':
        wp = zipfile.ZipFile('./pre_install/python.zip')
        wp.extractall(f'./files/{user}/{server_name}/')
        wp.close()

    portWeb = ports.getPort()
    portSSH = ports.getPort()

    try:
        server = client.containers.run(
            "rastasheep/ubuntu-sshd", 
            detach=False, 
            mem_limit='1024m', 
            cpu_count=0.1, 
            ports={'22/tcp': portSSH, '80/tcp': portWeb}, 
            volumes=f'{path}/files/{user}/{server_name}:/app'
        )
        session = create_session()
        log = Server(
            name=server_name,
            ports='[{"web": '+str(portWeb)+', "ssh": '+str(portSSH)+'}]',
            password='root',
        )
        session.add(log)
        session.commit()
        return {"IP": "...", "web_port": portWeb, "ssh_port": portSSH, "panel": f"/{server_name}"}
    except Exception as e:
        return e

# Start server
if __name__ == "__main__":
    # dev
    uvicorn.run('app:app',
        host="0.0.0.0", 
        port=8000,
        log_level="debug",
        http="h11",
        #reload=True,
        use_colors=True,
        workers=3
    )
    # prod
    #uvicorn.run('app:app',
    #    host="0.0.0.0", 
    #    port=80,
    #    http="h11"
    #)