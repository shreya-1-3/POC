from sqlalchemy import inspect

def get_schema(engine):
    inspector = inspect(engine)
    schema = ""

    for table in inspector.get_table_names():
        schema += f"Table {table}:\n"
        for col in inspector.get_columns(table):
            schema += f"- {col['name']} ({col['type']})\n"
        schema += "\n"

    return schema
