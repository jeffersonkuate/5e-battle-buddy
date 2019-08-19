import os
import json
import re
import random
import math
from collections.abc import MutableMapping
from display import Display

# Prompts
PROMPT_START = "Enter q to quit, i for info, and enter to start: "
PROMPT_YES_NO = "Enter Y or N: "
PROMPT_NUMERIC = "Enter a number: "
PROMPT_ENTER = "Press Enter to Continue: "

INVALID = "INPUT INVALID!"

# Regular Expressions
REGEX_LONG_PATH = '/'
REGEX_QUIT = 'q$|quit$'
REGEX_INFO = 'i$|info$'
REGEX_START = 'q$|i$|quit$|info$|$'
REGEX_BLANK = '$'
REGEX_ALL = '.*'

# Top-level Config Properties
GAME = 'game'
GAMES = 'games'
CONFIG = 'config'
CHARACTERS = 'characters'
SKILLS = 'skills'
ABILITIES = 'abilities'
RESOURCES = 'resources'
STRATEGY = 'strategy'

# Strategy Manager Properties
SIMULATIONS_PER_GENERATION = 'simulations_per_generation'
CLONED_STRATEGY_COUNT = 'cloned_strategy_count'
MUTATED_STRATEGY_COUNT = 'mutated_strategy_count'
MERGED_STRATEGY_COUNT = 'merged_strategy_count'
MAX_STRATEGY_COMPLEXITY = 'max_strategy_complexity'
FITNESS_IMPROVEMENT_THRESHOLD = 'fitness_improvement_threshold'
STRATEGY_GROUPING = 'strategy_grouping'

# Key 5ebb-JSON Properties
PROFILE = 'profile'
ARGUMENTS = 'arguments'
CONDITIONS = 'conditions'
EFFECTS = 'effects'
VALUE = 'value'
NAME = 'name'
BONUS = 'bonus'
CONTEXT = 'property'
PROTOTYPE = 'prototype'
PROTOTYPES = 'prototypes'
TRIGGER = 'trigger'

# Basic Functions
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

# Die
DIE_ROLL = 'roll'
DIE_COUNT = 'count'
DIE_SIDES = 'sides'

# Hooks
START_OF_TURN = 'start_turn'
END_OF_TURN = 'end_turn'
ROLL = 'roll'
MOVEMENT = 'movement'
THREATENED_ZONE_ENTRANCE = 'threatened_zone_entrance'
THREATENED_ZONE_EXIT = 'threatened_zone_exit'
DAMAGE_DONE = 'damage_done'
DAMAGE_TAKEN = 'damage_taken'

# Affinities
HOSTILE = 'hostile'
FRIENDLY = 'friendly'
SELF = 'self'

# D&D Skills
ABSTAIN = 'abstain'
MOVEMENT_SKILL = 'movement'
DODGE = 'dodge'
ATTACK = 'attack'
ACTION_ATTACK = 'action_attack'
OPPORTUNITY_ATTACK = 'opportunity_attack'
DISENGAGE = 'disengage'

# D&D Targeting
SELF_TARGET = 'self'
SINGLE_TARGET = 'single_target'
RANGED_TARGET = 'ranged_attack'

# D&D Effects
END_TURN = 'end_turn'
MOVEMENT_EFFECT = 'movement'
SET = 'set'
CREDIT = 'credit'
DEBIT = 'debit'
ADVANTAGE = 'advantage'
DISADVANTAGE = 'disadvantage'
REMOVE_FROM_PLAY = 'remove_from_play'

# D&D Properties
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

    def simulate(self):
        pass


class MatchContext(BasicContext):
    def __init__(self):
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
        self.simulations_per_generation = expression[SIMULATIONS_PER_GENERATION]
        self.cloned_strategy_count = expression[CLONED_STRATEGY_COUNT]
        self.mutated_strategy_count = expression[MUTATED_STRATEGY_COUNT]
        self.merged_strategy_count = expression[MERGED_STRATEGY_COUNT]
        self.max_strategy_complexity = expression[MAX_STRATEGY_COMPLEXITY]
        self.fitness_improvement_threshold = expression[FITNESS_IMPROVEMENT_THRESHOLD]

    def merge(self, strategy1, strategy2):
        pass

    def mutate(self, strategy):
        pass

    def optimize(self, strategy_name):
        cloneable_strategies = []
        mutateable_strategies = []
        mergeable_strategies = []

        last_fitness = 0
        best_strategy = None
        strategies = []
        while (best_strategy is None
               or (((last_fitness * self.fitness_improvement_threshold) + last_fitness) < best_strategy.fitness)):
            last_fitness = best_strategy.fitness

            for i in range(self.cloned_strategy_count):
                strategies.append(Strategy(self.game, strategy_name))
            random.shuffle(mergeable_strategies)
            while len(cloneable_strategies) > 0:
                strategies.append(cloneable_strategies.pop())
            while len(mutateable_strategies) > 0:
                strategies.append(self.mutate(mutateable_strategies.pop()))
            while len(mergeable_strategies) > 1:
                strategy1 = mergeable_strategies.pop()
                strategy2 = mergeable_strategies.pop()
                strategies.append(self.merge(strategy1, strategy2))

            for strategy in strategies:
                fitness = 0
                for i in range(self.simulations_per_generation):
                    self.strategies[strategy_name] = strategy
                    fitness += self.game.simulate()[strategy_name]
                strategy.fitness = fitness / self.simulations_per_generation

                cloneable_strategies.append(strategy)
                mutateable_strategies.append(strategy)
                mergeable_strategies.append(strategy)

                if strategy.fitness > best_strategy.fitness:
                    best_strategy = strategy

        self.strategies[strategy_name] = best_strategy

    def trim_cloneable(self, strategies):
        return self.trim(strategies, self.cloned_strategy_count)

    def trim_mutateable(self, strategies):
        return self.trim(strategies, self.mutated_strategy_count)

    def trim_mergeable(self, strategies):
        return self.trim(strategies, self.merged_strategy_count)

    def trim(self, strategies, threshold):
        pass


class Strategy:
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.fitness = 0,
        self.nodes = {}

    def optimize(self, alignment):
        pass


class Node:
    def act(self, action_list):
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
                manager.optimize(strategy.name)
                optimization_count += 1
                report_strategy(strategy, display)
        else:
            strategy = manager.strategies[user_input]
            if strategy is None:
                display_invalid(display)
            else:
                manager.optimize(strategy.name)
                optimization_count += 1
                report_strategy(strategy, display)


if __name__ == '__main__':
    main()
