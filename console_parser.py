import argparse


class ConsoleParser:
    def __init__(self):
        self.import_file = None
        self.export_file = None
        self.parser = argparse.ArgumentParser\
            (description="List of extra functions the program accepts")

    def start(self):
        self.parser.add_argument('-i', '--import_from',
                                 help="Sets an import file to import cards in the program startup")
        self.parser.add_argument('-e', '--export_to',
                                 help="Sets an export file to export cards when the program does finish")

        args = self.parser.parse_args()

        self.import_file = args.import_from
        self.export_file = args.export_to
