"""This file is created to show an example of using this tool. Currently only CSV is fully operational"""
import datetime

import Operations
import Parser
import Utils

#   First parse the file downlaoded form your bank.
Parser.hdfc("path/to/file")  # This will create a file in Data/<year> called <month>.csv

# Load the created file to do multiple operations...
data_file = "Data/24/AUG.csv"

data = Operations.load(data_file)

# Sort RAW
data_s = Operations.sort_by(data, 'N', False)

# Filter RAW
fr_dt = datetime.datetime.strptime("22/03/24", "%d/%m/%y")
to_dt = datetime.datetime.strptime("03/04/24", "%d/%m/%y")
data_ft = Operations.filter_by_date(data_s, fr_dt)
data_f = Operations.filter_by(data, "INTEREST")

# View RAW
Utils.view_all(data_ft)


# Utils.print_heighest(data)

# You can also group the transactions instead of viewing it RAW and giving your self more clarity.
# Note: Grouping uses the Narration part of the row to identify unique payees. So usually it is recomended to clear up the non-common parts to work with.
# An example is given below.

def beautify_payee(tarnxs: list[list[str]]):
    for row in tarnxs:
        if row[1].startswith('POS'):
            row[1] = f"POS-{row[1][19:]}"
            if row[1] == "POS-ZOMATOLIMITED":
                row[1] = "POS-ZOMATO"   # Renames POS-ZOMATOLIMITED to POS-ZOMATO to avoid duplicates.
        elif row[1].startswith('UPI'):
            row[1] = row[1][:row[1].find("-", 4)]   # Removes unwated information of a UPI transaction.


beautify_payee(data)

# Group
grps = Utils.group_by_payee(data)

# Sort Grouped
grps = Operations.sort_by_grp(grps, 'D', False)

# View by Group
Utils.print_by_grp(grps)
Utils.print_totals(grps)
# Utils.print_highest_grp(grps, 'C')
