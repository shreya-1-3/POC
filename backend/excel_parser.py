import pandas as pd

def process_excel(file_path, engine):
    xls = pd.ExcelFile(file_path)
    tables = []

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)

        table_name = sheet.lower().replace(" ", "_")
        df.to_sql(table_name, engine, if_exists="replace", index=False)

        tables.append(table_name)

    return tables
