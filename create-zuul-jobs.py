#!/usr/bin/env python3

import os
import yaml

_AUTO_PATH = 'automation/vars/'
_JOBS = []
_PROJECTS = ['noop']
_BASE_TRIGGER_FILES = [
        'lib',
        ]

def create_job(name, data):
    j_name = 'rhoso-architecture-validate-{}'.format(name)
    _paths = [p['path'] for p in data['stages']] + _BASE_TRIGGER_FILES
    for i in ['va', 'dt']:
        if os.path.exists(os.path.join(i, name)):
            _paths.append(os.path.join(i, name))
    _mock = os.path.join('automation', 'mocks', '{}.yaml'.format(name))
    if os.path.exists(_mock):
        _paths.append(_mock)
    _paths.sort()
    job = {
            'job': {
                'name': j_name,
                'parent': 'rhoso-architecture-base-job',
                'vars': {
                    'cifmw_architecture_scenario': name,
                    },
                'files': _paths,
                }
            }
    _JOBS.append(job)
    _PROJECTS.append(j_name)


for fname in [f for f in os.listdir(_AUTO_PATH) if f.endswith('.yaml')]:
    with open(os.path.join(_AUTO_PATH, fname), 'r') as y_file:
        scenarios = yaml.safe_load(y_file)
    for scenario, stages in scenarios['vas'].items():
        create_job(scenario, stages)

_sorted_jobs = sorted(_JOBS, key= lambda d: d['job']['name'])
with open('./zuul.d/validations.yaml', 'w+') as zuul_jobs:
    yaml.dump(_sorted_jobs, zuul_jobs)

_PROJECTS.sort()
with open('./zuul.d/projects.yaml', 'w+') as zuul_projects:
    struct = [{'project': {'github-check': {'jobs': _PROJECTS},
                           'github-gate': {'jobs': _PROJECTS}
                           }
               }
              ]
    yaml.dump(struct, zuul_projects)
