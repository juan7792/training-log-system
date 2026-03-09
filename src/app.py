from tabulate import tabulate
from more_itertools import locate
import matplotlib.pyplot as plt
import math
import numpy as np
import datetime
import database

menu_1 = """Please choose your option:
1) Add user
2) Select user
3) Exit

Your option: """

menu_2 = """Please choose your option:
1) Add exercise
2) Add training
3) View training
4) View training volume
5) View muscle groups and exercises
6) Exit

Your option: """

initial_message = "Welcome to your training log book."
print(initial_message)

# CREATE TABLES BEFORE ENTERING LOOP
database.create_tables()


# FUNCTIONS FOR THE FIRST MENU
# MAIN FUNCTIONS
# insert new user to database
def insert_user():
    username_to_create = input("Write your username: ")
    database.add_user(username_to_create)
    print(f"Great! User created: {username_to_create}\n")


# select user from database
def select_user():
    # get lists from cursor
    users = database.get_all_users()

    # in case no user has been created, go to first menu
    while not users:
        print("No existing user! Add one user before proceeding!")
        return

    # if table users has entries
    return ask_user_id()


# FUNCTIONS TO BE CALLED BY MAIN FUNCTIONS
# check that input is a number
def ask_user_id():
    # get lists from cursor
    users = database.get_all_users()

    # decompose list to get id and name of each element and then print them
    for _id, name in users:
        print(f"{_id}) {name}")

    # check that the input is not letters and it is within the numbers of users
    message_select_user = "Select user to add exercise to (only ID number please): "
    return check_id(message_select_user, users)


# check id input from user to confirm it is within list options
def check_id(message, dummy):
    while select_id := input(message):
        try:
            try:
                int(select_id)
                dummy[int(select_id) - 1][0]
                return select_id
            except ValueError:
                print(f"Error: Please select only an ID number within the list!")
        except IndexError:
            print("Error: Please select only an ID number within the list!")


# FIRST MENU
while (user_option_1 := input(menu_1)) != "3":
    if user_option_1 == "1":
        insert_user()
    elif user_option_1 == "2":
        user_id = select_user()
        username = database.get_specific_user(user_id)
        print(f"\nWelcome {username[0][0]}!\n")
        break
    else:
        print("Error: invalid option selected. Select a valid option, becerra!\n")


# FUNCTIONS SECOND MENU
# MAIN FUNCTIONS
# insert exercise to user
def insert_exercise(user_id):
    # input exercise or go back to menu
    exercise_name = input("Enter exercise name or enter 'q' to go back to menu: ")
    if exercise_name == "q":
        return

    # input training type or go back to menu
    training_type = input("Enter training type (e.g. Push, Pull, Legs) or enter 'q' to go back to menu: ")
    if training_type == "q":
        return

    # commit transaction
    database.add_exercise(user_id, exercise_name, training_type)

    # print confirmation message
    username = database.get_specific_user(user_id)
    print(f"Great! Exercise created: {exercise_name} (User: {username[0][0]})\n")


# insert new training into logbook
def insert_training(user_id):
    # while loop used to continue looping in the exercise selection if user decides to add a new exercise in this module
    while (exercise_id := ask_exercise_id(user_id)) is None:
        pass

    # exit insert_training() if selected
    if exercise_id == True:
        return

    # enter date in dd-mm-YYYY format and check date
    training_added_date = ask_date()

    # parse date
    timestamp_training_added_date = parse_date_into_timestamp(training_added_date)

    # enter valid number of sets
    message_sets = "Enter the number of sets you did: "
    sets_training = check_positive_input(message_sets)

    # enter reps and only allow valid input using number of sets as parameter
    message_reps = "Enter number of reps per set separated by '-' (e.g. 3 sets of 5 reps: 5-5-5): "
    reps_training = check_reps_or_intensity(sets_training, message_reps)

    # enter the intensity per rep and only allow valid input using number of sets as parameter
    message_intensity = "Enter weight lifted per set separated by '-' in kg (e.g. 3 sets with 40kg: 40-40-40): "
    intensity_training = check_reps_or_intensity(sets_training, message_intensity)

    # enter workout type - body building, powerlifting, functional, etc.
    workout_type = input("Enter the workout type (e.g. body building, powerlifting): ")

    # enter body weight
    message_body_weight = "Enter your current body weight in kg: "
    body_weight = check_positive_input(message_body_weight)

    # enter observations
    observations = input("Enter your observations: ")

    # commit transaction
    database.add_training(user_id, exercise_id, timestamp_training_added_date, int(sets_training), reps_training,
                          intensity_training, workout_type, body_weight, observations)

    print(f"Great! Your exercise has been added to your training log on the {training_added_date}!\n")


