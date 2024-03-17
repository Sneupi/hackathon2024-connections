import tkinter as tk
import random
from itertools import cycle
import numpy as np
import csv
from customtkinter import *


class GameButton(tk.Button):
    def __init__(self, master, row, col, name, color='#242424', disabled=False):
        super().__init__(master, text=name, command=self.toggle_color, width=15, height=6, fg='white',
                         font=('Arial', 20), activebackground=color, activeforeground='white')
        self.row = row
        self.col = col
        self.name = name
        self.color = color
        self.disabled = disabled
        self.update_state()

    def toggle_color(self):
        if self.disabled:
            return
        if self.color == '#242424' and self.master.count_dark_gray_buttons() < 4:
            self.color = '#484848'
        else:
            self.color = '#242424'
        self.update_state()

    def mark_solved(self, color='light green'):
        self.disabled = True
        self.color = color
        self.update_state()

    def update_state(self):
        self.config(bg=self.color)
        self.config(state=tk.DISABLED if self.disabled else tk.NORMAL)


class ButtonGrid(tk.Frame):
    def __init__(self, master, grid_data):
        super().__init__(master)
        self.grid_data = grid_data
        self.buttons = []
        self.disabled_buttons = set()
        self.dark_gray_buttons = set()
        self.selected_buttons = set()
        self.mistakes_left = 4
        self.init_grid()
        self.solved_colors = cycle(['light green', 'light blue', 'pink', 'light goldenrod'])
        self.configure(bg='#242424')

        self.mistakes_label = tk.Label(self, text=f"Mistakes left: {self.mistakes_left}")
        self.mistakes_label.grid(row=0, column=0, columnspan=4)
        self.mistakes_label.config(bg='#242424', fg='white', font=('Arial', 20))
        self.message_label = tk.Label(self)
        self.message_label.grid(row=1, column=0, columnspan=4)
        self.message_label.config(bg='#242424', fg='white', font=('Arial', 20))

        self.shuffle_grid()

    def init_grid(self):
        for i, row_key in enumerate(self.grid_data.keys()):
            for j, col_key in enumerate(self.grid_data[row_key]):
                button = GameButton(self, i + 2, j, col_key)
                self.buttons.append(button)
                button.grid(row=i + 2, column=j, padx=2, pady=2)

    def count_dark_gray_buttons(self):
        count = sum(1 for button in self.buttons if button.color == '#484848')
        return count

    def shuffle_grid(self):
        unsolved_buttons = [button for button in self.buttons if not button.disabled]
        random.shuffle(unsolved_buttons)
        self.buttons = [button for button in self.buttons if button.disabled] + unsolved_buttons
        self.update_grid_state()

    def update_grid_state(self):
        for i, button in enumerate(self.buttons):
            button.row = i // 4
            button.col = i % 4
            button.grid(row=button.row + 2, column=button.col)

    def disable_button(self, button):
        button.disabled = True
        self.disabled_buttons.add(button)

    def enable_button(self, button):
        button.disabled = False
        if button in self.disabled_buttons:
            self.disabled_buttons.remove(button)

    def set_dark_gray_button(self, button):
        button.color = '#484848'
        self.dark_gray_buttons.add(button)

    def clear_dark_gray_buttons(self):
        for button in self.dark_gray_buttons:
            button.color = '#242424'
        self.dark_gray_buttons.clear()
        self.update_grid_state()

    def check_match(self, selected_buttons):
        # get the names of the 4 selected buttons
        selected_names = [button.name for button in selected_buttons]

        found = bool(False)

        # check for matches or one away
        for category, names in self.grid_data.items():

            # check if all 4 selected buttons are of same category
            if set(names) == set(selected_names):

                # Mark selected buttons as solved and move them to the top of the buttons list
                solved_color = next(self.solved_colors)
                for button in selected_buttons:
                    button.mark_solved(solved_color)
                    self.buttons.remove(button)
                    self.buttons.insert(0, button)

                # print category solved
                self.message_label.config(text=f"Solved Category \"{category}\"")
                # Update grid state
                self.update_grid_state()
                found = True
                break

            # check if only 3 of the 4 selected buttons are of same category
            # if yes, update the message label and break the loop
            elif len(set(names).intersection(set(selected_names))) == 3:
                self.message_label.config(text="One Away...")
                break

        return found

    def check_game_over(self):

        if self.mistakes_left <= 0:

            # print losing message
            self.message_label.config(text=f"Game Over: You lost!\nCategories: {list(self.grid_data.keys())}")
            # Solve the remaining sets of unsolved buttons
            for category, names in self.grid_data.items():

                unsolved_buttons = [button for button in self.buttons if button.name in names and not button.disabled]

                if unsolved_buttons:
                    solved_color = next(self.solved_colors)  # Use a different color for each unsolved category
                    for button in unsolved_buttons:
                        button.mark_solved(solved_color)
                        self.buttons.remove(button)
                        self.buttons.append(button)  # Add unsolved buttons to the end of the list

            self.update_grid_state()

        elif all(button.disabled for button in self.buttons):

            # print winning message
            self.message_label.config(text=f"Congratulations! You won!\nCategories: {list(self.grid_data.keys())}")

    def submit(self):
        # if all buttons are disabled (i.e. all buttons have been solved), return
        if all(button.disabled for button in self.buttons):
            return

        # get selected buttons in the grid
        selected_buttons = [button for button in self.buttons if button.color == '#484848']

        # Check if exactly 4 buttons are selected
        if len(selected_buttons) == 4:

            # Clear the message label of any previous messages
            self.message_label.config(text="")

            # if neither a full match nor a one away are made, reduce mistakes left by 1 and update the mistakes label
            if self.check_match(selected_buttons) is False:
                self.mistakes_left -= 1
                print("Selected buttons are not part of the same category.")
                self.mistakes_label.config(text=f"Mistakes left: {self.mistakes_left}")

        else:
            print("Please select exactly 4 buttons.")
            return

        # check for game over or game won conditions
        self.check_game_over()

    def load_new_data(self, new_filepath):
        # Clear existing buttons from the grid
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

        # Retrieve new data
        new_data = read_csv_file(new_filepath)  # Change new_filepath to the path of the new CSV file

        # Set new data to grid_data
        self.grid_data = new_data

        # Initialize the grid again with the new data
        self.init_grid()

        # Reset any other necessary variables or labels
        self.mistakes_left = 4
        self.mistakes_label.config(text=f"Mistakes left: {self.mistakes_left}")
        self.message_label.config(text="")

        # Return if further processing is not needed
        if not new_data:
            return

        self.shuffle_grid()


