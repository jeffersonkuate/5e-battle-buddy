import os
import json
import re
import random
from collections.abc import MutableMapping
from display import Display


PROMPT_START = "Enter q to quit, i for info, and enter to start: "
PROMPT_YES_NO = "Enter Y or N: "
PROMPT_NUMERIC = "Enter a number: "
PROMPT_ENTER = "Press Enter to Continue: "

INVALID = "INPUT INVALID!"

REGEX_LONG_PATH = '/'
REGEX_QUIT = 'q$|quit$'
REGEX_INFO = 'i$|info$'
REGEX_START = 'q$|i$|quit$|info$|$'
REGEX_BLANK = '$'
REGEX_ALL = '.*'

GAME = 'game'
GAMES = 'games'
CONFIG = 'config'
CHARACTERS = 'characters'
SKILLS = 'skills'
ABILITIES = 'abilities'
RESOURCES = 'resources'
STRATEGY = 'strategy'
OPTIMIZATION_CYCLES = 'optimization_cycles'

ARGUMENTS = 'arguments'
CONDITION = 'condition'
EFFECTS = 'effects'
VALUE = 'value'
NAME = 'name'
BONUS = 'bonus'
CONTEXT = 'property'
PROTOTYPE = 'prototype'
PROTOTYPES = 'prototypes'

ADDITION = 'addition'
SUBTRACTION = 'subtraction'
MULTIPLICATION = 'multiplication'
DIVISION = 'division'
GREATER = 'greater'
LESS = 'less'
GREATER_OR_EQUAL = 'greater_or_equal'
LESS_OR_EQUAL = 'less_or_equal'
MAXIMUM = 'max'
MINIMUM = 'min'
MAP = 'map'
CONTAINS = 'contains'
ANY = 'any'
OR = 'or'
AND = 'and'
NOT = 'not'
GET = 'get'
EVAL = 'eval'

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


