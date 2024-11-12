from matplotlib import pyplot as plt
import numpy as np
import time
import tkinter as tk
import random
import seaborn as sns

# import version6
def load_word_list(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]
# Initialize the state for tracking the current row and column
current_row = 0
current_col = 0
max_rows = 6
max_cols = 5
ga_result =''
fitness=0
Generation=0
GUESS_LIST = load_word_list('guesses-list.txt')
ANSWER_LIST = load_word_list('answers-list.txt')
TARGET_WORD = random.choice(ANSWER_LIST)
print(TARGET_WORD)
GREEN = "#6aaa64"   # Correct letter in the correct position
YELLOW = "#c9b458"  # Correct letter but in the wrong position
GRAY = "#787c7e"    # Letter not in word
# Function to handle button clicks
User_word = ''  # Global variable to store the constructed word
word_feed_back=''
game_over = False
attemps = 1
final_word =''
def disable_grid():
    """Disable all labels in the grid to prevent further input."""
    for i in range(max_rows):
        for j in range(max_cols):
            guess_labels[i][j].config(state="disabled")

    for button in keyboard_buttons:
        button.config(state="disabled")   

def provide_feedback(guess):
    feedback_colors = []
    for i in range(len(TARGET_WORD)):
        if guess[i] == TARGET_WORD[i]:
            feedback_colors.append(GREEN)  # Correct position (green)
        elif guess[i] in TARGET_WORD:
            feedback_colors.append(YELLOW)  # Wrong position (yellow)
        else:
            feedback_colors.append(GRAY)    # Not in word (gray)
    return feedback_colors
# def provide_feedback(guess):
#     feedback = ""
#     for i in range(len(TARGET_WORD)):
#         if guess[i] == TARGET_WORD[i]:
#             feedback += f"{GREEN}{guess[i]}{RESET}"  # Correct position (green)
#         elif guess[i] in TARGET_WORD:
#             feedback += f"{YELLOW}{guess[i]}{RESET}"  # Wrong position (yellow)
#         else:
#             feedback += guess[i]  # Not in word (no color)
#     return feedback
def on_letter_click(letter):
    global User_word, current_row, current_col,word_feed_back,game_over,attemps,final_word
    if game_over:
        message_label.config(text=f"Game over! The word was: {TARGET_WORD}")
        return
 
    # Handle letter input (only allow letters)
    if letter.isalpha() and current_col < max_cols:
        # Place the letter in the current position in the grid
        if letter != "Enter" and letter != "Delete":
            User_word += letter.lower()
            final_word = User_word
            # print(f'word: {User_word}')  # Print the current constructed word
            guess_labels[current_row][current_col].config(text=letter)
            current_col += 1  # Move to the next column
    # 
    # Handle "Delete" button. 
    if letter == "Delete" and current_col > 0:
        current_col -= 1  # Move back one column
        guess_labels[current_row][current_col].config(text="")  # Clear the letter
        User_word = User_word[:-1]  # Remove the last character from User_word
   

    # Handle "Enter" button
    if letter == "Enter" and current_col == max_cols and User_word in ANSWER_LIST:
        
        # Only move to the next row if all columns are filled
        word_feed_back = provide_feedback(User_word)
        # print(provide_feedback(User_word))
        for i, color in enumerate(word_feed_back):
            guess_labels[current_row][i].config(bg=color)
        if User_word == TARGET_WORD:
            message_label.config(text=f"You got it: {User_word}\nGA guess was: {ga_result}\nfitness: {fitness}\ngen:{Generation}")
            disable_grid()
            game_over=False
            return 
        else:
            message_label.config(text="Incorrect guess. Try again!")
            attemps+=1
            # print(f'Final word: {User_word == TARGET_WORD}')  # Print the full constructed word
            if current_row < max_rows - 1:
                current_row += 1
                current_col = 0  # Reset to the first column in the new row
        User_word = ''  # Reset User_word after processing the row
        if current_row == current_col and not game_over:
            message_label.config(text=f"Game over!\nThe word was: {TARGET_WORD}\nYour guess was: {final_word}\nGA guess was: {ga_result}\nfitness: {fitness}\ngen:{Generation}")
            # message_label.config(text=f"Your guess was: {User_word}")
            # message_label.config(text=f"GA guess was: (Placeholder)")
            disable_grid()
            game_over=True
            return 
# =====================================================
def calculate_fitness(guess):
    fitness = 0
    for i in range(len(TARGET_WORD)):
        if guess[i] == TARGET_WORD[i]:  # Correct position (green)
            fitness += 2
        elif guess[i] in TARGET_WORD:   # Incorrect position (yellow)
            fitness += 1
    return fitness

# Initialize population with guesses from GUESS_LIST
def initialize_population(size):
    return [random.choice(GUESS_LIST) for _ in range(size)]

# GA Selection, Crossover, and Mutation
def select_parents(population, fitness_scores):
    # Selects 2 parents via probability
    # Higher probability (fitness) --> more likely to be selected
    return random.choices(population, weights=fitness_scores, k=2)

