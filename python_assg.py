import time
import random

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.inventory = []

def introduction():
    print("Welcome to the Epic Adventure Game!")
    print("You wake up in a medieval kingdom. Your mission awaits.")

def make_choice(options):
    print("\nChoose your action:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return choice
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def battle_enemy(player):
    print("\nYou encounter an enemy!")
    enemy_health = random.randint(50, 100)

    while player.health > 0 and enemy_health > 0:
        print(f"\nYour health: {player.health} | Enemy health: {enemy_health}")
        print("1. Attack")
        print("2. Retreat")

        choice = make_choice(["Attack", "Retreat"])

        if choice == 1:
            damage_to_enemy = random.randint(10, 20)
            damage_to_player = random.randint(5, 15)

            enemy_health -= damage_to_enemy
            player.health -= damage_to_player

            print(f"\nYou dealt {damage_to_enemy} damage to the enemy.")
            print(f"The enemy dealt {damage_to_player} damage to you.")

        elif choice == 2:
            print("\nYou chose to retreat from the battle.")
            return

    if player.health <= 0:
        print("\nYou were defeated in battle. Game over.")
        exit()
    else:
        print("\nYou defeated the enemy! You gain a valuable item.")
        player.inventory.append("Valuable Item")

def explore_kingdom(player):
    print("\nYou explore the kingdom and find various locations.")
    time.sleep(2)

    options = ["Visit the Tavern", "Enter the Dark Forest", "Check the Castle Courtyard"]
    choice = make_choice(options)

    if choice == 1:
        print("\nYou enter the Tavern and meet some interesting characters.")
        time.sleep(2)
        print("You hear rumors about a hidden cave with treasures.")
        player.inventory.append("Treasure Map")
    elif choice == 2:
        battle_enemy(player)
    elif choice == 3:
        print("\nYou stroll through the Castle Courtyard.")
        time.sleep(2)
        print("You witness a royal event, and the king rewards you.")
        player.inventory.append("Royal Medal")

def main():
    player_name = input("Enter your character's name: ")
    player = Player(player_name)

    introduction()

    while True:
        explore_kingdom(player)

        print("\nCurrent Status:")
        print(f"Player: {player.name} | Health: {player.health} | Inventory: {player.inventory}")

        play_again = input("Do you want to continue exploring? (yes/no): ").lower()
        if play_again != 'yes':
            print("Thanks for playing! Goodbye.")
            break

if __name__ == "__main__":
    main()
