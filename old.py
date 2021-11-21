from flask import Flask
import os
import zipfile
import subprocess
import ports
import pathlib

app = Flask(__name__)

path = pathlib.Path(__file__).parent.resolve()

@app.route('/create_server/<user>/<server_name>/<pre_install>')
def hello_world(user, server_name, pre_install):
    try:
        os.mkdir(f'./files/{user}')
        os.mkdir(f'./files/{user}/{server_name}')
    except:
        pass

    if pre_install == 'wp':
        wp = zipfile.ZipFile('./pre_install/wordpress.zip')
        wp.extractall(f'./files/{user}/{server_name}/')
        wp.close()

    portWeb = ports.getPort()
    portSSH = ports.getPort()

    try:
        server = subprocess.run(
            f'docker run --rm -m 1024m --cpus=1 -d -p "{portWeb}:80" -p "{portSSH}:22" -v {path}/files/{user}/{server_name}:/app rastasheep/ubuntu-sshd', 
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            shell=True, check=True
        ).stdout.decode('utf-8')
        return {"IP": "...", "web_port": portWeb,"ssh_port": portSSH, "panel": "/admin"}
    except Exception as e:
        return e

if __name__ == '__main__':
    app.run()