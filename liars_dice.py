#!/usr/bin/env python3

import random
from math import factorial, pow

class Game(object):
    def __init__(self):
        self.players = []
        self.bids = []
        self.next_players_turn = None
        self.next_move_possible = None
        self.dice_in_middle = []
        # current_bid : (total_count_bid, dice_value)
        self.current_bid = (0, 0)

    def new(self, player_count):
        if player_count < 2:
            raise ValueError("Need at least two players!")

        for n in range(player_count):
            self.players.append(Player(n))
        self.next_players_turn = 0
        self.next_move_possible = ["move", "claim"]

    def restart(self, player_count):
        self.players.clear()
        self.bids.clear()
        self.next_players_turn = None
        self.next_move_possible = None
        self.dice_in_middle.clear()
        self.current_bid = (0, 0)
        self.new(player_count)

    def show_game_status(self):
        print(f"Currently, it is player {self.next_players_turn}'s turn.")
        print(f"He can chose any of these moves: {', '.join(self.next_move_possible)}.")
        print(f"Dice in the middle:\n\t{self.dice_in_middle}")
        for player in self.players:
            print(f"Player {player.name}:\n\t{player.remaining_dice}")

    def move(self, player_number, dice_value, count):
        if player_number != self.next_players_turn:
            raise ValueError(f"It is player {self.next_players_turn}'s turn, not player {player_number}'s turn.")

        if 'move' not in self.next_move_possible:
            raise ValueError(f"Player must perform game operation {' '.join(self.next_move_possible)}, not 'move'")

        if 5 < count < 0:
            raise ValueError(f"Player must move between 0 and 5 dice into the middle!")

        curr_player = self.get_player(player_number)
        returned_dice = curr_player.get_dice(dice_value, count)
        for die in returned_dice:
            self.dice_in_middle.append(die)
        self.next_move_possible = ["claim"]

    def get_player(self, player_number):
        for player in self.players:
            if player.name == player_number:
                return player

    def claim(self, player_number, dice_count_bid, dice_value):
        if player_number != self.next_players_turn:
            raise ValueError(f"It is player {self.next_players_turn}'s turn, not player {player_number}'s turn.")

        if 'claim' not in self.next_move_possible:
            raise ValueError(f"Player must perform game operation {' '.join(self.next_move_possible)}, not 'claim'")

        if dice_count_bid < self.current_bid[0]:
            raise ValueError(
                f"Player must claim/bid a higher number than the current guess which is {self.current_bid[0]}"
            )

        if 6 < dice_value < 1:
            raise ValueError(f"Player had an incorrect dice value... Must be between 1 and 6.")

        curr_player = self.get_player(player_number)
        self.current_bid = (dice_count_bid, dice_value)
        self.calcualate_bid_odds()

        curr_player.shuffle_remaining_dice()
        self.next_players_turn += 1 if curr_player.name != len(self.players) - 1 else 0
        self.next_move_possible = ["move", "claim", "challenge"]

    def calcualate_bid_odds(self):
        odds = 0.0
        total_dice = len(self.players) * 5
        for num in range(self.current_bid[0], total_dice + 1):
            odds += self.calc_odds_single_guess(total_dice, num)
        print(f"The odds of there being at least {self.current_bid[1]} dice in the game are {odds:.20f}")

    def calc_odds_single_guess(self, n, k):
        return (factorial(n) / (factorial(k) * factorial(n - k))) * pow((1/6), k) * pow(5/6, n - k)

    def challenge(self, player_number):
        challenger = player_number
        challenged = player_number - 1 if player_number != 0 else len(self.players) - 1
        print(f"Player number {challenger} is challenging player number {challenged} that there are "\
               f"{self.current_bid[0]} or more dice of value {self.current_bid[1]} in play right now!")

        challenger_wins, actual_num = self.challenger_wins()

        if challenger_wins:
            print(f"Player number {challenger} correctly challenged! There are {actual_num} occurences of the dice " \
                    f"with value {self.current_bid[1]}")
        else:
            print(f"Player number {challenger} incorrectly challenged! There are {actual_num} occurences of the " \
                    f"dice with value {self.current_bid[1]}")

    def challenger_wins(self):
        running_num = 0
        for die in self.dice_in_middle:
            if die.value == self.current_bid[1]:
                running_num += 1
        for player in self.players:
            for die in player.remaining_dice:
                if die.value == self.current_bid[1]:
                    running_num += 1
        if running_num >= self.current_bid[0]:
            return (True, running_num)
        else:
            return (False, running_num)


class Player(object):
    def __init__(self, player_number):
        self.name = player_number
        self.remaining_dice = []
        self.in_turn = True
        self.initialize_dice()

    def initialize_dice(self):
        for _ in range(5):
            self.remaining_dice.append(Dice())

    def shuffle_remaining_dice(self):
        for die in self.remaining_dice:
            die.reroll()

    def get_dice(self, dice_value, count):
        if count > self.get_count_of_dice_value(dice_value):
            raise ValueError(
                f"Player {self.name} tried to move {count} dice into the middle, and he doesn't " \
                f"have that many dice of value {dice_value}. He only has {self.get_count_of_dice_value(dice_value)} " \
                f"dice of value {dice_value}. Try Again!"
            )
        returned_dice = []
        for die in self.remaining_dice:
            if die.value == dice_value and len(returned_dice) < count:
                returned_dice.append(die)

        for die in returned_dice:
            self.remaining_dice.remove(die)

        return returned_dice

    def get_count_of_dice_value(self, dice_value):
        num_of_dice = 0
        for die in self.remaining_dice:
            if dice_value == die.value:
                num_of_dice += 1
        return num_of_dice


    def __repr__(self):
        return f"Player Number {self.name}"


class Dice(object):
    def __init__(self):
        self.value = 0
        self.reroll()

    def reroll(self):
        self.value = random.randint(1,6)

    def __repr__(self):
        return f"Die Value: {self.value}"
