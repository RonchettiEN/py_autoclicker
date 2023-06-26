import os
import csv
from pathlib import Path
import pyautogui
from pynput import mouse

FOLDER_NAME = "profiles"


def check_profiles_folder():
    Path(FOLDER_NAME).mkdir(exist_ok=True)


def read_profiles_folder():
    profiles_data = []

    if os.path.exists(FOLDER_NAME) and os.path.isdir(FOLDER_NAME):
        file_list = [file for file in os.listdir(FOLDER_NAME) if file.endswith(".csv")]

        for file_name in file_list:
            file_path = os.path.join(FOLDER_NAME, file_name)
            with open(file_path, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                instructions = list(csv_reader)

            # Remove the ".csv" extension from the file name
            name = os.path.splitext(file_name)[0]

            profile = {"name": name, "instructions": instructions}
            profiles_data.append(profile)

    return profiles_data


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_menu():
    clear_screen()
    print("Menu:")
    print("1) Execute profile")
    print("2) Make profile")


def execute_profile():
    clear_screen()
    profiles = read_profiles_folder()

    if not profiles:
        print("No profiles found.")
        return

    print("Available profiles:")
    for index, profile in enumerate(profiles, start=1):
        print(f"{index}) {profile['name']}")

    selection = input("Enter the profile number to execute: ")

    try:
        profile_index = int(selection) - 1
        selected_profile = profiles[profile_index]
        execute_instructions(selected_profile["instructions"], selected_profile["name"])
    except (ValueError, IndexError):
        print("Invalid profile number.")


def execute_instructions(instructions, profile_name):
    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.right:
            return False  # Stop capturing events

    listener = mouse.Listener(on_click=on_click)
    listener.start()

    clear_screen()
    print(f"Executing profile '{profile_name}'... Press right-click to stop.")

    while True:
        for instruction in instructions:
            if len(instruction) == 4:
                x, y, wait_time, repeat = map(int, instruction)
                for _ in range(repeat):
                    pyautogui.click(x=x, y=y)
                    if wait_time == -1:
                        pyautogui.sleep(0.001)
                    else:
                        pyautogui.sleep(wait_time / 1000)
            else:
                print(f"Comment: {''.join(instruction)}")

            if not listener.is_alive():
                return


def make_profile():
    clear_screen()
    print("Making profile...")

    initial_comment = input("Enter an initial comment: ")

    coordinates = [initial_comment]
    capture_events = True  # Variable de control para la captura de eventos

    def on_click(x, y, button, pressed):
        nonlocal capture_events  # Hacer referencia a la variable de control externa

        if pressed and button == mouse.Button.left:
            if capture_events:
                coordinates.append((x, y))
                print(f"Recorded coordinates: ({x}, {y})")

        if pressed and button == mouse.Button.right:
            capture_events = False  # Detener la captura de eventos
            comment = input("Enter a comment: ")
            coordinates.append(comment)
            print("Comment added.")
            capture_events = True  # Detener la captura de eventos

        if pressed and button == mouse.Button.middle:
            return False  # Detener la captura de eventos

    with mouse.Listener(on_click=on_click) as listener:
        print("Making profile (click to record coordinates):")
        print("Press right button to add a comment.")
        listener.join()

    save_profile(coordinates)


def save_profile(coordinates):
    folder_name = FOLDER_NAME
    Path(folder_name).mkdir(exist_ok=True)

    profile_name = input("Enter profile name: ")
    file_name = profile_name + ".csv"
    file_path = os.path.join(folder_name, file_name)

    with open(file_path, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        for coord in coordinates:
            if len(coord) == 2:  # Verificar si coord tiene 2 elementos (x, y)
                csv_writer.writerow([coord[0], coord[1], 1000, 1])
            else:
                csv_writer.writerow(coord)

    print(f"Profile '{profile_name}' saved successfully.")


check_profiles_folder()

while True:
    show_menu()
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        execute_profile()
    elif choice == "2":
        make_profile()
    else:
        clear_screen()
        print("Invalid choice. Please try again.")
