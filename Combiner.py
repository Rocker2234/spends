import calendar


def combine(year):
    data_dir = f"Data/{year}"
    out_file = data_dir + '/Combined.csv'
    all_data = "Date,Narration,ValueDat,DebitAmount,CreditAmount,Chq/RefNumber,ClosingBalance\n"

    for month in calendar.month_abbr[1:]:
        try:
            file_found = False
            with open(f"{data_dir}/{month.upper()}.csv") as month_file:
                file_found = True
                month_file.__next__()
                all_data += month_file.read()
        except FileNotFoundError:
            if file_found:
                print(f"{month.upper()}.csv not found in the dir. Stopping.")
                break

    with open(out_file, 'w', newline='\n') as combine_file:
        combine_file.write(all_data)


if __name__ == "__main__":
    combine("22")
