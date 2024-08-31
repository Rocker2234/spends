from typing import Union


def print_heighest(data):
    debits = []
    creds = []
    who = set()
    for item in data:
        debits.append(float(item[3]))
        creds.append(float(item[4]))
        who.add(item[1])
    high_t = data[debits.index(max(debits))]
    high_t = f"Date: {high_t[0]}\nTo: {high_t[1]}\nAmount:{high_t[3]}"
    print("Heighest single transaction:", high_t, sep="\n")


def view_all(data: list[list[str]]):
    for row in data:
        print(row[2], row[1], '-' + row[3] if float(row[3]) else '+' + row[4], "=" + row[6])


# noinspection PyUnresolvedReferences
def group_by_payee(data: list[list[str]]) -> dict:
    groups = {}
    for row in data:
        if not row[1] in groups.keys():
            groups[row[1]] = [float(row[3]), float(row[4])]
        else:
            groups[row[1]][0] = round(groups[row[1]][0] + float(row[3]), 2)
            groups[row[1]][1] = round(groups[row[1]][1] + float(row[4]), 2)
    return groups


def print_by_grp(grps: dict):
    print("===================")
    print("All Grouped Trnxs")
    for key in grps.keys():
        print("------------------------")
        print(key, f"Debit:{grps[key][0]}", f"Credit:{grps[key][1]}", sep='\n')
    print("===================")


def heighest_grp(grps: dict, value='D') -> list:
    high_p = ''
    if value.upper() == "C":
        action = 1
    else:
        action = 0

    for key in list(grps.keys()):
        if high_p == '':
            high_p = key
        elif grps[key][action] > grps[high_p][action]:
            high_p = key
    return [high_p, grps[high_p]]


def print_highest_grp(grps: dict, value='D'):
    high = heighest_grp(grps, value)
    action = 'credit' if value.upper() == 'C' else 'debit'
    print("============")
    print(f"Heighest {action}ed payee:")
    print(high[0], f"Debit: {high[1][0]}", f"Credit: {high[1][1]}", sep='\n')
    print("============")


def get_grp_totals(grps: dict) -> tuple:
    debits = 0.0
    creds = 0.0
    for key in grps.keys():
        debits += grps[key][0]
        creds += grps[key][1]
    return debits, creds


def get_totals(data: list) -> tuple:
    debits = 0.0
    creds = 0.0
    for transaction in data:
        debits += float(transaction[3])
        creds += float(transaction[4])
    return debits, creds


def print_totals(transactions: Union[list, dict]):
    if type(transactions) is list:
        debits, creds = get_totals(transactions)
    elif type(transactions) is dict:
        debits, creds = get_grp_totals(transactions)
    else:
        print("Error in transactions!")
        return

    debits = round(debits, 2)
    creds = round(creds, 2)

    print(f"Totals\n==============")
    print(
        f"Total Credits:\t{creds}\nTotal Debits:\t{debits}\n-----------------------\nDifference:   \t{round((creds - debits), 2)}")
