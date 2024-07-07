def load_exercises(file_path):
    with open(file_path, 'r') as file:
        exercises = [line.split(',')[0].strip() for line in file.readlines()]
    return exercises