# retrieve and view training logs
def view_training(user_id):
    global dummy_trainings

    # options menu in function
    message_view_trainings = """1) View training history
2) View desired training date
3) View desired training period
4) Return to menu
Choose what would you like to view: """

    # use function to select date and retrieve cursor with trainings
    dummy_trainings = select_view_option(user_id, message_view_trainings, selection="training", muscle_group= None)

    # return if user selected that option
    if dummy_trainings is None:
        print("\n--- Returning to menu ---\n")
        return

    # show message if no training was found in the selected date and return
    if not dummy_trainings:
        print("\nNo training on this date or invalid date period!\n")
        return

    # convert tuples to list
    trainings = [list(training) for training in dummy_trainings]

    # convert timestamps to dates
    for i in range(len(trainings)):
        trainings[i][0] = parse_input_timestamp_to_date(trainings[i][0])

    # print table with trainings
    header_trainings = ("Date", "Muscle group", "Exercise", "Sets", "Reps", "Intensity [kg]", "Discipline",
                        "Body weight [kg]", "Observations")
    print(f"\n{tabulate(trainings, headers=header_trainings)}\n")

    input("Enter any key to continue: ")


# retrieve training logs, calculate training volume and present it
def view_training_volume(user_id):
    # print options
    global dummy_trainings

    # string with selected muscle group
    selected_muscle_group = select_muscle_group(user_id)

    # options menu in function
    message_training_volume = """1) View training volume history
2) View desired training volume date
3) View desired training volume period
4) Return to menu
Choose what would you like to view: """
    # cursor with trainings
    dummy_trainings = select_view_option(user_id, message_training_volume, selection="volume",
                                         muscle_group=selected_muscle_group)

    # return if user selected that option
    if dummy_trainings is None:
        return

    # show message if no training was found in the selected date
    if not dummy_trainings:
        print("\nNo training on this date or invalid date period!\n")
        return

    # extract reps, intensity and dates from returned cursor, separate entries and store them in lists
    dummy_reps = [dummy_trainings[i][0].split("-") for i in range(len(dummy_trainings))]
    dummy_intensities = [dummy_trainings[i][1].split("-") for i in range(len(dummy_trainings))]
    dates = [dummy_trainings[i][2] for i in range(len(dummy_trainings))]

    # parse reps and intensity from list of string into list of integers
    reps = [list(map(int, rep)) for rep in dummy_reps]
    intensities = [list(map(int, intensity)) for intensity in dummy_intensities]

    # calculate volume for each entry
    volume = [np.multiply(reps[i], intensities[i]).sum() for i in range(len(dummy_trainings))]

    # find unique values in dates for training volume
    unique_dates = list(set(dates))
    unique_dates.sort()

    # locate positions of unique values and store them in different lists
    index_dates = [list(locate(dates, lambda a: a == unique_dates[i])) for i in range(len(unique_dates))]

    # group volume elements into groups according to their date
    volume = [volume[index_dates[i][0]:index_dates[i][-1] + 1] for i in range(len(index_dates))]

    # sum groups of volumes
    volume = [sum(volume[i]) for i in range(len(volume))]

    # create list pairing training volume with dates (parsed from timestamps to dates)
    volume_with_dates = [[parse_input_timestamp_to_date(unique_dates[i]), volume[i]] for i in range(len(volume))]

    # print table
    header_volume = ("Date", "Training volume")
    print(f"\n{tabulate(volume_with_dates, headers=header_volume)}\n")

    # plot training volume (with parsed timestamps into dates)
    unique_dates = [parse_input_timestamp_to_date(unique_dates[i]) for i in
                    range(len(unique_dates))]
    if len(volume) > 1:
        plt.figure()
        plt.plot_date(unique_dates, volume, color='b', linestyle='-', linewidth=2)
        plt.xlabel("Dates (dd-mm-YYYY)")
        plt.ylabel("Training volume [kg]")
        plt.title(f"Training volume history ({selected_muscle_group} split)")
        plt.subplots_adjust(bottom=0.3)
        plt.xticks(rotation=30, ha="right")
        plt.show()