class BasicContext(MutableMapping):
    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, value):
        self.properties.__delitem__(value)

    def __getitem__(self, key):
        self.get(key)

    def __len__(self):
        self.properties.__len__()

    def __iter__(self):
        self.properties.__iter__()

    def __init___(self, properties, base=None):
        self.base = base
        self.properties = properties
        self.die = Die()
        self.function_map = {
            CONTEXT: self.context,
            ADDITION: self.add,
            SUBTRACTION: self.subtract,
            MULTIPLICATION: self.multiply,
            DIVISION: self.divide,
            GREATER: self.greater,
            LESS: self.less,
            GREATER_OR_EQUAL: self.greater_or_equal,
            LESS_OR_EQUAL: self.less_or_equal,
            MAXIMUM: self.maximum,
            MINIMUM: self.minimum,
            MAP: self.func_map,
            CONTAINS: self.contains,
            ANY: self.func_any,
            OR: self.func_or,
            AND: self.func_and,
            NOT: self.func_not,
            GET: self.func_get,
            EVAL: self.eval,
            DIE_ROLL: self.roll
        }

    def context(self, expression):
        return self.get(self.eval(expression[VALUE]))

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

    def greater(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            if self.eval(argument) <= value:
                return False
        return True

    def less(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            if self.eval(argument) >= value:
                return False
        return True

    def greater_or_equal(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            if self.eval(argument) < value:
                return False
        return True

    def less_or_equal(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            if self.eval(argument) > value:
                return False
        return True

    def maximum(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            argument_eval = self.eval(argument)
            if argument_eval > value:
                value = argument
        return value

    def minimum(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            argument_eval = self.eval(argument)
            if argument_eval < value:
                value = argument
        return value

    def func_map(self, expression):
        arguments = (expression[ARGUMENTS])
        collection = self.eval(arguments[0])
        func = arguments[1]

        value = []
        for item in collection:
            value.append(item.eval(func))

        return value

    def contains(self, expression):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0])
        for argument in arguments[1:]:
            if self.eval(argument) not in value:
                return False
        return True

    def func_any(self, expression):
        arguments = expression[ARGUMENTS]
        for argument in arguments:
            if self.eval(argument):
                return True
        return False

    def func_and(self, expression):
        arguments = expression[ARGUMENTS]
        for argument in arguments:
            argument_eval = self.eval(argument)
            if not argument_eval:
                return False
        return True

    def func_or(self, expression):
        arguments = expression[ARGUMENTS]
        for argument in arguments:
            argument_eval = self.eval(argument)
            if argument_eval:
                return True
        return False

    def func_not(self, expression):
        return not self.eval(expression[ARGUMENTS])

    def func_get(self, expression):
        arguments = expression[ARGUMENTS]
        return self.eval(arguments[0]).get(self.eval(arguments[1]))

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

    def re_context(self, base):
        return self.__new__(self.properties, base)

    def get(self, key):
        if hasattr(self, key):
            value = getattr(self, key)
        else:
            value = self.properties[key]

        if not (value or self.base):
            value = self.base.get(key)

        if is_context(value):
            value = self.re_context(value)
        elif is_expression(value):
            value = deep_copy(value).update(self.properties)

        return value

    def set(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.properties[key] = value

        if self.base:
            self.base.set(key, value)


class Game(BasicContext):
    def __init__(self, name='', base=None):
        self.strategy_factory = None
        self.alignments = []
        self.characters = []
        self.abilities = {}
        self.resources = {}
        self.name = name
        self.board = None
        super.__init__(self, {}, base)

    def re_context(self, base):
        return self.__new__(self.properties, self.name, base)

    def optimize(self, strategy):
        pass


class Alignment(BasicContext):
    def __init__(self, name='', base=None):
        self.name = name
        super.__init__(self, {}, base)
        self.function_map[INITIATIVE] = self.get_initiative

    def get_initiative(self, expression):
        initiative = self.get(INITIATIVE)
        if initiative is None:
            initiative = self.roll(get_d20()) + self.eval(expression[BONUS])
            self.set(INITIATIVE, initiative)

    def re_context(self, base):
        return self.__new__(self.properties, self.name, base)


class Character(BasicContext):
    def __init__(self, name='', base=None):
        self.name = name
        super.__init__(self, {}, base)
        self.function_map[INITIATIVE] = self.get_initiative

    def get_initiative(self, expression):
        initiative = self.get(INITIATIVE)
        if initiative is None:
            initiative = self.roll(get_d20()) + self.eval(expression[BONUS])
            self.set(INITIATIVE, initiative)

    def re_context(self, base):
        return self.__new__(self.properties, self.name, base)


class Board(BasicContext):
    def __init__(self, width, height, base=None):
        self.width = width
        self.height = height
        super.__init__(self, {}, base)

    def re_context(self, base):
        return self.__new__(self.properties, self.width, self.height, base)


class StrategyManager:
    def __init__(self, game, expression):
        self.game = game
        self.strategies = {}

    def optimize(self, strategy):
        pass


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


def unload_config(config):
    game = Game()

    characters = get_concretes(config[CHARACTERS])
    for character in characters:
        create_character(game, characters[character])

    skills = get_concretes(config[SKILLS])
    for skill in skills:
        create_skill(game, skills[skill])

    abilities = get_concretes(config[ABILITIES])
    for ability in abilities:
        create_ability(game, abilities[ability])

    resources = get_concretes(config[RESOURCES])
    for resource in resources:
        create_resource(game, resources[resource])

    games = get_concretes(config[GAMES])
    create_game(game, games[config[GAME]])

    return create_strategy_manager(game, config[STRATEGY])


def load_config():
    config = load('config.json')
    for file in config['configs']:
        config.update(load(file))
    return config


def load(path):
    if not match(REGEX_LONG_PATH, path):
        path = os.getcwd() + '/config/' + path
    return json.load(open(path))


def create_game(game, expression):
    pass


# TODO
def create_strategy_manager(game, expression):
    manager = StrategyManager()
    return manager


def create_character(game, expression):
    pass


def create_skill(game, expression):
    pass


def create_ability(game, expression):
    pass


def create_resource(game, expression):
    pass


def get_d20():
    return {DIE_COUNT: 1, DIE_SIDES: 20}


def report_strategies(manager, display):
    for strategy_name in manager.strategies:
        report_strategy(manager.strategies[strategy_name], display)


def report_strategy(strategy, display):
    pass


def checked_input(display, string='', prompt='', reg=REGEX_ALL):
    user_input = display.input(string, prompt)
    while not match(reg, user_input):
        display_invalid(display)
        user_input = display.input(string, prompt)
    return user_input


def display_invalid(display):
    display.input(INVALID, PROMPT_ENTER)


def search(reg, string):
    return not (re.search(reg.lower(), string.lower()) is None)


def match(reg, string):
    return not (re.match(reg.lower(), string.lower()) is None)


def get_concretes(expression):
    values = {}
    concretes = {}

    for key in expression:
        value = expression[key]
        prototypes = []
        if PROTOTYPES in value:
            prototypes = value[PROTOTYPES]

        for prototype in prototypes:
            deep_fill(value, values[prototype])

        values[key] = value

    for key in values:
        value = values[key]
        if not value[PROTOTYPE]:
            concretes[key] = value

    return concretes


def deep_fill(dictionary, update):
    if is_context(update):
        for key in update:
            value = dictionary[key]
            if value is None:
                dictionary[key] = deep_copy(update[key])
            else:
                deep_fill(dictionary[key], update[key])


def deep_copy(dictionary):
    value = {}
    if is_context(dictionary):
        for key in dictionary:
            value[key] = deep_copy(dictionary[key])
        return value
    else:
        return dictionary


def is_context(context):
    return issubclass(BasicContext, context)


def is_expression(expression):
    return issubclass(dict, expression)


def main():
    display = Display()
    config = load_config()
    display.print(json.dumps(config))
    manager = unload_config(config)
    optimization_count = 0

    while True:
        user_input = display.input("There have been " + str(optimization_count)
                                   + " optimization(s) made.\n"
                                   + "Enter q to quit, i for info, the name of a strategy to optimize it,"
                                   + "or nothing to optimize all strategies")

        if match(REGEX_QUIT, user_input):
            quit(1)
        elif match(REGEX_INFO, user_input):
            report_strategies(manager, display)
        elif match(REGEX_BLANK, user_input):
            for strategy_name in manager.strategies:
                strategy = manager.strategies[strategy_name]
                manager.optimize(strategy)
                optimization_count += 1
                report_strategy(strategy, display)
        else:
            strategy = manager.strategies[user_input]
            if strategy is None:
                display_invalid(display)
            else:
                manager.optimize(strategy)
                optimization_count += 1
                report_strategy(strategy, display)


if __name__ == '__main__':
    main()
