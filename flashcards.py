import flashcard_engine
import console_parser


def main():
    flashcard = flashcard_engine.Flashcard()
    parser = console_parser.ConsoleParser()
    parser.start()

    if parser.import_file is not None:
        flashcard.import_from_file(parser.import_file)

    flashcard.start()

    if parser.export_file is not None:
        flashcard.export_from_file(parser.export_file)


if __name__ == '__main__':
    main()
