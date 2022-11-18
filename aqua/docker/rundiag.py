"""Runs an AQUA diagnostic using Docker"""

import yaml
import os
import docker
from jinja2 import Template, FileSystemLoader, Environment

def rundiag(cmd = None, machine_file=r'machine.yaml', diagnostic_file=r'diagnostic.yaml'):

    if machine_file is dict:
        # We can also pass directly a dict because the config file has been read before
        machine_cfg = machine_file
    else:
        # Import directory setting and volumes to mount from machine.yaml
        with open(machine_file) as file:
            machinecfg = yaml.load(file, Loader=yaml.FullLoader)

    # Transform volumes dict into "host=bind" strings 
    volume_list = []
    for key, value in machinecfg['volumes'].items():
        volume_list += [f'{value}:/{key}']

    if diagnostic_file is dict:
        diagcfg = diagnostic_file
    else:
        # Import parameters needed to render templates
        with open(diagnostic_file) as file:
            diagcfg = yaml.load(file, Loader=yaml.FullLoader)

    templateLoader = FileSystemLoader(searchpath="./templates")
    templateEnv = Environment(loader=templateLoader)

    # Now use jinja2 to render al top-level keys in recipe file
    # as templates into actual recipes, config files etc.

    for k in diagcfg:
        dest_file = os.path.join(machinecfg['volumes'][diagcfg[k]['target_volume']], diagcfg[k]['filename'])
        template_file = diagcfg[k]['template']
        template = templateEnv.get_template(template_file)
        template.stream(diagcfg[k]['parameters']).dump(dest_file)

    # Run actual diagnostic docker
    if not cmd:
        cmd_value = list(machinecfg['command'].values())[0]
    else:
        cmd_value = machinecfg['command'][cmd]
        
    client = docker.from_env()
    output = client.containers.run(image=machinecfg['image'],
                        command=cmd_value, 
                        volumes=volume_list, 
                        environment=machinecfg['environment'])
    return output