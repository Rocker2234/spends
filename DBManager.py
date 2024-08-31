import datetime
import sqlite3
import csv
import sys

import Groupify


def adapt_datetime_epoch(val: datetime.datetime):
    """Adapt datetime.datetime to Unix timestamp."""
    return int(val.timestamp())


def adapt_boolean(val: bool):
    """Adapt boolean to 1/0"""
    return int(val)


sqlite3.register_adapter(datetime.datetime, adapt_datetime_epoch)
sqlite3.register_adapter(bool, adapt_boolean)


def convert_timestamp(val):
    """Convert Unix epoch timestamp to datetime.datetime object."""
    return datetime.datetime.fromtimestamp(int(val))


def convert_bool(val):
    """Convert 1/0 to boolean."""
    return bool(val)


sqlite3.register_converter("DATETIME", convert_timestamp)
sqlite3.register_converter("BOOLEAN", convert_bool)


class DBManager:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.connection.row_factory = lambda cursor, row: list(row)
        self.cursor = connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def initialize_DB(self):
        """Used to create nessasary tables. This should only be called onece for a given .db file."""

        self.cursor.execute("PRAGMA foreign_keys = ON;")  # Enable Forign Keys

        self.cursor.execute("""CREATE TABLE ACCOUNTS (
        ACC_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NAME TEXT NOT NULL,
        ACC_NO TEXT NOT NULL,
        IFSC_CODE TEXT NOT NULL,
        ACC_TYP TEXT,
        MIN_BAL REAL NOT NULL DEFAULT 0 CHECK (MIN_BAL >= 0),
        DIS_BAL REAL NOT NULL DEFAULT 0 CHECK (DIS_BAL >= 0),
        ACT_IND INTEGER NOT NULL DEFAULT 1 CHECK (ACT_IND IN (0,1)),
        UNIQUE(ACC_NO, IFSC_CODE))""")

        self.cursor.execute("""CREATE TABLE FILE_AUDIT (
        FILE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        FILE_NAME TEXT NOT NULL,
        ACC_ID INTEGER,
        OP_DESC TEXT,
        UPDT_DT DATETIME NOT NULL,
        ISRT_DT DATETIME NOT NULL,
        STATUS TEXT
        )""")

        self.cursor.execute("""CREATE TABLE TRANSACTIONS (
        TXN_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ACC_ID INTEGER REFERENCES ACCOUNTS(ACC_ID),
        TXN_DATE DATETIME NOT NULL,
        TXN_DESC TEXT NOT NULL,
        GRP_NAME TEXT,
        OPR_DT DATETIME NOT NULL,
        DBT_AMT REAL,
        CR_AMT REAL,
        REF_NBR TEXT NOT NULL DEFAULT 0,
        CF_AMT REAL NOT NULL,
        FILE_ID INTEGER REFERENCES FILE_AUDIT(FILE_ID));""")

    def add_account(self, name: str, acc_no: str, ifsc: str, typ: str, min_bal: float = 0, dis_bal: float = 0,
                    act_ind: int = 1):
        """ Insert a new bank account"""

        self.cursor.execute("""INSERT INTO ACCOUNTS (NAME,ACC_NO,IFSC_CODE,ACC_TYP,MIN_BAL,DIS_BAL,ACT_IND)
        VALUES (?,?,?,?,?,?,?)""", (name, acc_no, ifsc, typ, min_bal, dis_bal, act_ind))
        self.connection.commit()

    def add_transaction(self, acc_id: int, *values, **maps):
        """Insert new transaction, ignores maps kwarg if values arg is found."""

        if values:
            insert = [acc_id]
            insert.extend(values)
            self.cursor.execute("""INSERT INTO TRANSACTIONS 
            (ACC_ID,TXN_DATE,TXN_DESC,OPR_DT,DBT_AMT,CR_AMT,REF_NBR,CF_AMT,FILE_ID) 
            VALUES (?,?,?,?,?,?,?,?,?);""", insert)
        elif maps:
            insert = {
                "acc": acc_id,
                "date": None,
                "narration": None,
                "operation_date": None,
                "dbt_amt": None,
                "cr_amt": None,
                "ref_no": None,
                "cf_amt": None}
            for key in insert.keys():
                try:
                    insert[key] = maps[key]
                except KeyError:
                    print("Missing key:", key, "\nRow not inserted!", file=sys.stderr)
                    return
            self.cursor.execute("""INSERT INTO TRANSACTIONS
            (ACC_ID,TXN_DATE,TXN_DESC,OPR_DT,DBT_AMT,CR_AMT,REF_NBR,CF_AMT) 
            VALUES (:acc,:date,:narration,:operation_date,:dbt_amt,:cr_amt,:ref_no,:cf_amt);""", insert)
        else:
            print("No data passed, nothing inserted!")

    # noinspection PyTypeChecker
    def load_transactions(self, acc_id: int, file: str, grouper: str = "<standard>"):
        """Load transactions from a csv file. Refer the documentation for the format to load data properly."""

        with open(file) as f:
            reader = csv.reader(f)
            reader.__next__()
            curr_time = datetime.datetime.now()
            self.cursor.execute("""INSERT INTO FILE_AUDIT 
                (FILE_NAME,ACC_ID,OP_DESC,UPDT_DT,ISRT_DT,STATUS)
                VALUES (?,?,'Data Import',?,?,'Uploaded')""", (file, acc_id, curr_time, curr_time))
            self.cursor.execute("SELECT FILE_ID FROM FILE_AUDIT WHERE ISRT_DT=? AND FILE_NAME=?", (curr_time, file))
            file_id = self.cursor.fetchone()[0]
            for row in reader:
                row[0] = datetime.datetime.strptime(row[0], "%d/%m/%y")
                row[2] = datetime.datetime.strptime(row[2], "%d/%m/%y")
                row.append(file_id)
                self.add_transaction(acc_id, *row)
        self.connection.commit()
        print("File successfully imported!\nFile ID:", file_id)
        self.cursor.execute("UPDATE FILE_AUDIT SET STATUS='Successful', UPDT_DT=UNIXEPOCH() WHERE FILE_ID=?", (file_id,))
        self.connection.commit()
        self.update_grps(file_id, grouper)
        self.connection.commit()
        return file_id

    def update_grps(self, file_id: int, grouper: str = "<standard>"):
        """Used to identify groups for a file uploaded, if grouper is set to <skip>, the transaction is skipped,
        or the user can pass in any text file name for execution of custom python code. Default value will run standard grouping."""

        self.cursor.execute("SELECT TXN_ID, TXN_DESC FROM TRANSACTIONS WHERE FILE_ID=?", (file_id,))
        for row in self.cursor.fetchall():
            if grouper == "<standard>":
                group_val = Groupify.standard(row[1])
                self.cursor.execute("UPDATE TRANSACTIONS SET GRP_NAME=? WHERE TXN_ID=?", (group_val, row[0]))
            elif grouper != "<skip>":
                group_val = Groupify.custom(row[1], grouper)
                self.cursor.execute("UPDATE TRANSACTIONS SET GRP_NAME=? WHERE TXN_ID=?", (group_val, row[0]))

    def get_tansactions(self, **filters):
        sql = "SELECT * FROM TRANSACTIONS"
        if filters:
            sql += " WHERE "
            for key in filters:
                if key == 'start':
                    print("Adding start condition!")
                    sql += "TXN_DATE >= :start AND "
                elif key == 'end':
                    print("Adding end condition!")
                    sql += "TXN_DATE <= :end AND "
                elif key == "min_credit":
                    print("Adding min credit condition!")
                    sql += "CR_AMT >= :min_credit AND "
                elif key == "max_credit":
                    print("Adding max credit condition!")
                    sql += "CR_AMT <= :max_credit AND "
                elif key == "min_debit":
                    print("Adding min debit condition!")
                    sql += "DBT_AMT >= :min_debit AND "
                elif key == "max_debit":
                    print("Adding max debit condition!")
                    sql += "DBT_AMT <= :max_debit AND "
                elif key == "desc_like":
                    print("Description filter!")
                    sql += "TXN_DESC LIKE '%'||:desc_like||'%' AND "
                elif key == "file_id":
                    sql += "FILE_ID = :file_id AND "
                else:
                    print(f"Unknown filter {key}, ignoring it.")
            if sql.endswith("AND "):
                sql = sql.rstrip("AND ")
        self.cursor.execute(sql, filters)
        tanx_list = self.cursor.fetchall()
        return tanx_list


if __name__ == "__main__":
    # conn = sqlite3.connect("Data/Spends.db", detect_types=sqlite3.PARSE_DECLTYPES)
    conn = sqlite3.connect("Data/Test.db", detect_types=sqlite3.PARSE_DECLTYPES)
    # conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    dbm = DBManager(conn)
    # dbm.initialize_DB()
    # dbm.add_account("HDFC", "123456789", "HDFC0000999", "Salary")
    # dbm.load_transactions(1, "Data/22/Combined.csv", "Custom_formatter.txt")
    # dbm.load_transactions(1, "Data/23/Combined.csv", "Custom_formatter.txt")
    # dbm.load_transactions(1, "Data/24/Combined.csv", "Custom_formatter.txt")
    # print(dbm.get_tansactions(file_id=1)[5:8])
    # dbm.update_grps(1, "Custom_formatter.txt")
