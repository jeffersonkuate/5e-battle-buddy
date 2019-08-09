import os
import json
import re
import random
from display import Display


REGEX_LONG_PATH = '/'

ARGUMENTS = 'arguments'
CONDITION = 'condition'
EFFECT = 'effect'
VALUE = 'value'
NAME = 'name'
BONUS = 'bonus'
CONTEXT = 'property'

ADDITION = 'addition'
SUBTRACTION = 'subtraction'
MULTIPLICATION = 'multiplication'
DIVISION = 'division'
# TODO
MAXIMUM = 'max'
MINIMUM = 'min'

STRENGTH = 'strength'
DEXTERITY = 'dexterity'
CONSTITUTION = 'constitution'
INTELLIGENCE = 'intelligence'
WISDOM = 'wisdom'
CHARISMA = 'charisma'

SEPARATOR = '_'
ABILITY_MODIFIER = 'am'
SAVE = 'save'

LEVEL = 'level'
MAX_HP = 'max_hp'
INITIATIVE = 'initiative'
INITIATIVE_BONUS = 'initiative_bonus'

RESOURCE_LEVEL = 'level'

DIE_ROLL = 'roll'
DIE_COUNT = 'count'
DIE_SIDES = 'sides'


class BasicContext:
    def __init___(self, properties):
        self.properties = properties
        self.die = Die()
        self.function_map = {
            CONTEXT: self.context,
            ADDITION: self.add,
            SUBTRACTION: self.subtract,
            MULTIPLICATION: self.multiply,
            DIVISION: self.divide,
            DIE_ROLL: self.roll
        }

    def context(self, expression):
        return self.get(expression[VALUE])

    def add(self, expression):
        arguments = expression[ARGUMENTS]
        count = 0
        for argument in arguments:
            count += self.eval(argument)
        return count

    def subtract(self, expression):
        arguments = expression[ARGUMENTS]
        count = self.eval(arguments[0])
        for argument in arguments[1:]:
            count -= self.eval(argument)
        return count

    def multiply(self, expression):
        arguments = expression[ARGUMENTS]
        count = self.eval(arguments[0])
        for argument in arguments[1:]:
            count *= self.eval(argument)
        return count

    def divide(self, expression):
        arguments = expression[ARGUMENTS]
        count = self.eval(arguments[0])
        for argument in arguments[1:]:
            count /= self.eval(argument)
        return count

    def roll(self, expression):
        return self.die.roll(expression[self.eval(DIE_COUNT)], expression[self.eval(DIE_SIDES)])

    def eval(self, expression):
        if type(expression) is dict:
            key = expression.keys[0]
            func = self.function_map[key]
            if func is not None:
                return func(expression[key])
            else:
                return self.get(key).eval(expression[key])
        else:
            return expression

    def get(self, key):
        if hasattr(self, key):
            value = getattr(self, key)
        else:
            value = self.properties.get(key)
        return value

    def set(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.properties[key] = value


class Game(BasicContext):
    def __init__(self, name=''):
        self.alignments = []
        self.characters = []
        self.strategies = {}
        self.name = name
        self.board = None
        super.__init__(self, {})


class Alignment(BasicContext):
    def __init__(self, name=''):
        self.name = name
        super.__init__(self, {})
        self.function_map[INITIATIVE] = self.get_initiative

    def get_initiative(self, expression):
        initiative = self.get(INITIATIVE)
        if initiative is None:
            initiative = self.roll(get_d20()) + self.eval(expression[BONUS])
            self.set(INITIATIVE, initiative)


class Character(BasicContext):
    def __init__(self, name=''):
        self.name = name
        super.__init__(self, {})
        self.function_map[INITIATIVE] = self.get_initiative

    def get_initiative(self, expression):
        initiative = self.get(INITIATIVE)
        if initiative is None:
            initiative = self.roll(get_d20()) + self.eval(expression[BONUS])
            self.set(INITIATIVE, initiative)


class Board(BasicContext):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        super.__init__(self, {})


class Strategy:
    def __init__(self, game):
        self.game = game
        self.nodes = {}

    def optimize(self, alignment):
        pass


class Die:
    def __init__(self, rand_func=random.randint):
        self.rand_func = rand_func

    def roll(self, die_count, sides):
        count = 0
        for i in range(die_count):
            count += self.rand_func(1, sides)
        return count


def unload_config(game, strategy, config):
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


def report_strategy(strategy, display):
    pass


def get_d20():
    return {DIE_COUNT: 1, DIE_SIDES: 20}


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
