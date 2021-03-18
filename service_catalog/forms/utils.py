

def get_choices_from_string(string_with_anti_slash_n):
    split_lines = string_with_anti_slash_n.splitlines()
    returned_list = list()
    for line in split_lines:
        returned_list.append((line, line))
    return returned_list
