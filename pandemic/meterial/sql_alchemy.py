def get_table_define_as_markdown(base):
    tables = [x for x in base.metadata.tables.values()]
    arr = []

    for table in tables:
        """
        'key',
        'name',
        'table',
        'type',
        'is_literal',
        'primary_key',
        'nullable',
        'default',
        'server_default',
        'server_onupdate',
        'index',
        'unique',
        'system',
        'doc',
        'onupdate',
        'autoincrement',
        'constraints',
        'foreign_keys',
        'comment',
        'computed',
        '_creation_order',
        'dispatch',
        'proxy_set',
        'description',
        'comparator',
        '_cloned_set',
        '_from_objects',
        '_label',
        '_key_label',
        '_render_label_in_columns_clause'
        """

        arr.append("## " + table.name)
        if table.comment:
            arr.append(table.comment)
            arr.append("")
        arr.append(
            "| name | type | pk | unique | index | nullable | default | comment |"
        )
        arr.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        for column in table._columns.values():

            dic = create_column_info_as_dict(
                name=column.name,
                type_=column.type,
                pk=column.primary_key,
                unique=column.unique,
                index=column.index,
                nullable=column.nullable,
                default=column.default,
                comment=column.comment,
            )

            s = "| {name} | {type} | {pk} | {unique} | {index} | {nullable} | {default} | {comment} |".format(
                **dic
            )
            arr.append(s)

        arr.append("")

    return "\n".join(arr)


def create_column_info_as_dict(
    name, type_, pk, unique, index, nullable, default, comment
):
    def get_value_or_empty(value):
        if value is None:
            return ""
        else:
            return value

    def get_str_or_ohter(value):
        if isinstance(value, str) and value == "":
            return '""'

        return value

    try:
        type_ = str(type_)
    except:
        # JSON?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        type_ = type(type_).__name__

    # ????????????None????????????????????????????????????????????????????????????
    return dict(
        name=get_value_or_empty(name),
        type=get_value_or_empty(type_),
        pk="x" if pk else "",
        unique="x" if unique else "",
        index="x" if index else "",
        nullable="x" if nullable else "",
        default=get_str_or_ohter(default.arg) if default else "",
        comment=get_value_or_empty(comment),
    )
