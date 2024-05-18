#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA cli tool to submit parallel aqua-web slurm jobs
'''

import subprocess
import argparse
import re
import sys
from jinja2 import Template
from ruamel.yaml import YAML
from tempfile import NamedTemporaryFile
from aqua.util import load_yaml, get_arg

def is_job_running(job_name, username):
    """verify that a job name is not already submitted in the slurm queue"""
    # Run the squeue command to get the list of jobs
    output = subprocess.run(['squeue', '-u', username, '--format', '%j'], 
                            capture_output=True, check=True)
    output = output.stdout.decode('utf-8').splitlines()[1:]
    
    # Parse the output to check if the job name is in the list
    return job_name in output

def submit_sbatch(model, exp, source='',
                  dependency=None,
                  config='./config.aqua-web.yaml',
                  template='./aqua-web.job.j2',
                  dryrun=False,
                  parallel=True,
                  ):
    """
    Submit a sbatch script for the LRA CLI with basic options

    args:
        model: model to be processed
        exp: exp to be processed
        source: source to be processed
        slurm_dict: dictionary with slurm optiosn
        yaml_file: config file for submission
        dependency: jobid on which dependency of slurm is built

    Return
        jobid
    """

    yaml = YAML(typ='rt')
    with open(config, 'r', encoding='utf-8') as file:
        definitions = yaml.load(file)

    if model:
        definitions['model'] = model
    else:
        model = definitions['model']
    if exp:
        definitions['exp'] = exp
    else:
        exp = definitions['exp']
    if source:
        definitions['source'] = source
    else:
        source = definitions['source']
    if parallel:
        definitions['parallel'] = '-p'
    else:
        definitions['parallel'] = ''

    username = definitions['username']

    # create identifier for each model-exp-source-var tuple
    job_name = "_".join([model, exp, source])
    full_job_name = 'aqua-web_' + job_name

    definitions['job_name'] = full_job_name
    definitions['output'] = 'aqua-web-' + job_name + '_%j.out'
    definitions['error'] = 'aqua-web-' + job_name + '_%j.err'

    print("read these defs:")
    print(definitions)

    with open(template, 'r', encoding='utf-8') as file:
        template = Template(file.read())
        rendered_job = template.render(definitions)

    with NamedTemporaryFile('w', delete=False) as temp:
        temp.write(rendered_job)
        job_temp_path = temp.name

    if dryrun:
        print("SLURM job:")
        print(rendered_job)
    
    sbatch_cmd = [ 'sbatch' ]

    if dependency is not None:
        sbatch_cmd.append('--dependency=afterany:'+ str(dependency))

    sbatch_cmd.append(job_temp_path)

    if not dryrun and is_job_running(full_job_name, username):
        print(f'The job is {job_name} is already running, will not resubmit')
        return 0

    if not dryrun:
        print(' '.join(['Submitting', model, exp, source]))
        result = subprocess.run(sbatch_cmd, capture_output = True, check=True).stdout.decode('utf-8')
        jobid = re.findall(r'\b\d+\b', result)[-1]
        return jobid
    else:
        print("SBATCH cmd:")
        print(sbatch_cmd)
        return 0


def parse_arguments(arguments):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='AQUA aqua-web CLI tool to submit parallel diagnostic jobs')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-m', '--model', type=str,
                        help='model to be processed')
    parser.add_argument('-e', '--exp', type=str,
                        help='experiment to be processed')
    parser.add_argument('-s', '--source', type=str,
                        help='source to be processed')
    parser.add_argument('-l', '--list', type=str,
                        help='list of experiments in format: model, exp, source')
    parser.add_argument('-p', '--parallel', action="store_true",
                        help='run in parallel mode')
    parser.add_argument('-x', '--max', type=int,
                        help='max number of jobs to submit without dependency')
    parser.add_argument('-t', '--template', type=str,
                        help='template jinja file for slurm job')
    parser.add_argument('-d', '--dry', action="store_true",
                        help='perform a dry run (no job submission)')

    return parser.parse_args(arguments)


if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])

    model = get_arg(args, 'model', None)
    exp = get_arg(args, 'exp', None)
    source = get_arg(args, 'source', None)
    config = get_arg(args, 'config', './config.aqua-web.yaml')
    parallel = get_arg(args, 'parallel', True)
    list = get_arg(args, 'list', None)
    dependency = get_arg(args, 'max', None)
    template = get_arg(args, 'template', './aqua-web.job.j2')
    dryrun = get_arg(args, 'dry', True)

    count = 0
    parent_job = None
    jobid = None

    if list:
        
        with open(list, 'r') as file:
            for line in file:
                
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
    
                model, exp, *source = re.split(r',|\s+|\t+', line.strip())  # split by comma, space, tab

                if len(source) == 0:
                    source = None

                if dependency and (count % dependency == 0) and count != 0:
                            print('Updating parent job to' + jobid)
                            parent_job = str(jobid)

                count = count + 1
                
                jobid = submit_sbatch(model=model, exp=exp, source=source, parallel=parallel,
                                    config=config, dependency=dependency,
                                    template=template, dryrun=dryrun)            
    else:
        jobid = submit_sbatch(model=model, exp=exp, source=source, parallel=parallel,
                              config=config, dependency=dependency,
                              template=template, dryrun=dryrun)
