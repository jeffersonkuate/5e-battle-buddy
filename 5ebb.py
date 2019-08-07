import display


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


def populate_game(game):
    pass


def evaluate(expression, context):
    pass


def report_strategy(strategy, display):
    pass


def main():
    game = Game()
    populate_game(game)

    strategy = Strategy(game)
    for alignment in game.alignments:
        strategy.optimize(alignment)
        report_strategy(strategy)


if __name__ == '__main__':
    main()