def view_muscle_group_division(user_id):
    # string with selected muscle group
    username = database.get_specific_user(user_id)
    print(f"\n--- Muscle groups for {username[0][0]} ---\n")

    # retrieve string with desired muscle group
    selected_muscle_group = select_muscle_group(user_id)

    # retrieve exercises from selected muscle group
    exercises_from_selected_muscle_group = database.get_exercises_from_muscle_group_from_user(user_id,
                                                                                              selected_muscle_group)

    # print exercises
    print("")
    for i in range(len(exercises_from_selected_muscle_group)):
        print(f"{exercises_from_selected_muscle_group[i][0]}")
    input("\nEnter any key to continue: ")


# FUNCTIONS TO BE CALLED BY MAIN FUNCTIONS
# ask exercise id and use check_id function to check input
def ask_exercise_id(user_id):
    # get exercise list from cursor
    exercises = database.get_all_exercises_from_user(user_id)

    # print names of exercises and list them from 1 to n
    for i in range(len(exercises)):
        print(f"{i + 1}) {exercises[i][1]}")
    # print last options to add exercise or go back to menu
    print(f"{len(exercises) + 1}) Add exercise")
    print(f"{len(exercises) + 2}) Go back to menu")

    # exercises IDs in a list of strings
    exercise_list = [f"{exercises[i][0]}" for i in range(len(exercises))]
    # list to check if user entered correct ID
    dummy_list = [f"{i + 1}" for i in range(len(exercises) + 2)]

    # check that input is a number and is within options
    message_select_exercise = "Select user to add exercise to (only ID number please): "
    select_exercise = check_id(message_select_exercise, dummy_list)

    # decide if exercise should be added, go back to menu or take existing exercise
    if select_exercise == dummy_list[-2]:
        insert_exercise(user_id)
        return None
    elif select_exercise == dummy_list[-1]:
        return True
    else:
        exercise_id = exercise_list[int(select_exercise) - 1]  # select proper exercise ID
        return exercise_id


# check that reps or intensities are input in the asked format
def check_reps_or_intensity(sets, message):
    while reps_or_intensity_input := input(message):
        try:
            try:
                try:
                    dummy = reps_or_intensity_input.split("-", int(sets))
                    [int(dum) for dum in dummy]
                    dummy[int(sets) - 1]
                    return reps_or_intensity_input
                except ValueError:
                    print("Error: wrong input. Follow the format given in the example!")
            except TypeError:
                print("Error: wrong input. Do not introduce letters!")
        except IndexError:
            print("Error: wrong input. Write the numbers for each respective set separated by a '-'!")


# check that input is a number and positive
def check_positive_input(message):
    while input_number := input(message):
        try:
            int(input_number)
            math.log(int(input_number), 2)
            return input_number
        except ValueError:
            print("Error: input must be a number and non-negative!")


