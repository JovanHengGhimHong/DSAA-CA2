import os
from structures.DASK_ParseTree import DASK_ParseTree

parser = DASK_ParseTree()


def input_file_path(prompt) -> str:
    # handles bad file paths
    file_path = input(prompt)
    while not os.path.exists(file_path):
        print('That file path is invalid! Please try again!\n')
        file_path = input(prompt)

    return file_path

def dask_input(prompt, allow_quit=False):
    dask = input(prompt)

    # quit check
    if allow_quit and dask.strip().lower() == 'q':
        return 'q', 'q'

    # basic format check
    if dask.strip() == '' or '=' not in dask:
        print('That is not a valid DASK expression! Please try again\n')
        return dask_input(prompt, allow_quit)

    key, exp = dask.strip().split('=', 1)

    # expression validation
    if not parser.verify_expression(exp):
        print('That is not a valid DASK expression! Please try again\n')
        return dask_input(prompt, allow_quit)

    return key, exp

def yes_no_input(prompt) -> str:
    choice = input(prompt)
    while choice.lower() not in ['y', 'n']:
        print('That is not a valid choice. Please try again!\n')
        choice = input(prompt)

    return choice.lower() 