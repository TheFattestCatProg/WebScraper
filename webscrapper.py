from argparse import ArgumentParser
import os
from types import ModuleType
from aiohttp import ClientSession
import importlib.util
import yaml
import logging

from async_util import NameFabric, hand_worker
from env import Env

logging.basicConfig(format='%(levelname)s %(name)s -> %(message)s', level=logging.DEBUG)


def panic(*args):
    print(*args)
    exit(1)


def process_cfg_val(v):
    if isinstance(v, dict):
        return process_cfg_dict(v)
    return v


def process_cfg_key(k: str):
    return k.replace('-', '_')


def process_cfg_dict(d: dict) -> dict:
    return { process_cfg_key(k): process_cfg_val(d[k]) for k in d }


def load_config(path: str) -> dict:
    with open(path, 'r') as file:
        cfg = yaml.safe_load(file)

    return { k: process_cfg_val(cfg[k]) for k in cfg }


def load_module(path: str) -> ModuleType:
    name = os.path.splitext(os.path.split(path)[1])[0]
    
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
    

def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('yaml_file', type=str)

    args = arg_parser.parse_args()
    cfg = load_config(args.yaml_file)

    mode_module = load_module('./modes.py')

    async def hand(session: ClientSession):
        env = Env(
            session,
            NameFabric(),
            cfg,
            mode_module
        )

        await env.main_rule()

    hand_worker(hand)


if __name__ == '__main__':
    main()