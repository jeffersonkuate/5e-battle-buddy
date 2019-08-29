import math
import os
import json
import re
import random
from collections.abc import MutableMapping, MutableSequence
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
MATCH = 'environment'
MATCHES = 'environments'
CONFIG = 'config'
CHARACTERS = 'characters'
SKILLS = 'skills'
ABILITIES = 'abilities'
RESOURCES = 'resources'
STRATEGY = 'strategy'

# Strategy Manager Properties
MAXIMUM_TURNS = 'maximum_turns'
SIMULATIONS_PER_GENERATION = 'simulations_per_generation'
NOVEL_STRATEGY_COUNT = 'novel_strategy_count'
CLONED_STRATEGY_COUNT = 'cloned_strategy_count'
MUTATED_STRATEGY_COUNT = 'mutated_strategy_count'
MERGED_STRATEGY_COUNT = 'merged_strategy_count'
MAX_STRATEGY_COMPLEXITY = 'max_strategy_complexity'
MUTATION_COEFFICIENT = 'mutation_coefficient'
FITNESS_IMPROVEMENT_THRESHOLD = 'fitness_improvement_threshold'
STRATEGY_GROUPING = 'strategy_grouping'

# Key 5ebb-JSON Properties
PROFILE = 'profile'
ARGUMENTS = 'arguments'
CONDITIONS = 'conditions'
EFFECTS = 'effects'
SUCCESS_EFFECTS = 'success_effects'
FAILURE_EFFECTS = 'failure_effects'
VALUE = 'value'
NAME = 'name'
BONUS = 'bonus'
CONTEXT = 'property'
PROTOTYPE = 'prototype'
PROTOTYPES = 'prototypes'
TRIGGER = 'trigger'
INITIAL = 'initial'
COMPULSORY = 'compulsory'
TARGETING = 'targeting'
HOOK = 'hook'

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
DEATH = 'death'
REMOVAL_FROM_PLAY = 'remove_from_play'

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
TILE_TARGET = 'terrain_target'

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

ALIGNMENT = 'alignment'
POSITION = 'position'
INITIATIVE = 'initiative'
BOARD_WIDTH = 'board_width'
BOARD_HEIGHT = 'board_height'

SEPARATOR = '_'
ABILITY_MODIFIER = 'am'
SAVE = 'save'

LEVEL = 'level'
MAX_HP = 'max_hp'
INITIATIVE_BONUS = 'initiative_bonus'

MAX_VALUE = 'max_value'
HIT_POINT = 'hit_point'
CURRENT_ROLL = 'current_roll'
DAMAGE = 'damage'
RESOURCE_LEVEL = 'level'


# Basics

def get_d20():
    return {DIE_COUNT: 1, DIE_SIDES: 20}


def trim(self, items, threshold, sort_value=lambda x: x):
    items = sorted(items, key=sort_value, reverse=True)
    if len(items) > threshold:
        items = items[:threshold]
    return items


def deep_fill(dictionary, update):
    if is_map(update):
        for key in update:
            value = dictionary.get(key)
            if value is None:
                dictionary[key] = deep_copy(update.get(key))
            else:
                deep_fill(dictionary[key], update.get(key))


def deep_copy(dictionary):
    value = {}
    if is_map(dictionary):
        for key in dictionary:
            value[key] = deep_copy(dictionary.get(key))
        return value
    else:
        return dictionary


def is_map(context):
    return issubclass(type(context), MutableMapping)


def is_evaluable(expression):
    return issubclass(type(expression), dict) or issubclass(type(expression), Evaluable)


def is_list(expression):
    return issubclass(type(expression), MutableSequence)


def is_context(context):
    return issubclass(type(context), BasicContext)


class Die:
    def __init__(self, rand_func=random.randint):
        self.rand_func = rand_func

    def roll(self, die_count, sides):
        count = 0
        for i in range(die_count):
            count += self.rand_func(1, sides)
            return count


