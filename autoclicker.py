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
    print("Executing profile...")
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

    print(f"Executing profile '{profile_name}'... Press right-click to stop.")

    while True:
        for instruction in instructions:
            x, y, wait_time, repeat = map(int, instruction)
            for _ in range(repeat):
                pyautogui.click(x=x, y=y)
                pyautogui.sleep(0.001)

            if not listener.is_alive():
                return


def make_profile():
    clear_screen()
    print("Making profile...")

    coordinates = []

    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            coordinates.append((x, y))
            print(f"Recorded coordinates: ({x}, {y})")

        if pressed and button == mouse.Button.right:
            return False  # Stop capturing events

    with mouse.Listener(on_click=on_click) as listener:
        print("Making profile (click to record coordinates):")
        print("Press right button to finish.")
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
        for x, y in coordinates:
            csv_writer.writerow([x, y, 1000, 1])

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
