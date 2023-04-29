from Levenshtein import distance


def min_distance(input: str, values: list[str]):
    last_min_distance = distance(input, values[0])
    min_values = [values[0]]

    for value in values:
        current_distance = distance(input, value)

        if last_min_distance == current_distance:
            min_values.append(value)

        elif current_distance < current_distance:
            min_values.clear()
            min_values.append(value)
            min_distance = current_distance

        return min_values, last_min_distance
