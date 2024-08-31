import csv
import datetime


def load(data_file: str) -> list:
    data = []
    with open(data_file) as file:
        file.__next__()
        reader = csv.reader(file)
        for row in reader:
            if len(row):
                data.append(row)
    return data


def sort_by(data: list, value='N', reverse=False) -> list:
    if value.upper() == "C":
        action = 4
    elif value.upper() == 'D':
        action = 3
    else:
        action = 0
        return sorted(data, key=lambda item: datetime.datetime.strptime(item[action], "%d/%m/%y"), reverse=reverse)
    return sorted(data, key=lambda item: float(item[action]), reverse=reverse)


def filter_by(data: list, term) -> list:
    def fil(v):
        if v[1].lower().find(term.lower()) >= 0:
            return True
        else:
            return False

    return list(filter(fil, data))


def filter_by_date(data: list, fr_dt: datetime.datetime, to_dt: datetime.datetime = datetime.datetime.now()):
    def fil(v):
        txn_dt = datetime.datetime.strptime(v[0], "%d/%m/%y")
        if fr_dt <= txn_dt <= to_dt:
            return True
        else:
            return False

    return list(filter(fil, data))


def sort_by_grp(grps: dict, value='D', reverse=False) -> dict:
    if value.upper() == "C":
        action = 1
    else:
        action = 0

    s = sorted(grps.items(), key=lambda item: item[1][action], reverse=reverse)
    res = {}
    for grp in s:
        res[grp[0]] = grp[1]
    return res


def filter_by_grp(grps: dict, term: str) -> dict:
    def fil(v):
        if v[0].lower().find(term.lower()) >= 0:
            return True
        else:
            return False

    f = filter(fil, grps.items())
    res = {}
    for grp in f:
        res[grp[0]] = grp[1]
    return res