def read_csv_file(filepath):
    category_mapping = {}  # Initialize an empty dictionary to store category to list of words mapping

    if filepath:
        # Read the CSV file
        with open(filepath, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Check if the row is empty or has less than 2 elements
                if not row or len(row) < 2:
                    continue

                # Extract category and words
                category = row[0]
                words = row[1:]

                # Check if category already exists in the dictionary
                if category in category_mapping:
                    # Append the words to the existing list of words
                    category_mapping[category].extend(words)
                else:
                    # Create a new list with the words for the category
                    category_mapping[category] = words

    # Select 4 random categories and create a new mapping with them
    random_categories = np.random.choice(list(category_mapping.keys()), size=4, replace=False)
    new_category_mapping = {str(category): category_mapping[category] for category in random_categories}
    print(new_category_mapping)

    return new_category_mapping


def main():
    root = CTk()
    root.title("Button Grid")
    grid_data = read_csv_file('Objects.csv')
    set_appearance_mode("dark")

    button_grid = ButtonGrid(root, grid_data)
    button_grid.pack(side=tk.RIGHT, padx=10, pady=10)

    animal = CTkButton(root, text="Animals", command=lambda: button_grid.load_new_data("Animals.csv"),
                       fg_color="transparent", hover_color='#8B0000', border_width=2, border_color='#8B0000')
    animal.pack(side=tk.TOP, pady=10)

    entertainment = CTkButton(root, text="Entertainment",
                              command=lambda: button_grid.load_new_data("Entertainment.csv"),
                              fg_color="transparent", hover_color='#006400', border_width=2, border_color='#006400')
    entertainment.pack(side=tk.TOP, pady=10)

    food = CTkButton(root, text="Food", command=lambda: button_grid.load_new_data("Food.csv"),
                     fg_color="transparent", hover_color='#0000FF', border_width=2, border_color='#0000FF')
    food.pack(side=tk.TOP, pady=10)

    objects = CTkButton(root, text="Objects", command=lambda: button_grid.load_new_data("Objects.csv"),
                        fg_color="transparent", hover_color='#DAA520', border_width=2, border_color='#DAA520')
    objects.pack(side=tk.TOP, pady=10)

    shuffle_button = CTkButton(root, text="Shuffle", command=button_grid.shuffle_grid,
                               fg_color="transparent", hover_color='#800080', border_width=2, border_color='#800080')
    shuffle_button.pack(side=tk.LEFT, padx=5, pady=5)

    mark_solved_button = CTkButton(root, text="Submit", command=button_grid.submit,
                                   fg_color="transparent", hover_color='#26B170', border_width=2,
                                   border_color='#26B170')
    mark_solved_button.pack(side=tk.LEFT, padx=5, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