# Models

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

    def __eq__(self, other):
        return self.get(NAME) == other.get(NAME)

    def __init___(self, properties=None, name='', base=None):
        self.base = base
        self.name = name
        self.properties = {} if properties is None else properties
        self.initiative = None
        self.die = Die()
        self.effect_map = {}
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
            if self.eval(argument):
                return True
        return False

    def func_not(self, expression):
        return not self.eval(expression[ARGUMENTS])

    def func_get(self, expression):
        arguments = expression[ARGUMENTS]
        return self.eval(arguments[0]).get(self.eval(arguments[1]))

    def roll(self, expression):
        return self.die.roll(expression[self.eval(DIE_COUNT)], expression[self.eval(DIE_SIDES)])

    def get_initiative(self, expression=None):
        initiative = self.initiative
        if initiative is None:
            initiative = self.roll(get_d20()) + self.eval(expression[BONUS])
            self.initiative = initiative
        return initiative

    def affect(self, expression):
        effect = self.effect_map[expression[PROFILE]]
        if effect is not None:
            effect(expression)

    def check_conditions(self, conditions=None):
        if conditions is None:
            conditions = self.get(CONDITIONS)
        return self.func_and({ARGUMENTS: conditions})

    def get_match(self):
        return self.get(MATCH)

    def set_match(self, match):
        self.set(MATCH, match)

    def eval(self, expression):
        if is_evaluable(expression):
            key = expression.keys[0]
            func = self.function_map[key]
            if func is not None:
                return func(expression[key])
            else:
                return self.get(key).eval(expression[key])
        else:
            return expression

    def re_context(self, base):
        return type(base)(properties=base.properties, base=self)

    def get(self, key):
        if hasattr(self, key):
            value = getattr(self, key)
        elif key == INITIATIVE:
            return self.get_initiative()
        else:
            value = self.properties[key]

        if (value is None) and (self.base is not None):
            value = self.base.get(key)

        if is_context(value):
            value = self.re_context(value)
        elif is_evaluable(value):
            value = Evaluable(value, base=self)

        return value

    def set(self, key, value):
        self.properties[key] = value

        if hasattr(self, key):
            setattr(self, key, value)


class Evaluable(BasicContext):
    def __init__(self, expression, name='', base=None):
        super().__init__(expression, name, base)


class BasicContextList(MutableSequence):
    def __init__(self, name='', base=None):
        self.name = name
        self.base = base

    def insert(self, index, value):
        return self.base.insert(index, value)

    def __getitem__(self, index):
        return self.base.__getitem__(index)

    def __setitem__(self, index, value):
        return self.base.__setitem__(index, value)

    def __delitem__(self, index):
        return self.base.__delitem__(index)

    def __len__(self):
        return self.base.__len__()


# Environment

