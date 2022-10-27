class TermExistsError(Exception):
    def __init__(self, term):
        self.term = term

    def __str__(self):
        return f'The card "{self.term}" already exists. Try again:'


class DefinitionExistsError(Exception):
    def __init__(self, definition):
        self.definition = definition

    def __str__(self):
        return f'The definition "{self.definition}" already exists. Try again:'
