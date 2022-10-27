import io

from errors import DefinitionExistsError, TermExistsError
import os
import random
from constants import *


class Flashcard:

    def __init__(self):
        self.existing_cards = []
        self.number_of_cards = 0
        self.log_steam = None
        self.statistics = {}
        self.initialize_logger()

    def start(self):
        """ starting point of the application"""
        self.start_menu()

    def start_menu(self):
        """ shows the MENU based on a list of options
        and gets the menu option from the user.
        Calls a function assigned to such option
        """
        user_choice = self.get_user_input(f'Input the action ({", ".join(MENU_OPTIONS)}):\n')
        if user_choice in MENU_OPTIONS:
            if user_choice == CARD_MENU_OPTION_ADD:
                self.add_card_option()
            elif user_choice == CARD_MENU_OPTION_REMOVE:
                self.remove_card_option()
            elif user_choice == CARD_MENU_OPTION_IMPORT:
                self.import_option()
            elif user_choice == CARD_MENU_OPTION_EXPORT:
                self.export_option()
            elif user_choice == CARD_MENU_OPTION_ASK:
                self.ask_option()
            elif user_choice == CARD_MENU_OPTION_LOG:
                self.save_logs_to_file()
            elif user_choice == CARD_MENU_OPTION_HARDEST:
                self.find_hardest_card()
            elif user_choice == CARD_MENU_OPTION_RESET_STATS:
                self.reset_statistics()
            elif user_choice == CARD_MENU_OPTION_EXIT:
                self.show_message("Bye bye!")
                return
        else:
            if user_choice == "show_logs":
                self.show_message(self.log_steam.getvalue())
            elif user_choice == "print_statistics":
                self.print_statistics()
            else:
                self.show_message("invalid menu option!")

        self.start_menu()

    def add_card_option(self):
        """ Adds a new card by asking the user for terms
        and definitions.
        it calls create_card with the args from user

        Returns
            - the created card or False if it failed
        """
        self.show_message("The card:")

        while True:
            try:
                user_term = self.get_user_input('')
                if self.check_term_exists(user_term):
                    raise TermExistsError(user_term)
            except TermExistsError as err:
                self.show_message(str(err))
                continue
            else:
                card_term = user_term
                break

        self.show_message("The definition of the card:")

        while True:
            try:
                user_definition = self.get_user_input('')
                if self.check_definition_exists(user_definition):
                    raise DefinitionExistsError(user_definition)
            except DefinitionExistsError as err:
                self.show_message(str(err))
                continue
            else:
                card_definition = user_definition
                break

        result = self.create_card(card_term, card_definition)

        if result:
            self.show_message(f'The pair ("{result[0]}":"{result[1]}") has been added.')

        return result

    def remove_card_option(self):
        """ Removes a card from the list of cards by asking the user
        for the term of the card to remove

        Returns
            True if the card was succesfully removed
            False otherwise
        """
        card_term = self.get_user_input("Which card?\n")
        result = self.remove_card(card_term)
        if not result:
            self.show_message(f'Can\'t remove "{card_term}": there is no such card.')
        else:
            self.show_message("The card has been removed.")
        return result

    def ask_option(self):
        """Starts the guess game by asking the user
        how many times he wants to guess and calling
        a random card from the list of cards

        """
        self.show_message("How many times to ask?")
        times_to_ask = self.get_user_input('')
        while not times_to_ask.isdigit():
            self.show_message("Invalid number, try again:\n")
            times_to_ask = self.get_user_input('')
        number_of_questions = int(times_to_ask)
        self.guess_cards(number_of_questions)

    def export_option(self):
        """ Asks the user for the name of the file wich will be used to export
        and calls a function to export cards to the given file
        """
        file_name = self.get_user_input("File name:\n")
        self.export_from_file(file_name)

    def export_from_file(self, file_name):
        with open(file_name, 'w+') as file:
            files_saved = 0
            for index in range(len(self.existing_cards)):
                card = self.existing_cards[index]
                line = f'{card[0]}:{card[1]}:{card[2]:{card[3]}}\n'
                file.write(line)
                files_saved += 1
            self.show_message(f'{files_saved} cards have been saved.')

    def import_option(self):
        """asks the user the name of the file to use as import
        and imports the cards from the file
        """
        file_name = self.get_user_input("File name:\n")
        self.import_from_file(file_name)

    def import_from_file(self, file_name):
        """Imports cards from the given file name

        Params
            - file_name - The name of the file to import
        """
        if os.access(file_name, os.F_OK):
            with open(file_name, 'r', encoding="utf-8") as file:
                added_cards = 0
                for line in file:
                    self.show_message(line)
                    card = line.split(":")
                    card_term = card[0].strip()
                    card_definition = card[1].strip()
                    try:
                        card_incorrects = int(card[2].strip())
                    except IndexError:
                        card_incorrects = 0
                    try:
                        card_corrects = int(card[3].strip())
                    except IndexError:
                        card_corrects = 0
                    if self.check_term_exists(card_term):
                        # pop the existing one
                        self.remove_card(card_term)
                    self.create_card(card_term, card_definition, results=(card_incorrects, card_corrects))
                    added_cards += 1
                self.show_message(f'{added_cards} cards have been loaded')

        else:
            self.show_message("File not found.")

    def create_card(self, term, definition, results=(0, 0)):
        """Creates a card and adds it into the existing_cards list

        Returns
            - the new list of cards
        """

        card = (term, definition, results[0], results[1])
        self.existing_cards.append(card)
        return card

    def remove_card(self, card_term):
        """ removes a card from the list of cards if it exists

        Returns
            True if removed
            False otherwise
        """
        if self.check_term_exists(card_term):
            # find de index of the term
            index = -1
            for i in range(len(self.existing_cards)):
                if self.existing_cards[i][0] == card_term:
                    self.existing_cards.pop(i)
                    return True
            return False
        else:
            return False

    def guess_cards(self, times_to_ask):
        """Ask the user for the answer of one of the existing cards
        in the instance existing_cards if there is available

        """
        for _ in range(times_to_ask):
            random.seed()
            card_number = random.randint(0, len(self.existing_cards) - 1)
            card = self.existing_cards[card_number]
            answer = self.get_user_input(f'Print the definition of "{card[0]}":\n')
            if answer == card[1]:
                self.update_statistics(card[0], True)
                self.print_result(True)
            else:
                # check if the answer exists in another card
                definition_exist = self.check_definition_exists(answer)
                self.update_statistics(card[0], False)
                if definition_exist:
                    self.print_result(False, card[1], definition_exist)
                else:
                    self.print_result(False, card[1])

    def print_result(self, result: bool, correct_answer: str = '', secondary_card=None):
        """Prints the result of the user guess"""
        if result:
            self.show_message(CARD_GUESS_CORRECT)
        else:
            if secondary_card is not None:
                self.show_message(CARD_GUESS_INCORRECT_SECONDARY.replace('&', correct_answer).replace('%', secondary_card[0]))
            else:
                self.show_message(CARD_GUESS_INCORRECT.replace('&', correct_answer))

    def print_card_information(self, card_information: tuple[str, str]) -> bool:
        """Prints the flashcard information

        Params
            - card_information -> tuple[str,str]
                * index 0 -> term
                * index 1 -> definition

        Returns
            - bool
                * True if print is succesful
                * False if it fails

        """
        try:
            self.show_message(CARD_TEXT)
            self.show_message(card_information[0])
            self.show_message(DEFINITION_TEXT)
            self.show_message(card_information[1])
        except Exception:
            self.show_message("Error while printing card information")
            return False
        else:
            return True

    def get_card_index_by_term(self, term):
        """ returns the first card that has the given term

        :param term: - the term to search
        :return: the card
        :return: None if no card was found
        """
        for card_index in range(len(self.existing_cards)):
            if self.existing_cards[card_index][0] == term:
                return card_index
        return None

    def check_term_exists(self, term) -> bool:
        """Checks if the term exist in the list of existing cards

        Returns
            True if it exist
            False if not
        """
        result = [card for card in self.existing_cards if card[0] == term]
        return len(result) > 0

    def check_definition_exists(self, definition) -> bool:
        """Checks if the definition exist in the list of existing cards

        Returns
            True if it exist
            False if not
        """
        result = [card for card in self.existing_cards if card[1] == definition]
        return result[0] if len(result) > 0 else False

    def initialize_logger(self):
        """Starts a logging based on in-memory text buffer

        Returns
            - Logger instance pointing a text buffer
        """

        # Create the string io to store the log steams
        self.log_steam = io.StringIO()

    def save_logs_to_file(self):
        """Saves the programm log history from Stringio into a
        file chosen by the user
        """
        file_name = self.get_user_input("File name:\n")
        try:
            with open(file_name, 'w', encoding="utf-8") as f:
                f.write(self.log_steam.getvalue())
        except Exception:
            self.show_message("Failed while saving log file")
        else:
            self.show_message("The log has been saved.")

    def reset_statistics(self):
        """
        Resets the statistics dictionary
        """
        for card_index, card in enumerate(self.existing_cards):
            new_card = (card[0], card[1], 0, 0)
            self.existing_cards[card_index] = new_card
        self.show_message("Card statistics have been reset.")

    def print_statistics(self):
        """
        Prints the statistics dictionary in json format
        """
        for card in self.existing_cards:
            print(f'card {card[0]} has {card[3]} correct answers and {card[2]} incorrect answers')

    def find_hardest_card(self):
        highest_card = []
        highest_card_score = 0
        for card in self.existing_cards:
            current_card_incorrect_score = card[2]
            if current_card_incorrect_score > 0 and current_card_incorrect_score > highest_card_score:
                highest_card = [card[0]]
                highest_card_score = current_card_incorrect_score
            elif current_card_incorrect_score > 0 and current_card_incorrect_score == highest_card_score:
                highest_card.append(card[0])
            else:
                pass  # nothing to do here
        # build hardest card message
        message = ''
        if len(highest_card) == 1:
            message = f'The hardest card is "{"".join(highest_card)}". You have {highest_card_score} errors answering it.'
        elif len(highest_card) > 1:
            cards_str_list = [f'"{x}"' for x in highest_card]
            message = f'The hardest cards are {", ".join(cards_str_list)}'
        else:
            message = 'There are no cards with errors.'
        self.show_message(message)
        return highest_card, highest_card_score

    def update_statistics(self, term, result):
        """ Stores and updates statistics on the card
        
        :param term: the term (key) to be updated / created
        :param result: if result was correct or incorrect
        """""
        if self.check_term_exists(term):
            card_index = self.get_card_index_by_term(term)
            if card_index is not None:
                mutated_card = list(self.existing_cards[card_index])
                if result:
                    mutated_card[3] += 1
                else:
                    mutated_card[2] += 1

                self.existing_cards[card_index] = mutated_card
            else:
                self.show_message("Card does not exist, cannot update statistics")
        else:
            self.show_message("Term does not exist. statistics couldn't be updated")

    def get_user_input(self, message):
        input_result = input(message)
        self.log_steam.write(message)
        self.log_steam.write(input_result + '\n')
        return input_result

    def show_message(self, message):
        """ shows the message into the console
        and logs it into the logger string steam

        :param message: The message to log
        """
        print(message)
        self.log_steam.write(message + "\n")