class Environment(BasicContext):
    def __init__(self, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.alignments = []
        self.characters = {}
        self.abilities = {}
        self.skills = {}
        self.resources = {}
        self.match_data = None

    def add_character(self, character):
        self.characters[character.name] = character
        if character.alignement not in self.alignments:
            self.alignments.append(character.alignement)

    def add_skill(self, skill):
        self.skills[skill.name] = skill

    def add_ability(self, ability):
        self.abilities[ability.name] = ability

    def add_resource(self, resource):
        self.resources[resource.name] = resource


class Character(BasicContext):
    def __init__(self, properties, name='', base=None):
        super().__init__(properties, name, base)
        self.abilities = {}
        self.skills = {}
        self.function_map[INITIATIVE] = self.get_initiative


class Skill(BasicContext):
    def __init__(self, properties, name='', base=None):
        super().__init__(properties, name, base)
        self.targeting = None
        self.conditions = []
        self.trigger = None


class Ability(BasicContext):
    def __init__(self, properties, name='', base=None):
        super().__init__(properties, name, base)
        self.hook = None
        self.conditions = []
        self.trigger = None


class Resource(BasicContext):
    def __init__(self, properties, name='', base=None):
        super().__init__(properties, name, base)
        self.initial = 0
        self.properties[INITIAL] = 0

    def set_initial(self, expression):
        if expression is not None:
            self.set(INITIAL, self.eval(expression))


# Match

class MatchContext(BasicContext):
    def __init__(self, environment, match_data, strategy_manager):
        super().__init__(match_data, base=environment)
        self.environment = environment
        self.board = Board(match_data[BOARD_WIDTH], match_data[BOARD_HEIGHT])
        self.match_characters = []
        self.initiative_set = InitiativeSet()
        self.action_set_stack = []
        self.turn = 0
        self.strategy_manager = strategy_manager

        for character in match_data[CHARACTERS]:
            match_character = MatchCharacter(character, base=environment.characters[character[NAME]])
            self.add_character(match_character)

        self.set_match(self)

    def add_character(self, character):
        character.set_match(self)
        self.match_characters.append(character)
        self.initiative_set.add_character(character)

    def simulate(self):
        while self.strategy_manager.is_ongoing(self):
            actions = []
            if len(self.action_set_stack) > 0:
                actions = self.action_set_stack.pop()
            else:
                self.turn += 1
                character = self.initiative_set.get_next_character()
                if character is not None:
                    actions = character.get_actions()

            if len(actions) > 0:
                self.strategy_manager.get_strategy(actions[0].actor).choose_action(actions).act()

    def no_conflict(self):
        alignments = []
        for character in self.match_characters:
            alignment = character.alignement
            if character.is_in_play() and alignment not in alignments:
                alignments.append(alignment)
                if len(alignments) > 1:
                    return False
        return True

    def get_fitness(self, strategy_name):
        value = 0
        for character in self.match_characters:
            if self.strategy_manager.get_strategy(character) == strategy_name:
                for resource in character.resources:
                    value += resource.get_quantity * resource.value
        return value

    def add_actions(self, action_set):
        self.action_set_stack.append(action_set)


class InitiativeSet(BasicContext):
    def __init__(self):
        self.characters = []
        self.turn_order = {}
        self.initiatives = []
        self.current_initiative = math.inf
        self.current_characters = []

    def get_next_character(self):
        character = None

        if len(self.current_characters) > 0:
            character = self.current_characters[0]
            if not character.is_turn():
                self.current_characters.pop()
                self.trigger_start()
        else:
            self.load_current_characters()
            self.trigger_start()

        return character

    def trigger_start(self):
        if len(self.current_characters) > 0:
            self.current_characters[0].trigger_hook(START_OF_TURN)

    def load_current_characters(self):
        i = 0
        initiative = self.initiatives[i]
        while self.current_initiative >= initiative:
            i += 1
            if i >= len(self.initiatives):
                i = 0
                self.current_initiative = math.inf
            initiative = self.initiatives[i]
        self.current_initiative = initiative
        self.current_characters = self.turn_order[initiative]

    def add_character(self, character):
        initiative = character.get_initiative()
        turns = self.turn_order[initiative]
        if turns is None:
            turns = [character]
            self.turn_order[initiative] = turns
            self.initiatives.append(initiative)
        else:
            turns.append(character)

        self.characters.append(character)
        self.initiative.sort(reverse=True)


class MatchCharacter(Character):
    def __init__(self, properties, name='', base=None):
        if name == '':
            name = properties[NAME]
        super().__init__(properties, name, base)
        self.alignment = MatchAlignment(name=properties[ALIGNMENT])
        self.match = None
        self.in_play = True
        self.is_turn = False
        self.resources = MatchResourceSet()
        self.add_abilities(self.abilities.values())
        self.hook_map = {}
        self.hook_targeting = {}
        self.effect_map[ATTACK] = self.attack
        self.effect_map[CREDIT] = self.credit
        self.effect_map[DEBIT] = self.debit
        self.effect_map[SET] = self.set_func
        self.effect_map[END_TURN] = self.end_turn
        self.effect_map[REMOVAL_FROM_PLAY] = self.remove_from_play

        x = properties[POSITION][0]
        y = properties[POSITION][1]
        self.set(POSITION, Tile(x, y))

    def add_abilities(self, abilities):
        for ability in abilities:
            self.add_ability(ability)

    def add_ability(self, ability):
        self.add_hook(ability[HOOK][PROFILE], ability[TRIGGER])

    def add_hook(self, hook, trigger):
        self.hook_map[hook].append(trigger)

    def trigger_hook(self, hook_name):
        for trigger in self.hook_map[hook_name]:
            targeting = get_targeting(self.hook_targeting.get(hook_name), base=self)
            targets = targeting.get_targets()
            target = None
            if len(targets) > 0:
                target = targets[0]
            targeting.act(self.re_context(target), Trigger(trigger))

    def get_actions(self):
        actions = []
        for skill_name in self.skills:
            skill = self.skills[skill_name]
            if self.check_conditions(skill.conditions):
                targeting = get_targeting(expression=skill[TARGETING], base=self)
                actions += targeting.get_actions(skill)
        return actions

    def get_hp(self):
        return self.resources.get(HIT_POINT)

    def is_turn(self):
        return self.is_turn

    def start_turn(self, expression=None):
        self.is_turn = True

    def end_turn(self, expression=None):
        self.is_turn = False

    def is_in_play(self):
        return self.in_play

    def remove_from_play(self, expression=None):
        self.in_play = False

    def attack(self, expression):
        self.set(DAMAGE, self.eval(expression[VALUE]))
        self.trigger_hook(DAMAGE_TAKEN)
        damage = self.get(DAMAGE)
        self.resources.debit(self.resources.get(HIT_POINT), damage)

    def roll(self, expression):
        self.set(CURRENT_ROLL, super().roll(expression))
        self.trigger_hook(ROLL)
        return self.get(CURRENT_ROLL)

    def credit(self, expression):
        self.eval(expression[ARGUMENTS][0]).credit(expression[ARGUMENTS][1], expression[ARGUMENTS][2])

    def debit(self, expression):
        self.eval(expression[ARGUMENTS][0]).debit(expression[ARGUMENTS][1], expression[ARGUMENTS][2])

    def set_func(self, expression):
        self.eval(expression[ARGUMENTS][0]).set(expression[ARGUMENTS][1], expression[ARGUMENTS][2])


class MatchAlignment(BasicContext):
    def __init__(self, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.function_map[INITIATIVE] = self.get_initiative


class MatchAction(BasicContext):
    def __init__(self, actor, skill, target, targeting, properties=None, name='', base=None):
        super().__init__(properties=properties, name=name, base=base)
        self.actor = actor
        self.target = target
        self.targeting = targeting
        self.trigger = skill[TRIGGER]

    def act(self):
        self.targeting.act(self.re_context(self.target), self.trigger)


class Targeting(BasicContext):
    def __init__(self, expression, name='', base=None):
        if name == '':
            name = expression[PROFILE]
        super().__init__(expression, name, base)

    def get_actions(self, skill):
        targets = self.get_targets()
        return [MatchAction(self.base, skill, target, self, base=skill) for target in targets]

    def get_targets(self):
        return []

    def act(self, context, trigger):
        trigger = context.re_context(trigger)
        if trigger.check_conditions():
            for effect in trigger.success_effects:
                context.affect(effect)
        else:
            for effect in trigger.failaure_effects:
                context.affect(effect)
        for effect in trigger.effects:
            context.affect(effect)


class SelfTargeting(Targeting):
    def __init__(self, expression, name='', base=None):
        super().__init__(expression, name, base)

    def get_targets(self):
        return [self.base]


class SingleTargeting(Targeting):
    def __init__(self, expression, name='', base=None):
        super().__init__(expression, name, base)

    def get_targets(self):
        return [self.get_match().match_characters]


# TODO: add more targeting
def get_targeting(expression=None, base=None):
    if expression[PROFILE] == ATTACK:
        return SingleTargeting(expression=expression, base=base)
    else:
        return SelfTargeting(expression=expression, base=base)


class Trigger(BasicContext):
    def __init__(self, expression, name='', base=None):
        super().__init__(expression, name=name, base=base)
        self.conditions = expression.get(CONDITIONS)
        self.effects = expression.get[EFFECTS]
        self.success_effects = expression.get(SUCCESS_EFFECTS)
        self.failure_effects = expression.get(FAILURE_EFFECTS)

        if self.conditions is None:
            self.conditions = []
        if self.effects is None:
            self.effects = []
        if self.success_effects is None:
            self.success_effects = []
        if self.failure_effects is None:
            self.failure_effects = []


class MatchResourceSet(BasicContext):
    def __init__(self, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.resource_definitions = []
        self.resources = {}

    def add_resource(self, resource):
        self.resource_definitions.append(resource)
        self.get(resource.name).set_initial()

    def get(self, key):
        if key in [resource.name for resource in self.resource_definitions]:
            if self.resources[key] is None:
                return MatchResource(self.resources[key], self, name=key)
        else:
            return super().get(key)

    def credit(self, resource, value):
        self.set_func(resource, resource.quantity + value)

    def debit(self, resource, value):
        self.set_func(resource, resource.quantity - value)

    def set_func(self, resource, value):
        name = resource.name
        resource.quantity = value
        if value > 0:
            self.resources[name] = resource
        else:
            if name in self.resources:
                self.resources.pop(name)


class MatchResource(BasicContext):
    def __init__(self, expression, resource_set, name='', base=None):
        super().__init__(expression, name, base)
        self.quantity = 0
        self.resource_set = resource_set
        self.initial = expression.get(INITIAL)
        self.max_value = expression.get(MAX_VALUE)
        self.compulsory = expression.get(COMPULSORY)

    def set_initial(self):
        self.resource_set.set_func(self, self.initial)

    def credit(self, key, value):
        self.resource_set.credit(self, value)

    def debit(self, key, value):
        self.resource_set.debit(self, value)

    def set_func(self, key, value):
        self.resource_set.set_func(self, value)

    def get_quantity(self):
        return self.quantity

    def get_damage(self):
        return self.max_value - self.quantity if self.max_value is not None else self.quantity


class Board(BasicContext):
    def __init__(self, width, height, base=None):
        super().__init__({}, base)
        self.width = width
        self.height = height


class Tile(BasicContext):
    def __init__(self, x, y, base=None):
        super().__init__({}, base)
        self.x = x
        self.y = y


# Strategy

class StrategyManager:
    def __init__(self, environment, match_data, expression):
        self.environment = environment
        self.character_templates = []
        self.match_data = match_data
        self.match = None
        self.maximum_turns = expression[MAXIMUM_TURNS]
        self.simulations_per_generation = expression[SIMULATIONS_PER_GENERATION]
        self.novel_strategy_count = expression[NOVEL_STRATEGY_COUNT]
        self.cloned_strategy_count = expression[CLONED_STRATEGY_COUNT]
        self.mutated_strategy_count = expression[MUTATED_STRATEGY_COUNT]
        self.merged_strategy_count = expression[MERGED_STRATEGY_COUNT]
        self.max_strategy_complexity = expression[MAX_STRATEGY_COMPLEXITY]
        self.mutation_coefficient = expression[MUTATION_COEFFICIENT]
        self.fitness_improvement_threshold = expression[FITNESS_IMPROVEMENT_THRESHOLD]
        self.strategy_grouping = expression[STRATEGY_GROUPING]

        self.strategies = {}
        for character in match_data[CHARACTERS]:
            match_character = MatchCharacter(character, base=environment.characters[character[NAME]])
            self.character_templates.append(match_character)
            strategy_name = match_character.eval(self.strategy_grouping)
            if strategy_name not in self.strategies:
                self.strategies[strategy_name] = Strategy(environment, strategy_name)

    def get_match(self):
        return self.match

    def get_strategy(self, character):
        strategy_name = character.eval(self.strategy_grouping)
        if self.strategies[strategy_name] is None:
            self.strategies[strategy_name] = Strategy(self, strategy_name)
        return self.strategies[strategy_name]

    def optimize(self, strategy_name):
        cloneable_strategies = []
        mutateable_strategies = []
        mergeable_strategies = []

        last_fitness = -math.inf
        best_strategy = Strategy(self, strategy_name)
        strategies = []
        while (best_strategy is None
               or (((last_fitness * self.fitness_improvement_threshold) + last_fitness) < best_strategy.fitness)):
            last_fitness = best_strategy.fitness

            for i in range(self.novel_strategy_count):
                strategies.append(Strategy(self, strategy_name))
            while len(cloneable_strategies) > 0:
                strategies.append(cloneable_strategies.pop())
            while len(mutateable_strategies) > 0:
                strategies.append(mutateable_strategies.pop().mutate())
            while len(mergeable_strategies) > 1:
                strategy1 = mergeable_strategies.pop()
                strategy2 = mergeable_strategies.pop()
                strategies.append(strategy1.merge(strategy2))

            for strategy in strategies:
                fitness = 0
                for i in range(self.simulations_per_generation):
                    self.strategies[strategy_name] = strategy
                    match_context = MatchContext(self.environment, self.match_data, self)

                    self.match = match_context
                    match_context.simulate()
                    fitness += match_context.get_fitness(strategy_name)
                    self.match = None

                strategy.fitness = fitness / self.simulations_per_generation

                cloneable_strategies.append(strategy)
                mutateable_strategies.append(strategy)
                mergeable_strategies.append(strategy)

                if strategy.fitness > best_strategy.fitness:
                    best_strategy = strategy

            self.trim_cloneable(cloneable_strategies)
            self.trim_mutateable(mutateable_strategies)
            self.trim_mergeable(mergeable_strategies)
            random.shuffle(mergeable_strategies)

        self.strategies[strategy_name] = best_strategy

    def trim_cloneable(self, strategies):
        return trim(strategies, self.cloned_strategy_count, lambda strategy: strategy.fitness)

    def trim_mutateable(self, strategies):
        return trim(strategies, self.mutated_strategy_count, lambda strategy: strategy.fitness)

    def trim_mergeable(self, strategies):
        return trim(strategies, self.merged_strategy_count, lambda strategy: strategy.fitness)

    def is_ongoing(self, match_context):
        return (match_context.not_conflict()) and (match_context.turn <= self.maximum_turns)

    def get_random_weight(self):
        return random.randint(0, 10)


class Strategy:
    def __init__(self, strategy_manager, name='', nodes=None):
        self.strategy_manager = strategy_manager
        self.name = name
        self.fitness = 0
        if nodes is None:
            nodes = [Node(strategy_manager, strategy_manager.get_random_weight())]
        self.nodes = nodes

    def merge(self, strategy):
        return Strategy(self.strategy_manager, self.name, self.nodes+strategy.nodes)

    def mutate(self):
        return Strategy(self.strategy_manager, self.name)

    def choose_action(self, action_list):
        weights = {}
        for action in action_list:
            weights[action] = 0
            for node in self.nodes:
                weights[action] += node.weigh(action)

        best_action = None
        largest_weight = -math.inf
        for action in weights:
            weight = weights[action]
            if weight > largest_weight:
                largest_weight = weight
                best_action = action

        return best_action


class Node:
    def __init__(self, strategy_manager, weight=0):
        self.strategy_manager = strategy_manager
        self.condition = MetaCondition(strategy_manager)
        self.action = MetaAction(strategy_manager)
        self.weight = weight

    def mutate(self):
        return Node(self.strategy_manager, self.weight+random.randint(-1, 1))

    def weigh(self, action):
        if self.check_action(action):
            return self.weight
        else:
            return 0

    def check_action(self, action):
        return self.condition.check() and self.action.check(action)


class MetaCondition(BasicContext):
    def __init__(self, strategy_manager, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.strategy_manger = strategy_manager
        self.target = random.choice(strategy_manager.character_templates)
        self.status = get_meta_status(strategy_manager)

    def check(self):
        return self.status.check(self.target)


def get_meta_status(strategy_manager):
    if random.randint(0, 1):
        return HealthMetaStatus(strategy_manager, random.randint(0, 10))
    else:
        return DamageMetaStatus(strategy_manager, random.randint(0, 10))


class HealthMetaStatus(BasicContext):
    def __init__(self, strategy_manager, value, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.strategy_manager = strategy_manager
        self.value = value

    # TODO: change to a percentile check
    def check(self, target):
        return target.get_hp().get_quantity() > self.value


class DamageMetaStatus(BasicContext):
    def __init__(self, strategy_manager, value, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.strategy_manager = strategy_manager
        self.value = value

    # TODO: change to a percentile check
    def check(self, target):
        return target.get_hp().get_damage() > self.value


class MetaCharacter(BasicContext):
    def __init__(self, strategy_manager, characters=None, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.strategy_manager = strategy_manager
        if characters is None:
            characters = strategy_manager.character_templates
        characters.append(None)
        self.character = random.choice(characters)

    def check(self, target):
        character = self.character
        if character is None:
            return True
        else:
            return target.name == character.name


class MetaAction(BasicContext):
    def __init__(self, strategy_manager, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.strategy_manager = strategy_manager
        # TODO specify characters
        self.actor = MetaCharacter(strategy_manager)
        act_names = None if self.actor.character is None else [skill.name for skill in self.actor.character.skills]
        name = ''
        if act_names is not None:
            name = random.choice(act_names)
        self.act = MetaAct(strategy_manager, name=name)

    def check(self, action):
        return self.actor.check(action.actor) and self.act.check(action)


class MetaAct(BasicContext):
    def __init__(self, strategy_manager, properties=None, name='', base=None):
        super().__init__(properties, name, base)
        self.strategy_manager = strategy_manager
        self.target = MetaCharacter(strategy_manager)

    def check(self, action):
        return self.target.check(action.target) and action.name == self.name


def create_character(environment, name, expression):
    character = Character(name)
    for key in expression:
        character.set(key, expression[key])
    environment.add_character(character)


def create_resource(environment, name, expression):
    resource = Resource(name)
    resource.set_initial(expression.get(INITIAL))
    for key in expression:
        resource.set(key, expression[key])
    environment.add_resource(resource)


def create_ability(environment, name, expression):
    if is_list(expression):
        environment.add_ability(BasicContextList(name, expression))
    else:
        ability = Ability(name)
        for key in expression:
            ability.set(key, expression[key])
        environment.add_ability(ability)


def create_skill(environment, name, expression):
    if is_list(expression):
        environment.add_skill(BasicContextList(name, expression))
    else:
        skill = Skill(name)
        for key in expression:
            skill.set(key, expression[key])
        environment.add_skill(skill)


# Driver

def unload_config(config):
    environment = Environment()

    characters = get_concretes(config[CHARACTERS])
    for character in characters:
        create_character(environment, character, characters[character])

    resources = get_concretes(config[RESOURCES])
    for resource in resources:
        create_resource(environment, resource, resources[resource])

    abilities = get_concretes(config[ABILITIES])
    for ability in abilities:
        create_ability(environment, ability, abilities[ability])

    skills = get_concretes(config[SKILLS])
    for skill in skills:
        create_skill(environment, skill, skills[skill])

    match_data = get_concretes(config[MATCHES])[config[MATCH]]
    return StrategyManager(environment, match_data, config[STRATEGY])


def load_config():
    config = load('config.json')
    for file in config['configs']:
        deep_fill(config, load(file))
    return config


def load(path):
    if not match(REGEX_LONG_PATH, path):
        path = os.getcwd() + '/config/' + path
    return json.load(open(path))


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


def report_strategies(manager, display):
    for strategy_name in manager.strategies:
        report_strategy(manager.strategies[strategy_name], display)


def report_strategy(strategy, display):
    return


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
