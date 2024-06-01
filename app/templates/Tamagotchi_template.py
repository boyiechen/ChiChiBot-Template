from random import randrange

class Pet(object):
    """
    A virtual pet
    """
    excitement_reduce = 3
    excitement_max = 10
    excitement_warning = 3
    food_reduce = 2
    food_max = 10
    food_warning = 3
    vocab = ['"Grrr..."', '"Hi"']

    def __init__(self, name, animal_type):
        self.name = name
        self.animal_type = animal_type
        self.food = randrange(self.food_max)
        self.excitement = randrange(self.excitement_max)
        self.vocab = self.vocab[:]

    def __clock_tick(self):
        self.excitement -= 1
        self.food -= 1

    def mood(self):
        if self.food > self.food_warning and self.excitement > self.excitement_warning:
            return "happy"
        elif self.food < self.food_warning:
            return "hungry"
        else:
            return "bored"

    def __str__(self):
        return "\nI'm " + self.name + "." + "\nI feel " + self.mood() + "."

    def teach(self, word):
        self.vocab.append(word)
        self.__clock_tick()

    def talk(self):
        print("I am a ", self.animal_type, " named ", self.name, ".", " I feel ", self.mood(), "now.\n")
        print(self.vocab[randrange(0, len(self.vocab))])

        self.__clock_tick()

    def feed(self):
        print("***crunch*** \n mmm. Thank you!")
        meal = randrange(0, self.food_max)
        self.food += meal

        if self.food < 0:
            self.food = 0
            print("I am still hungry!")

        elif self.food > self.food_max:
            self.food = self.food_max
            print("I am full!")
            
    def play(self):
        print("Whoohoo!")
        fun = randrange(self.excitement, self.excitement_max)
        self.excitement += fun
        if self.excitement < 0:
            self.excitement = 0
            print("I am bored")
        elif self.excitement >= self.excitement_max:
            self.excitement = self.excitement_max
            print("I am happy!")

        self.__clock_tick()

def main():
    pet_name = input("What do you want to name your pet?\n")
    pet_type = input("What type of animal is your pet?\n")

    # Create a new pet
    my_pet = Pet(pet_name, pet_type)

    input("Hello! I am " + pet_name + " and I am new here!" + "\nPress enter to start. \n")

    choice = None

    while choice != "0":
        print(
        """
        *** INTERACTION WITH YOUR PET ***

        1 - Feed your pet
        2 - Talk with your pet
        3 - Teach your pet a new word
        4 - Play with your pet
        0 - Quit
        """)

        choice = input()

        if choice == "0":
            print("Goodbye!")
        elif choice == "1":
            my_pet.feed()
        elif choice == "2":
            my_pet.talk()
        elif choice == "3":
            new_word = input("What do you want to teach your pet to say?\n")
            my_pet.teach(new_word)
        elif choice == "4":
            my_pet.play() 
        else:
            print("Sorry, that isn't a valid option")

    
        
if __name__ == "__main__":
    main()
