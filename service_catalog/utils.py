def str_to_bool(s):
    if isinstance(s, bool):  # do not convert if already a boolean
        return s
    else:
        if s == 'True' \
                or s == 'true' \
                or s == '1' \
                or s == 1 \
                or s == True:
            return True
        elif s == 'False' \
                or s == 'false' \
                or s == '0' \
                or s == 0 \
                or s == False:
            return False
    return False
