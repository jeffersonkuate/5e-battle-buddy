from basics.basics import Evaluable, BasicContext
from basics import *


def get_d20():
    return {DIE_COUNT: 1, DIE_SIDES: 20}


def pop(expression, key):
    if key in expression:
        return expression.pop(key)
    else:
        return None


def check_and_replace(value, check, replacement):
    if value == check:
        return replacement
    else:
        return value


def select(values, function):
    for value in values:
        if function(value):
            return value
    return None


def map_dict(expression, mapping):
    if is_map(expression):
        for key in expression:
            expression[key] = map_dict(expression[key], mapping)
    elif is_list(expression):
        for index in range(len(expression)):
            expression[index] = map_dict(expression[index], mapping)
    else:
        expression = mapping(expression)

    return expression


def trim(items, threshold, sort_value=lambda x: 0):
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
            elif is_map(value):
                deep_fill(dictionary[key], update.get(key))


def deep_copy(dictionary):
    value = {}
    if is_map(dictionary):
        for key in dictionary:
            value[key] = deep_copy(dictionary.get(key))
        return value
    else:
        return dictionary


def collapse_set(collection, context):
    new_set = []
    for value in collection:
        if is_list(context[value]):
            new_set += collapse_set(context[value], context)
        else:
            new_set.append(context[value])
    return new_set


def create_contexts(expression, context_type, base=None):
    contexts = []
    if is_list(expression):
        for value in expression:
            contexts += create_contexts(value, context_type, base=base)
    else:
        contexts.append(context_type(expression, base=base))
    return contexts


def is_map(context):
    return issubclass(type(context), MutableMapping)


def is_evaluable(expression):
    return issubclass(type(expression), dict) or issubclass(type(expression), Evaluable)


def is_list(expression):
    return issubclass(type(expression), MutableSequence)


def is_context(context):
    return issubclass(type(context), BasicContext)


def checked_input(display, string='', prompt='', reg=REGEX_ALL):
    user_input = display.input(string, prompt)
    while not re_match(reg, user_input):
        display_invalid(display)
        user_input = display.input(string, prompt)
    return user_input


def display_invalid(display):
    display.input(INVALID, PROMPT_ENTER)


def re_search(reg, string):
    return not (re.search(reg.lower(), string.lower()) is None)


def re_match(reg, string):
    return not (re.match(reg.lower(), string.lower()) is None)
