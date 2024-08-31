import os
import calendar


def hdfc(data_file: str, new_file: str = ''):
    """ Use this to format HDFC bank's Delemited transaction file which can be downloaded from the NetBanking website."""
    with open(data_file) as file:
        file.__next__()
        lines = file.readlines()

    lines = [line.replace(' ', '') for line in lines]

    last_date = lines[-1].split(',')[0]
    if not new_file:
        os.makedirs(f"Data/{last_date.split('/')[2]}", exist_ok=True)
        new_file = f"Data/{last_date.split('/')[2]}/{calendar.month_abbr[int(last_date.split('/')[1])].upper()}.csv"

    with open(new_file, 'w') as new_file:
        new_file.writelines(lines)
    print(f"Transactions written into: {new_file.name}")
    print(f"Number of transactions: {len(lines)-1}")
