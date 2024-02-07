import jinja2
import os
from aqua.util import load_yaml

definitions = load_yaml('config.tmpl')

print(definitions)
definitions['nemo_levellist'] = list(range(1,76))

# jinja2 loading and replacing (to be checked)
templateLoader = jinja2.FileSystemLoader(searchpath='./')
templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)

#definitions = {'expver': 'pippo'}

if definitions['eccodes_version'] == '2.30.0' : 
    definitions['eccodes_path'] = '/projappl/project_465000454/jvonhar/aqua/eccodes/eccodes-2.30.0/definitions'

template = templateEnv.get_template('ifs-nemo-catalog.j2')
outputText = template.render(definitions)

# create the new post file
output = os.path.join(definitions['experiment'] + '.yaml')
with open(output, "w", encoding='utf8') as fh:
    fh.write(outputText)
