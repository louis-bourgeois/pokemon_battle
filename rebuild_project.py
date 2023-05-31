""" JEUX VIDEO : TERMINAL POKEMON REMASTERED"""
import random
import json
import sys
import atexit
import difflib

with open('pokemon_data.json', encoding='utf-8') as json_file:
    pokemons_data = json.load(json_file)
pokemons_data["initial_names"] = ["leSpire",
"Louis", "Ikil_Ikon", "Chantal", "Robin", "Escanor", "Squeezie", "Sponsorisateur", "Sardoche"]
with open('pokemon_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(pokemons_data, json_file)
with open('pokemon_data.json', encoding='utf-8') as json_file:
    pokemons_data = json.load(json_file)
pokemons_data['names'] = pokemons_data['initial_names']
with open('pokemon_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(pokemons_data, json_file)

LIST_OF_POTIONS = ['TOXIC', 'HEALTH', 'SUPER_HEALTH']
PROBAS = [0.3365, 0.5385, 0.05]


def random_potions_attribution():
    """ Attribue des potions aléatoires"""
    return random.choices(LIST_OF_POTIONS, PROBAS)[0]


class Game:
    """
    No required parameters
    Classe principale permettant d'effectuer les principales actions
    Contient les infos les plus importantes relatives au bon déroulement des tours
    """

    def __init__(self):
        self.number_players = None
        self.players_names: list = []
        self.players_instance: list = []
        self.authorized_answer_number_players: list = ["2", "3", "4"]
        self.error_not_in_list = "Veuillez choisir un pokémon figurant dans la liste !"
        self.present_pokemons = []
        self.alive_pokemon = []
        self.dead_pokemon = []
        self.a_pokemon_has_no_full_hp: bool = False
        self.round_instance = None
        self.choice_1 = None
        self.formatted_names_line = None
        self.get_number_players()
        self.create_players()
        self.generate_order()
        self.ask_pokemon()
        self.start()

    def get_number_players(self):
        """
        Pas de changements à effectuer ici,
        la fonction prend en entrée un input str du nb de joueurs et le vérifie puis le renvoie.
        """
        while True:
            self.number_players = input("""
            Bonjour, 
            Quel sera le nombre de joueurs lors de cette partie ?
            Rappel : Ce mode se joue à au moins 2 joueurs, et au maximum 4 joueurs.
            Votre choix : """
                                        )
            if self.number_players in self.authorized_answer_number_players:
                self.number_players = int(self.number_players)
                return self.number_players
            else:
                print("\nVeuillez entrer un nombre valide.")
                continue

    def create_players(self):
        """
        Fonctionne parfaitement :
        boucle for itérant sur nb players et crée une instance de Player avec un id unique
        """
        if isinstance(self.number_players, int):
            for iterations in range(self.number_players):
                instance = Player(self, iterations + 1)
                self.players_instance.append(instance)
        else:
            print("Erreur critique : le nombre de joueur doit être un integer")

    def generate_order(self):
        """ Aucun prob. Mélange players names et print avec une boucle for itérant sur cette liste 
        l'ordre des players """

        random.shuffle(self.players_instance)
        print("Voici l'ordre aléatoire des joueurs pour cette partie :")
        for iteration, instance in enumerate(self.players_instance):
            print(f"{iteration + 1}. {instance.name}")
            self.players_names.append(instance.name)
        print()

    def validate_pokemon_choice(self, prompt):
        """ Valide le choix de "ask pokemon", et renvoie la variable error s'il y a une erreur """

        while True:
            choice = input(prompt)
            choice = choice.capitalize()
            if choice not in pokemons_data["names"]:
                closest_choice = difflib.get_close_matches(
                    choice, pokemons_data["names"])
                if closest_choice:
                    choice = closest_choice[0]
                    pokemons_data["names"].remove(choice)
                    self.formatted_names_line = ", ".join(
                        pokemons_data["names"])
                    with open('pokemon_data.json', 'w', encoding='utf-8') as file:
                        json.dump(pokemons_data, file)
                    return choice
                else:
                    print(self.error_not_in_list)

            else:
                pokemons_data["names"].remove(choice)
                self.formatted_names_line = ", ".join(pokemons_data["names"])
                with open('pokemon_data.json', 'w', encoding='utf-8') as file:
                    json.dump(pokemons_data, file)
                return choice

    def ask_pokemon(self):
        """ Méthode permettant de demander à chaque joueur leurs pokémons parmi une liste """

        self.formatted_names_line = ", ".join(pokemons_data["names"])
        for instance in self.players_instance:
            print(f'''{instance.name},
            Veuillez choisir 3 pokémons parmi cette liste :\n
            {self.formatted_names_line}
            
RAPPEL : Les pokémon choisis ne seront pas disponible pour les joueurs suivants.
 ''')
            while True:
                self.choice_1 = self.validate_pokemon_choice("Choix 1 : ")
                choice_2 = self.validate_pokemon_choice("Choix 2 : ")
                choice_3 = self.validate_pokemon_choice("Choix 3 : ")
                instance.alive_pokemons.extend(
                    [self.choice_1, choice_2, choice_3])
                self.alive_pokemon.extend(instance.alive_pokemons)
                print("Pokémons " + ", ".join(self.alive_pokemon))
                print(f"\n{instance.name}, voici vos pokémons :")
                for i, inst in enumerate(instance.alive_pokemons):
                    print(f"{i + 1}. {inst}")
                instance.associate_pokemon_instance()
                print(str(instance))
                break

    def start(self):
        """ Méthode démarrant un tour et donc la partie """
        if 6 <= len(self.alive_pokemon) <= 16:
            self.round_instance = Round(
                self.players_instance, self.alive_pokemon)
        return self.round_instance


class Round:
    """ Permet le déroulement du tour (système de tour, etc)"""

    def __init__(self, players_instance, alive_pokemons,):
        self.players_instance = players_instance
        self.active_player = players_instance
        self.current_player = players_instance[0]
        self.current_round = 0
        self.active_pokemons: list = alive_pokemons
        self.current_pokemon:object = object()
        self.a_pokemon_has_no_full_hp = False
        self.action_made = False
        self.start_menu = """
        1. Choisir un pokémon
        2. Abandonner comme une petite pute
        3. Chatter
        Votre choix : 
        """
        self.pokemons_instance = []
        for player in self.players_instance:
            self.pokemons_instance.append(player.its_pokemons_instance)
        self.answers_start = ['1', '2', '3']
        self.answers_menu = ['1', '2', '3', '4', '5', "6"]
        self.main_menu = """
        1. Attaquer
        2. Utiliser une potion
        3. Abandonner comme une pute
        4. Changer de Pokémon
        5. Inventaire
        6. Chatter
        """
        self.menu_inventory = """
        Choix possible :
            1. Remplacer l'actuel Pokémon
            2. Utiliser une potion
            3. Quitter
            
            Votre choix : 
            """
        while True:  # je dois corriger le fait qu'un joueur puisse jouer
            self.action_made = False
            print("Voici un récapitulatif de vos inventaires:")
            for player in self.players_instance:
                player.display_inventory()
            print(f"Le round {str(self.current_round)} démarre.")
            if self.current_round == 0:
                self.start_round()
                continue
            else:
                self.display_main_menu()
                continue

    def start_attack(self):
        """ Start an attack """
        print(f"""{self.current_player.name},
              Veuillez choisir l'attaque à utiliser :
               {', '.join(self.current_pokemon.attacks)}""")
        return

    def say(self, message):
        """ Allows to the player to say something """
        while True:

            if len(message) > 100:
                print("Votre message est trop long")
                message = input("Veuillez ressaisir votre message : ")
                continue
            else:
                print(f"\n{self.current_player.name} : {message}")
                break
        return message

    def change_pokemon(self):
        " Allows to change active pokemon "
        while True:
            print(self.current_player.name + ", \nVos Pokémons : " +
                  ", ".join(self.current_player.its_pokemons) + "\n")
            user_choice = input("""Parmi vos Pokémons lequel voulez vous choisir ?
            Votre choix : 
            """)
            found_pokemon = False
            for instance in self.current_player.its_pokemons_instance:
                if user_choice.capitalize() == instance.name:
                    if instance.is_alive:
                        found_pokemon = True
                        self.current_pokemon= self.current_player.current_pokemon = instance
                        print(f"""\n{self.current_player.name} a changé de pokémon.
                        Nouveau Pokémon : {self.current_pokemon.name}
                        {self.current_pokemon}""")
                        self.action_made = True
                        return
                    else:
                        print("""Le pokémon est mort. RIP""")
                        break
                else:
                    closest_choice = difflib.get_close_matches(user_choice.capitalize(),
                                                               [instance.name], n=1, cutoff=0.6)
                    if closest_choice:
                        found_pokemon = True
                        user_choice = closest_choice[0]
                        self.current_pokemon = instance
                        print(f"""\n{self.current_player.name} a changé de pokémon.
                        Nouveau Pokémon : {self.current_pokemon.name}
                        {self.current_pokemon}""")
                        self.action_made = True
                        break
                    else:
                        continue

            if not found_pokemon:
                print("Ne figure pas dans la liste des pokémons")

    def display_inventory(self):
        """ Allows to display the inventory of the player """
        while not self.action_made:
            self.current_player.display_inventory()
            user_choice = input("Votre choix : ")
            if user_choice == "1":
                self.change_pokemon()
                self.action_made = True
            elif user_choice == "2":
                self.use_this_potion()
                self.action_made = True
            elif user_choice == "3":
                return

    def use_this_potion(self):
        """ ALLOWS TO USE A POTION AGAINST SOMEBODY OR FOR SOMEBODY """
        used = False
        while not used:
            user_choice = input(f"""Parmi vos potions, lequel voulez vous utiliser ?
                                {", ".join(self.current_player.its_potions)}
                                Votre choix : """)
            user_choice = user_choice.upper()
            if len(self.current_player.its_potions) == 0:
                print("Vous n'avez plus de potions")
                self.action_made = False
                return

            if user_choice not in self.current_player.its_potions:
                closest_choice = difflib.get_close_matches(user_choice,
                                                           self.current_player.its_potions,
                                                           n=1, cutoff=0.8)
                if closest_choice:
                    user_choice = closest_choice[0]
                    self.potion_1(user_choice)
                    used = True
                    self.action_made = True
                else:
                    print("Votre potion n'est pas valide")
                    continue
            else:
                self.potion_1(user_choice)
                used = True
                self.action_made = True

    def potion_1(self, user_choice):
        """ Sequel of use potion"""
        for instance in self.current_player.its_potion_instance:
            self.current_player.its_potion_instance.remove(instance)
            self.current_player.its_potions.remove(instance.name)
            if instance.name == user_choice:
                potion_found = True
                self.action_made = True
                for _ in self.pokemons_instance:
                    if user_choice.upper() == "TOXIC":
                        user_choice = "TOXIC"
                        ennemies = [pokemon for player in
self.players_instance if player != self.current_player for pokemon in
                                      player.its_pokemons_instance]
                        while True:
                            print(", ".join(ennemy.name for ennemy in ennemies))

                            target_name = input(
                                """Parmi les pokémons suivants, lequel voulez-vous attaquer ?
                                Choix : """)

                            target = next(
                                (enemy for enemy in ennemies if enemy.name ==
                                 target_name),
                                None
                            )

                            if not target:
                                closest_choice = difflib.get_close_matches(target_name,
[enemy.name for enemy in ennemies], n=1, cutoff=0.6)
                                if closest_choice:
                                    target = closest_choice[0]
                                    target = next(
                                        (enemy for enemy in ennemies if enemy.name ==
                                         target_name),
                                        None
                                    )
                                    if target:
                                        target.is_poisonned = True
                                        break

                                else:
                                    print("Le pokémon ciblé n'est pas valide.")
                                    continue
                            else:
                                target.is_poisonned = True
                                self.action_made = True
                                return
                    elif user_choice.upper() == "SUPERHEALTH" or "HEALTH":
                        if user_choice.upper() == "HEALTH":
                            user_choice = "HEALTH"
                        if user_choice.upper == "SUPERHEALTH":
                            user_choice = "SUPERHEALTH"
                        while True:
                            target_name = input(f"""
                                                Parmi les pokémons suivants, lequel voulez-vous soigner ?
                                                {", ".join(self.current_player.its_pokemons)}
                                                Votre choix : """)

                            target = next((pokemon for pokemon in
self.current_player.its_pokemons_instance if pokemon.name == target_name), None)
                            if not target:
                                closest_choice = difflib.get_close_matches(target_name,
                                                                           [pokemon.name for
pokemon in self.current_player.its_pokemons_instance], n=1, cutoff=0.6)
                                if closest_choice:
                                    target_name = closest_choice[0]
                                    target = next((pokemon for pokemon in
self.current_player.its_pokemons_instance if pokemon.name == target_name), None)
                                    self.action_made = True
                                    return
                                else:
                                    print(
                                        "Le pokémon choisi n'est pas l'un des votre.")
                                    continue
                            else:
                                target.add_hp(instance.gain)
                                self.action_made = True
                                return
            else:
                continue
            if not potion_found:
                print("ERREUR")

    def start_round(self):
        """ Commence et initialize le round """
        checked = 0
        for instance in self.players_instance:
            print(f"{instance.name}, que voulez vous faire ? ")
            self.current_player = instance
            while True:
                user_choice = input(self.start_menu)
                if user_choice not in self.answers_start:
                    print("Veuillez entrer un nombre compris entre 1 et 3")
                    continue
                elif user_choice == self.answers_start[0]:
                    print(", ".join(value for dict_keys,
                                    value in self.current_player.its_pokemons_dict.items()))
                    while True:
                        pokemon_choice = input(
                            "Veuillez entrer le nom du pokémon qui va entamer le combat : ")
                        if pokemon_choice not in self.current_player.its_pokemons:
                            closest_choices = difflib.get_close_matches(
pokemon_choice.capitalize(), [self.current_player.its_pokemons], n=1, cutoff=0.6)
                            if closest_choices:
                                pokemon_choice = closest_choice[0]
                                for pokemon in self.current_player.its_pokemons_instance:
                                    if pokemon.name == closest_choices:
                                        instance.current_pokemon = pokemon
                                        self.current_pokemon = self.current_player.current_pokemon
                                        print(f"{instance.current_pokemon} va entamer le combat\n")
                                        break
                            print("Veuillez entrer un nom valide")
                            continue
                        else:
                            for pokemon in self.current_player.its_pokemons_instance:
                                if pokemon.name == pokemon_choice:
                                    instance.current_pokemon = pokemon
                                    self.current_pokemon = self.current_player.current_pokemon
                                    print(f"{instance.current_pokemon} va entamer le combat\n")
                                    break
                elif user_choice == self.answers_start[1]:
                    print(f"{self.current_player.name} a abandonné le match,")
                    self.active_player.remove(self.current_player)
                    self.current_player = self.active_player
                    print(f"{self.current_player} gagne donc la partie")
                    sys.exit()
                elif user_choice == self.answers_start[2]:
                    message = input(
                        "Veuillez écrire votre message ci-dessous (maximum de 100 mots) :\n"
                    )
                    self.say(message)
                    continue
                else:
                    print("error")
                    break
        for instance in self.players_instance:
            if instance.current_pokemon :
                checked += 1
        if checked == 2:
            self.current_round += 1
            return self.current_round

    def display_main_menu(self):
        "Allows to display the main menu of the round"
        for instance in self.players_instance:
            self.action_made = False
            self.current_player = instance
            print(f"{self.current_player.name},")
            print(self.main_menu)
            while not self.action_made:
                user_choice = input("Votre choix : ")
                if user_choice == "1":
                    self.start_attack()
                    self.action_made = True
                elif user_choice == "2":
                    self.use_this_potion()
                    if self.action_made:
                        break
                    else:
                        continue
                elif user_choice == "3":
                    self.active_player.remove(self.current_player)
                    self.current_player = self.active_player
                    print(f"{self.current_player.name} gagne donc la partie")
                    self.action_made = True
                    break
                elif user_choice == "4":
                    self.change_pokemon()
                    break
                elif user_choice == "5":
                    self.display_inventory()
                    if self.action_made:
                        break
                    else:
                        continue
                elif user_choice == "6":
                    message = input(
                        "Veuillez écrire votre message ci-dessous (maximum de 100 mots) :\n"
                    )
                    self.say(message)
                    continue
                else:
                    print("Veuillez entrer un nombre compris entre 1 et 6")
                    continue


class Player:

    """
    Classe d'un joueur (actif ou non+), permet de lui créer un nom d'avoir ses potions, id,
    son statut, et son game instance relié
    """
    # Required parameters : current game instance, player id ((i+1) in Game.create_player)

    def __init__(self, game_instance, player_id, name=""):
        self.choice: str = ""
        self.its_potions: list = []
        self.its_pokemons: list = []
        self.its_pokemons_instance: list = []
        self.its_potion_instance: list = []
        self.alive_pokemons = []
        self.active = True
        self.player_id = player_id
        self.game_instance = game_instance
        self.its_pokemons_dict = {}
        self.current_pokemon = object()
        if name == "":
            self.name = self.ask_name()
        else:
            self.name = name
        self.give_potions()

    def display_inventory(self):
        """ ALLLOWS TO DISPLAY INVENTORY'S PLAYER """
        print(f"=== Inventaire de {self.name} ===")
        for pokemon in self.its_pokemons_instance:
            print("\n" + "-"*20)
            print(f"Nom : {pokemon.name}")
            print(f"Attaques : {pokemon.attacks_dict}")
            print(f"HP : {pokemon.current_hp}")
            print(f"Énergie : {pokemon.current_energy}")
            print(f"État : {'Alive' if pokemon.is_alive else 'Dead'}")
        print("\n=== Potions ===")
        print("Mes Potions : " + ", ".join(self.its_potions))
        print("=================")
        print()
        input("Appuyez sur une touche pour continuer\n")

    def give_potions(self):
        """ Attribue aléatoirement des potions """

        for _ in range(3):
            potion = random_potions_attribution()
            if potion == LIST_OF_POTIONS[0]:
                instance = Potion(potion, 0, 10, None)
            elif potion == LIST_OF_POTIONS[1]:
                instance = Potion(potion, random.randint(5, 10), 0, None)
            else:
                instance = Potion(potion, random.randint(15, 23), 0, None)

            self.its_potions.append(potion)
            self.its_potion_instance.append(instance)
        print(f"{self.name}, voici vos potions pour la partie")
        for iteration, potion in enumerate(self.its_potions):
            print(f"{iteration + 1}. {potion}")
        print("")

        return self.its_potions, self.its_potion_instance

    def ask_name(self):
        """ ask le nom :str et le retourne """

        self.name = input(f"\nJoueur {self.player_id}, Quel est ton nom ? : ")
        if self.name in self.game_instance.players_names:
            self.name = self.name+"_"+str(self.player_id)
        self.game_instance.players_names.append(self.name)
        return self.name

    def associate_pokemon_instance(self):
        """ Allows to associate each pokmon choice with his instance """
        for pokemon_name in self.alive_pokemons:
            data = pokemons_data["pokemons"][pokemon_name]
            instance = Pokemon(data["name"],
                               data["initial_hp"],
                               data["initial_energy"],
                               list(data["attacks"].keys()),
                               belonging=self
                               )
            self.its_pokemons_dict[instance] = instance.name
            self.its_pokemons_instance.append(instance)
            self.its_pokemons.append(instance.name)

    def is_dead(self):
        """ Méthode permettant de tuer qqn """
        print("T as pas defini .is_dead")

    def __str__(self):
        return f"""
        Nom : {self.name}
        Mes potions : {', '.join(self.its_potions)}
        Mes Pokémons : {', '.join(self.its_pokemons)}

        """


class Pokemon:
    """ Classe d'un pokémon contient les attaques les infos sur l'état, un surnom etc """

    def __init__(self, name: str, initial_hp: int, initial_energy: int, attacks: list,
                 belonging: object):
        self.name = name
        self.initial_hp = initial_hp
        self.current_hp = initial_hp
        self.current_energy: int = initial_energy
        self.initial_energy: int = initial_energy
        self.attacks_dict: dict = {}
        self.attacks: list = attacks
        self.attacks_str: str = ""
        self.is_alive = True
        self.is_poisonned = False
        self.attack_data = pokemons_data["pokemons"][self.name]["attacks"]
        self.belonging = belonging
        self.his_malus = self.check_malus()
        print(str(self))
        self.initialize_my_attacks()

    def is_dead(self):
        """ Change the state of the pokemon to dead """

        self.is_alive = False
        return self.is_alive

    def initialize_my_attacks(self):
        """ Allows to attack, by initialise the attacks """
        for attack in self.attacks:
            if self.name == "Escanor":
                instance = Attack(
                    attack,
                    self.attack_data["Soleil_cruel"]["description"],
                    list(self.attack_data["Soleil_cruel"]["dammage"].keys()),
                    list(self.attack_data["Soleil_cruel"]
                         ["energy_cost"].keys())
                )
                self.attacks_dict["Soleil_cruel"] = instance
            else:
                instance = Attack(
                    attack,
                    self.attack_data[attack]["description"],
                    self.attack_data[attack]["dammage"],
                    self.attack_data[attack]["energy_cost"]
                )
                self.attacks_dict[attack] = instance
        print(self.attacks_dict)

    def remove_hp(self, value):
        """ Allows to remove hp from a pokemon """
        self.current_hp = self.current_hp - value
        if self.current_hp <= 0:
            self.is_dead()
            print(f"{self.name} a succombé à ses blessures... R.I.P")
        else:
            Partie_01.round_instance.a_pokemon_has_no_full_hp = True  # type: ignore

    def add_hp(self, value):
        """ Allows to add hp to a pokemon """
        self.current_hp = self.current_hp + value
        if self.current_hp > self.initial_hp:
            self.current_hp = self.initial_hp
            print(
                f"""
                {self.name} a récupéré {value} hp et a maintenant {self.current_hp} hp.
                """
            )
            return
        else:
            print(
                f"{self.name} a récupéré {value} hp et a maintenant {self.current_hp} hp.")

    def check_pv(self):
        """ Allows to check the hp of a player and die """

        if self.current_hp == 0:
            self.is_dead()
        elif self.current_hp == self.initial_hp:
            print(f"{self.name} n'a pas perdu d'hp")
        else:
            print(
                f"{self.name} a {self.current_hp} restant{'s' if self.current_hp > 1 else ''}")
            Partie_01.round_instance.a_pokemon_has_no_full_hp = True  # type: ignore

    def check_malus(self):
        """ Allows to check if the pokemon has to get a malus when he's initialized """
        if "Malus" in pokemons_data["pokemons"][self.name]:
            self.his_malus = pokemons_data["pokemons"][self.name]["Malus"]["name"]
            if self.his_malus == "branlette":
                # dcp ici je dois donc initialiser chaque effet des malus, les pokémons
                # doivent être initialisé au début d'une classe appellée manche
                print()
            elif self.his_malus == "paralyse":
                print()
            else:
                print("Error 404")
        else:
            self.his_malus = None
        return self.his_malus

    def check_bonus(self):
        """ Allows to check if the pokemon has to get a bonus when he's initialized """

    def __str__(self):
        if self.name == "leSpire":
            return """
        Je parie que tu ne sais pas dire : J'ai vu six sots suçant six-cent six saucisses ! 
    """
        elif self.name == "Robin":
            return """
            Bae t'as les crampter ?"""
        elif self.name == "Louis":
            return """ Faut comprendre que je vais vous niquer... """
        elif self.name == "Chantal":
            return """ Je me suis bien garé cette fois ! """
        elif self.name == "Escanor":
            return """
            J'ai une mauvaise nouvelle pour vous, voulais vous la connaître ?
            Le Soleil est au Zénith...
            """
        else:
            return "Bah c'est pas bon je vais te faire une potion"


class Potion:
    """ 
    La classe Potion est une classe regroupant les caractéristiques
    des différentes potions données aléatoi rement aux joueurs.
    """

    def __init__(self, name: str, gain: int, dmg: int, target=None):
        self.name: str = name
        self.gain: int = gain
        self.dmg: int = dmg
        self.target = target


class Attack:
    """ Represent a Pokemon's Attack """

    def __init__(self, name, description, dammage, energy_cost, energy_cost_range=None,
                 energy_gain: int = 0, hp_gain: int = 0, probability: float = 1.0000):
        self.name = name
        self.dammage = dammage
        self.energy_cost = energy_cost
        self.description = description
        self.energy_cost_range = energy_cost_range
        self.energy_gain = energy_gain
        self.hp_gain = hp_gain
        self.probability = probability


def reinitialize_json():
    ''' Reinitialize the pokemons_name list '''

    with open('pokemon_data.json', 'r', encoding='utf-8') as json_file_:  # pylint: disable=<W0621
        pokemons_data_ = json.load(json_file_)
    pokemons_data_["initial_names"] = ["leSpire",
"Louis", "Ikil_Ikon", "Chantal", "Robin", "Escanor", "Squeezie", "Sponsorisateur", "Sardoche"]
    pokemons_data_["names"] = pokemons_data['initial_names']
    with open('pokemon_data.json', 'w', encoding='utf-8') as json_file_:
        json.dump(pokemons_data_, json_file_)


def gestionnaire_exceptions(type_exc, valeur, traceback):
    ''' recovery function (for the JSON file and the pokemon_name list) '''

    # Appeler la fonction de réinitialisation du fichier JSON
    reinitialize_json()

    # Reraise l'exception pour obtenir le comportement par défaut
    sys.__excepthook__(type_exc, valeur, traceback)


sys.excepthook = gestionnaire_exceptions
atexit.register(reinitialize_json)


Partie_01 = Game()