# ask date and check that date exists and is in the correct format
def ask_date():
    # input date
    while training_date := input("Enter date in the format dd-mm-YYYY: "):
        try:
            datetime.datetime.strptime(training_date, '%d-%m-%Y')
            return training_date
        except ValueError:
            print("Error: enter date in the correct format (dd-mm-YYYY)!")


# parse input date into timestamp
def parse_date_into_timestamp(input_date):
    # parse from dd-mm-YYYY to timestamp
    parsed_training_date = datetime.datetime.strptime(input_date, "%d-%m-%Y")
    return parsed_training_date.timestamp()


# parse input timestamp into date
def parse_input_timestamp_to_date(input_date):
    # parse from timestamp to dd-mm-YYYY
    return datetime.datetime.fromtimestamp(input_date).strftime("%d-%m-%Y")


# selection of view option to retrieve trainings from logbook
def select_view_option(user_id, message, selection, muscle_group):
    # select viewing option
    dummy_list = [f"{i + 1}" for i in range(1, 5)]
    view_input = check_id(message, dummy_list)

    # depending on option, get cursor with all trainings, specific training or training period
    # commit transaction according to option
    if view_input == "1":
        if selection == "training":
            return database.get_all_trainings_from_user(user_id)
        elif selection == "volume":
            return database.get_muscle_group_for_volume_from_user(user_id, muscle_group)
    elif view_input == "2":
        print("--- Select desired training date ---")
        view_training_date = ask_date()
        # date must be parsed into timestamp to retrieve data from database
        view_training_date = parse_date_into_timestamp(view_training_date)
        if selection == "training":
            return database.get_specific_training_from_user(user_id, view_training_date)
        elif selection == "volume":
            return database.get_muscle_group_for_specific_volume_from_user(user_id, muscle_group, view_training_date)
    elif view_input == "3":
        print("--- INITIAL date of time period ---")
        initial_date_of_period = ask_date()
        print("--- FINAL date of time period ---")
        final_date_of_period = ask_date()
        # date must be parsed into timestamp for table in SQL
        initial_date_of_period = parse_date_into_timestamp(initial_date_of_period)
        final_date_of_period = parse_date_into_timestamp(final_date_of_period)
        if selection == "training":
            return database.get_training_period_from_user(user_id, initial_date_of_period, final_date_of_period)
        elif selection == "volume":
            return database.get_muscle_group_for_volume_in_period_from_user(user_id, muscle_group,
                                                                            initial_date_of_period,
                                                                            final_date_of_period)
    else:
        return None


# select muscle group and extract string with name
def select_muscle_group(user_id):
    # get list of user's muscle groups from cursor
    muscle_groups = database.get_muscle_group_from_user(user_id)

    # print muscle groups of user and list them
    for i in range(len(muscle_groups)):
        print(f"{i + 1}) {muscle_groups[i][0]}")

    # muscle groups positions in a list of strings
    dummy_muscle_groups = [f"{i + 1}" for i in range(len(muscle_groups))]

    # input number of muscle_group_id is a str; check that the input is within the numbers of users and is not letters
    message_muscle_groups = "Select muscle group (only ID number please): "
    muscle_group_input = check_id(message_muscle_groups, dummy_muscle_groups)

    # return string with name of the muscle group to be executed in SQLite
    return muscle_groups[int(muscle_group_input) - 1][0]


# SECOND MENU
while (user_option_1 == "2") and (user_option_2 := input(menu_2)) != "6":
    if user_option_2 == "1":
        insert_exercise(user_id)
        # function to add exercise
    elif user_option_2 == "2":
        insert_training(user_id)
        # function to add training -> add_training()
    elif user_option_2 == "3":
        view_training(user_id)
        # function to view training logs -> view_training()
    elif user_option_2 == "4":
        view_training_volume(user_id)
        # function to view training volume history -> view_training_volume()
    elif user_option_2 == "5":
        view_muscle_group_division(user_id)
        # function to view user's muscle groups -> view_muscle_group_division()
    else:
        print("Error: invalid option selected. Select a valid option!\n")
