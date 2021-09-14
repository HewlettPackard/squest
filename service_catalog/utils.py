import os
import re


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


def get_mysql_dump_major_version():
    """
    Return the major version of the mysqldump command. E.g: 8
    """
    stream = os.popen('mysqldump --version')
    output = stream.read()
    regex = r"mysqldump\s+Ver\s(?P<version>\d+).*"
    matches = re.search(regex, output)
    if matches:
        if matches.group("version") is not None:
            return int(matches.group("version"))
    return None


def get_celery_crontab_parameters_from_crontab_line(crontab_line):
    """
    Get a crontab line line '0 1 * * *' and return a dict that can be used in the Celery crontab scheduler

    """
    line_split_on_space = crontab_line.split()
    return {
        "minute": line_split_on_space[0],
        "hour": line_split_on_space[1],
        "day_of_week": line_split_on_space[2],
        "day_of_month": line_split_on_space[3],
        "month_of_year": line_split_on_space[4]
    }
