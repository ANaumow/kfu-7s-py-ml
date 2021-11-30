import random
from functools import reduce


def first_generation(generation_values_range=[1, 20],
                     generation_size=4):
    individuals = []

    for i in range(generation_size):
        individual = [random.randint(*generation_values_range) for _ in range(x_count)]
        individuals.append(individual)

    return individuals


def generate_child(parent1, parent2):
    temp_array = [parent1, parent2]
    child = []

    for i in range(x_count):
        child.append(temp_array[random.randint(0, 1)][i])

    return child


def reproduce(generation):
    new_generation = []

    while len(generation) > 1:
        individual = generation.pop()

        best_candidate_diff = -1
        best_candidate = -1

        for candidate in generation:
            candidate_diff = 0
            for i in range(x_count):
                candidate_diff += abs(individual[i] - candidate[i])

            if candidate_diff > best_candidate_diff:
                best_candidate_diff = candidate_diff
                best_candidate = candidate

        generation.remove(best_candidate)

        child_count = random.randint(2, 4)
        for i in range(child_count):
            child = generate_child(individual, best_candidate)
            new_generation.append(child)

    return new_generation


def mutate(generation):
    for individual in generation:
        for i in range(x_count):
            individual[i] += random.randint(-2, 2)


def target_fn(params, individual):
    return sum([params[i] * individual[i] for i in range(x_count)])


def do_selection(generation, params, result, limit=4):
    sorted_by_fn = sorted(generation, key=lambda individual: abs(result - target_fn(params, individual)))
    return sorted_by_fn[:limit]


if __name__ == '__main__':
    x_count = 6
    param_value_range = [0, 15]
    param_values = [random.randint(*param_value_range) for x in range(x_count)]

    solution_x_value_range = [0, 10]
    possible_x_values = [random.randint(*solution_x_value_range) for x in range(x_count)]

    result = target_fn(param_values, possible_x_values)

    print("будет решаться следующее уравнение: ")
    print(reduce(lambda x, y: x + " + " + y,
                 [str(param_values[i]) + " * x" + str(i) for i in range(x_count)]) + " = " + str(result))

    solution = None
    generation_limit = 1000
    generation_number = 0

    current_generation = first_generation()

    while True:
        current_generation = reproduce(current_generation)

        mutate(current_generation)

        current_generation = do_selection(current_generation, param_values, result)

        # print('номер поколения:', generation_number, ', лучшая особь', generation[0], ', разница',
        #       target_fn(param_values, generation[0]) - result)
        # print(generation)

        if target_fn(param_values, current_generation[0]) == result:
            solution = current_generation[0]
            break

        generation_number += 1
        if generation_number > generation_limit:
            break

    print('решение', solution)
    print('поколений было', generation_number)
    print('последнее поколение', current_generation)
