import tkinter as tk
from random import shuffle


class ButtonGrid(tk.Frame):
    def __init__(self, master, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.data = data
        self.buttons = []
        self.pressed_buttons = []  # List to store names of pressed buttons

        self.create_buttons()

    def create_buttons(self):
        # Shuffle the data values
        shuffled_data = []
        for key in self.data:
            shuffled_data.extend(self.data[key])
        shuffle(shuffled_data)

        # Create buttons and place them in a grid
        for i in range(4):
            for j in range(4):
                name = shuffled_data[i * 4 + j]
                bg_color = "white" if name not in self.pressed_buttons else "dark grey"
                btn = tk.Button(self, text=name, bg=bg_color, command=lambda n=name: self.toggle_button(n))
                btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.buttons.append((name, btn))

        # Configure grid to equally distribute space for each button
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

    def toggle_button(self, name):
        # Check if there are already 4 pressed buttons
        if len(self.pressed_buttons) >= 4 and name not in self.pressed_buttons:
            return

        for btn_name, btn in self.buttons:
            if btn_name == name:
                if btn["bg"] == "white":
                    btn["bg"] = "dark grey"
                    self.pressed_buttons.append(name)
                else:
                    btn["bg"] = "white"
                    self.pressed_buttons.remove(name)

        # Update the state of the SUBMIT button
        self.master.update_submit_button_state()

    def shuffle_buttons(self):
        for btn_name, btn in self.buttons:
            btn.destroy()  # Destroy the current buttons
        self.buttons.clear()  # Clear the buttons list
        self.create_buttons()  # Recreate and shuffle the buttons


class App(tk.Tk):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Button Grid")

        self.data = data

        self.button_grid = ButtonGrid(self, data)
        self.button_grid.pack()

        self.submit_button = tk.Button(self, text="SUBMIT", command=self.check_solution, state=tk.DISABLED)
        self.submit_button.pack()

        self.shuffle_button = tk.Button(self, text="SHUFFLE", command=self.shuffle_button_grid)
        self.shuffle_button.pack()

    def update_submit_button_state(self):
        if len(self.button_grid.pressed_buttons) == 4:
            self.submit_button.config(state=tk.NORMAL)
        else:
            self.submit_button.config(state=tk.DISABLED)

    def shuffle_button_grid(self):
        self.button_grid.shuffle_buttons()

    def check_solution(self):
        pressed_buttons = set(self.button_grid.pressed_buttons)
        for key, value in self.data.items():
            if set(value) == pressed_buttons:
                print("Match")
                return
            elif len(set(value).intersection(pressed_buttons)) == 3:
                print("Off by 1")
                return
        print("No match")


def main():
    # Dictionary to initialize the grid
    data = {
        "A": ["Apple", "Ant", "Axe", "Anchor"],
        "B": ["Banana", "Ball", "Bat", "Butterfly"],
        "C": ["Cat", "Car", "Cake", "Candle"],
        "D": ["Dog", "Duck", "Diamond", "Door"]
    }

    app = App(data)
    app.mainloop()


if __name__ == "__main__":
    main()
