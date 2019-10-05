from basics.basic_methods import *


class Die:
    def __init__(self, rand_func=random.randint):
        self.rand_func = rand_func

    def roll(self, die_count, sides):
        count = 0
        for i in range(die_count):
            count += self.rand_func(1, sides)
            return count


# Models

class BasicContext(MutableMapping, Hashable):
    environment = None
    logger = None

    def __eq__(self, obj):
        if is_map(obj):
            return self.get(NAME) == obj.get(NAME)
        else:
            return False

    def __hash__(self) -> int:
        return str(self).__hash__()

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, value):
        self.properties.__delitem__(value)

    def __getitem__(self, key):
        return self.get(key)

    def __len__(self):
        return self.properties.__len__()

    def __iter__(self):
        return self.properties.__iter__()

    def __init__(self, properties=None, name='', base=None):
        self.base = base
        self.name = name
        self.properties = {NAME: name}
        self.initiative = None
        self.match = None
        self.die = Die()
        self.temp_atr = {}
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

        if properties is not None:
            for key in properties:
                self.set(key, properties[key])

    def context(self, expression, display_message=None):
        return self.get(self.eval(expression[VALUE], display_message=display_message))

    def add(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        count = 0
        for argument in arguments:
            count += self.eval(argument, display_message=display_message)
        return count

    def subtract(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        count = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            count -= self.eval(argument, display_message=display_message)
        return count

    def multiply(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        count = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            count *= self.eval(argument, display_message=display_message)
        return count

    def divide(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        count = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            count /= self.eval(argument, display_message=display_message)
        return count

    def greater(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            if not (value > self.eval(argument, display_message=display_message)):
                return False
        return True

    def less(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            if not (value < self.eval(argument, display_message=display_message)):
                return False
        return True

    def greater_or_equal(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            if not (value >= self.eval(argument, display_message=display_message)):
                return False
        return True

    def less_or_equal(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            if not (value <= self.eval(argument, display_message=display_message)):
                return False
        return True

    def maximum(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            argument_eval = self.eval(argument, display_message=display_message)
            if argument_eval > value:
                value = argument
        return value

    def minimum(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            argument_eval = self.eval(argument, display_message=display_message)
            if argument_eval < value:
                value = argument
        return value

    def func_map(self, expression, display_message=None):
        arguments = (expression[ARGUMENTS])
        collection = self.eval(arguments[0], display_message=display_message)
        func = arguments[1]

        value = []
        for item in collection:
            value.append(item.eval(func, display_message=display_message))

        return value

    def contains(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        value = self.eval(arguments[0], display_message=display_message)
        for argument in arguments[1:]:
            if value is None or self.eval(argument, display_message=display_message) not in value:
                return False
        return True

    def func_and(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        for argument in arguments:
            argument_eval = self.eval(argument, display_message=display_message)
            if not argument_eval:
                return False
        return True

    def func_or(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        for argument in arguments:
            if self.eval(argument, display_message=display_message):
                return True
        return False

    def func_not(self, expression, display_message=None):
        return not self.eval(expression[ARGUMENTS], display_message=display_message)

    def func_get(self, expression, display_message=None):
        arguments = expression[ARGUMENTS]
        return self.eval(arguments[0], display_message=display_message).get(self.eval(arguments[1], display_message=display_message))

    def roll(self, expression, display_message=None):
        roll = self.die.roll(expression[self.eval(DIE_COUNT, display_message=display_message)], expression[self.eval(DIE_SIDES, display_message=display_message)])
        roll_string = str(expression) + "\nCaused a roll of " + str(roll)
        self.log(roll_string)
        if display_message is not None:
            display_message.add_sub_section(roll_string)
        return roll

    def get_initiative(self, expression=None, display_message=None):
        if expression is None:
            expression = self.initiative
        if expression is None:
            expression = self.roll(get_d20())

        match_initiative = self.match_initiative
        if match_initiative is None:
            match_initiative = self.eval(expression, display_message=display_message)
            self.match_initiative = match_initiative
        return match_initiative

    def affect(self, expression, actor=None, display_message=None):
        self.set_temp(ACTOR, actor)
        effect = self.effect_map.get(expression[PROFILE])
        if effect is not None:
            effect(expression, display_message=display_message)
        self.clear_temp(ACTOR)

    def check_conditions(self, conditions=None, display_message=None):
        return self.func_and({ARGUMENTS: conditions}) if conditions is not None else False

    def get_match(self):
        return self.match if self.match is not None else self.base.get_match()

    def set_match(self, match):
        self.set(MATCH, match)
        self.match = match

    def eval(self, expression, display_message=None):
        if is_evaluable(expression):
            key = list(expression.keys())[0]
            func = self.function_map.get(key)
            if func is not None:
                return func(expression[key], display_message=display_message)
            else:
                value = self.get(key)
                return value.eval(expression[key], display_message=display_message) if value is not None else None
        else:
            return expression

    def re_context(self, base):
        klass = BasicContext
        if is_context(base):
            properties = base.properties
            deep_fill(properties, base.base)
            klass = type(base)
        else:
            properties = base
        return klass(properties=properties, base=self)

    def get(self, key):
        if key == INITIATIVE:
            return self.get_initiative()
        elif hasattr(self, str(key)):
            value = getattr(self, str(key))
        else:
            value = self.properties.get(key)

        if (value is None) and (self.base is not None):
            value = self.base.get(key)

        if is_context(value):
            value = self.re_context(value)
        elif is_evaluable(value):
            value = Evaluable(value, base=self)

        if value is None:
            value = self.temp_atr.get(key)

        return value

    def set(self, key, value):
        self.properties[key] = value

        if hasattr(self, key):
            setattr(self, key, value)

    def set_temp(self, key, value):
        self.temp_atr[key] = value

    def clear_temp(self, attribute=None):
        if attribute is not None:
            self.temp_atr.pop(attribute)
        else:
            self.temp_atr = {}

    def log(self, string):
        if self.logger is not None:
            self.logger.log(str(self) + ':\n' + string)

    def __str__(self):
        return type(self).__name__ + ': ' + self.name + ' [' + str(id(self)) + ']'


class Evaluable(BasicContext):
    def __init__(self, properties=None, name='', base=None):
        super().__init__(properties, name, base)


class Environment(BasicContext):
    def __init__(self, properties=None, name='', base=None):
        self.characters = {}
        self.abilities = {}
        self.skills = {}
        self.resources = {}
        self.match_data = None
        super().__init__(properties, name, base)
