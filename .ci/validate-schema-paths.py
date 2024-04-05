#!/usr/bin/env python3

import glob
import pathlib
import yaml


class TestSchema():
    def __init__(self, automation_dir):
        cur_path = pathlib.Path(__file__).parent

        self.__autodir = automation_dir
        self.__src_dir = pathlib.Path(cur_path, '../', self.__autodir)
        self.__files = self.__src_dir.glob('*.yaml')

    def run(self):
        for f in self.__files:
            self.__run_file(f)

    def __run_file(self, f):
        rel = pathlib.Path(self.__autodir, f.name)
        print(f'Checking scenario file: {rel}')
        with open(f, 'r') as fh:
            content = yaml.safe_load(fh)
        for scenario in content['vas']:
            print(f'  Checking scenario: {scenario}')
            self.__validate(content['vas'][scenario])

    def __validate(self, scenario):
        for stage in scenario['stages']:
            _path = stage['path']
            print(f'    Checking path: {_path}', end='  ')
            source = pathlib.Path(_path)
            assert source.exists(), f'!! {source} does not exist'
            assert source.is_dir(), f'!! {source} is not a directory'
            print('[OK]')
            for val in stage['values']:
                f = val['src_file']
                _path = source / f
                print(f'    Checking source file: {_path}', end='  ')
                assert _path.is_file(), f'!! {_path} does not exist'
                print('[OK]')

if __name__ == '__main__':
    test = TestSchema('./automation/vars')
    test.run()
