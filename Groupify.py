import pathlib


def standard(txn_desc: str) -> str:
    """A standard method for grouping transactions."""

    if txn_desc.startswith('UPI'):
        txn_desc = txn_desc[:txn_desc.find("-", 4)]
        if txn_desc.startswith('UPI-IRCTC'):
            txn_desc = "UPI-IRCTC"
    elif txn_desc.startswith('IMPS'):
        temp = txn_desc.split('-')
        txn_desc = "-".join([temp[0], temp[2], temp[3], temp[4]])
    elif txn_desc.startswith('NEFT'):
        temp = txn_desc.split('-')
        txn_desc = "-".join([temp[0], temp[2]])
    elif txn_desc.find("RDINSTALLMENT") != -1:
        txn_desc = "RDINSTALLMENT"
    return txn_desc


def custom(txn_desc: str, file: str) -> str:
    code = f"txn_desc='{txn_desc}'\n" + pathlib.Path(file).read_text()
    result = {}
    exec(code, locals(), result)
    return result['txn_desc']
