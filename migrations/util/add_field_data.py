def add_field_data(conn, table, id_col_name, id_value,  col_name, col_data):

    update_dict = {col_name: col_data}
    conn.execute(
        table.update().where(
            table.c[id_col_name] == id_value
        ).values(update_dict)
    )


