import os
import json
import re
from display import Display


REGEX_LONG_PATH = '/'

class Game:
    def __init__(self):
        self.alignments = []


class Strategy:
    def __init__(self, game):
        self.game = game
        self.nodes = {}

    def optimize(self, alignment):
        pass


class Alignment:
    def __init__(self):
        pass


def unload_config(game, strategy, config):
    pass


def evaluate(expression, context):
    pass


def report_strategy(strategy, display):
    pass


def load_config():
    config = load('config.json')
    for file in config['configs']:
        config.update(load(file))
    return config


def load(path):
    if not match(REGEX_LONG_PATH, path):
        path = os.getcwd() + '/config/' + path
    return json.load(open(path))

def search(reg, string):
    return not (re.search(reg.lower(), string.lower()) is None)


def match(reg, string):
    return not (re.match(reg.lower(), string.lower()) is None)


def main():
    display = Display()
    config = load_config()
    display.print(json.dumps(config))
    game = Game()
    strategy = Strategy(game)
    unload_config(game, strategy, config)

    for i in range(config["strategy"]["optimization_cycles"]):
        for alignment in game.alignments:
            strategy.optimize(alignment)
            report_strategy(strategy, display)


if __name__ == '__main__':
    main()
