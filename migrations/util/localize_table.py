from uuid import uuid4
from models.Language import Language


def localize_one_id_table(conn, table, id_col_name, text_col_names, local_type='string'):
    table_name = str(table.fullname)
    joined_columns = ', '.join(text_col_names)
    query = 'select {0}, {1} from {2}'.format(id_col_name, joined_columns, table_name)

    res = conn.execute(query)
    locale_update = []

    for row_id, *columns in res:
        update_dict = {}

        for idx, col_value in enumerate(columns):
            if col_value is not None:
                col_name = text_col_names[idx]
                uuid = str(uuid4())

                if local_type == 'string':
                    locale_update.append({
                        'string_id': uuid,
                        'string_locale': Language.ru,
                        'string_content': col_value
                    })
                elif local_type == 'link':
                    locale_update.append({
                        'link_id': uuid,
                        'link_locale': Language.ru,
                        'link_path': col_value
                    })

                update_dict[col_name + '_id'] = uuid

        if len(update_dict) > 0:
            conn.execute(
                table.update().where(
                    table.c[id_col_name] == row_id
                ).values(**update_dict)
            )

    return locale_update


def localize_two_id_table(conn, table, col_id_names, text_col_names, local_type='string'):
    table_name = str(table.fullname)
    id_names = ', '.join(col_id_names)
    joined_columns = ', '.join(text_col_names)
    query = 'select {0}, {1} from {2}'.format(id_names, joined_columns, table_name)

    res = conn.execute(query)
    locale_update = []

    for first_row_id, second_row_id, *columns in res:
        update_dict = {}

        for idx, col_value in enumerate(columns):
            if col_value is not None:
                col_name = text_col_names[idx]
                uuid = str(uuid4())

                if local_type == 'string':
                    locale_update.append({
                        'string_id': uuid,
                        'string_locale': Language.ru,
                        'string_content': col_value
                    })
                elif local_type == 'link':
                    locale_update.append({
                        'link_id': uuid,
                        'link_locale': Language.ru,
                        'link_path': col_value
                    })

                update_dict[col_name + '_id'] = uuid

        if len(update_dict) > 0:
            conn.execute(
                table.update().where(
                    table.c[col_id_names[0]] == first_row_id
                ).where(
                    table.c[col_id_names[1]] == second_row_id
                ).values(**update_dict)
            )

    return locale_update