def crossover(parent1, parent2):
    child = ""
    for i in range(len(parent1)):
        # random.random() returns a value in the range [0, 1)
        child += parent1[i] if random.random() < 0.5 else parent2[i]
    return child


def mutate(word, mutation_rate=0.1):
    word_as_list = list(word)
    for i in range(len(word_as_list)):
        if random.random() < mutation_rate:
            word_as_list[i] = random.choice("abcdefghijklmnopqrstuvwxyz")
    return ''.join(word_as_list)

# Genetic Algorithm function
def genetic_algorithm(population_size=20, generations=200, mutation_rate=0.1):
    population = initialize_population(population_size)
    for generation in range(generations):
        fitness_scores = [calculate_fitness(word) for word in population]

        # Check if target word has been found
        if TARGET_WORD in population:
            # print(f"GA found the target word in generation {generation}!")
            return TARGET_WORD,generation

        # Selection and reproduction
        new_population = []
        for _ in range(population_size // 2):
            parent1, parent2 = select_parents(population, fitness_scores)
            child1 = crossover(parent1, parent2)
            child1 = mutate(child1, mutation_rate)

            child2 = crossover(parent2, parent1)
            child2 = mutate(child2, mutation_rate)
            new_population.extend([child1, child2])

        # Update population and output best guess
        population = new_population
        best_guess = max(population, key=calculate_fitness)
        best_fitness = calculate_fitness(best_guess)
    return best_guess,generation



# ===================================
# Create the main Tkinter window
root = tk.Tk()
root.title("GA Wordle Game")

root.configure(bg="white")

# Main frame to center all widgets
main_frame = tk.Frame(root, bg="white")
main_frame.grid(sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
message_label = tk.Label(main_frame, text="Welcome to GA Wordle Game!", font=("Helvetica", 16), bg="white")
message_label.pack(pady=10)
# Set up the display area for guesses inside the main frame
guess_frame = tk.Frame(main_frame, bg="white")
guess_frame.pack(pady=20)

guess_labels = []
for i in range(max_rows):  # Wordle typically has 6 guesses
    row = []
    for j in range(max_cols):  # Each word has 5 letters
        label = tk.Label(guess_frame, text=word_feed_back, font=("Helvetica", 24), width=2, height=1,
                         borderwidth=1, relief="solid", bg="#f0f0f0")
        label.grid(row=i, column=j, padx=5, pady=5)
        row.append(label)
    guess_labels.append(row)

# Define the keyboard layout including Enter and Delete keys
keyboard_rows = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
    ['Delete', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Enter']
]

# Keyboard button colors
button_bg = "#d3d6da"
button_fg = "black"

# Keyboard frame to organize buttons
keyboard_frame = tk.Frame(main_frame, bg="white")
keyboard_frame.pack(pady=10)

# Create buttons for each letter and special keys in the keyboard layout
keyboard_buttons = []

for row_index, row in enumerate(keyboard_rows):
    key_row_frame = tk.Frame(keyboard_frame, bg="white")
    key_row_frame.pack()
    for col_index, key in enumerate(row):
        # Adjust button width for "Enter" and "Delete" keys
        if key == "Enter" or key == "Delete":
            width = 6
        else:
            width = 4
        button = tk.Button(key_row_frame, text=key, font=("Helvetica", 12), width=width, height=2,
                           bg=button_bg, fg=button_fg, activebackground=button_bg,
                           command=lambda k=key: on_letter_click(k))
        button.pack(side="left", padx=3, pady=3)
        keyboard_buttons.append(button)  # Store the button reference


# Center the main frame
main_frame.pack(expand=True)
def play_wordle_with_ga():
    global ga_result,fitness,Generation
    print("GA is starting...")
    ga_result,Generation = genetic_algorithm()
    print(ga_result)
    fitness = calculate_fitness(ga_result)

    return ga_result, fitness
# Run the Tkinter main loop
play_wordle_with_ga()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def reload_game():
    global current_row, current_col, User_word, word_feed_back, game_over, attemps, final_word, TARGET_WORD, ga_result, fitness, Generation
    current_row = 0
    current_col = 0
    User_word = ''
    word_feed_back = ''
    game_over = False
    attemps = 1
    final_word = ''
    TARGET_WORD = random.choice(ANSWER_LIST)  # Choose a new target word
    ga_result, fitness, Generation = '', 0, 0

    # Clear the grid
    for i in range(max_rows):
        for j in range(max_cols):
            guess_labels[i][j].config(text="", bg="#f0f0f0", state="normal")

    # Enable keyboard buttons
    for button in keyboard_buttons:
        button.config(state="normal")

    message_label.config(text="New game started! Try to guess the word.")
    play_wordle_with_ga()  # Start the GA for the new target word

# Add the Reload button to the main frame
reload_button = tk.Button(main_frame, text="Reload", font=("Helvetica", 12), width=10, command=reload_game)
reload_button.pack(pady=10)
root.mainloop()

