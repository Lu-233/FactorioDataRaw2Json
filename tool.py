
def table2dict(data):
    """ lupa._lupa._LuaTable to dict """
    if str(type(data)) != "<class 'lupa._lupa._LuaTable'>":
        return data

    for k, v in data.items():
        if str(type(v)) != "<class 'lupa._lupa._LuaTable'>":
            continue
        if 1 in list(v.keys()):  # for array
            if k == "ingredients":
                tmp = {}
                for x, y in v.items():
                    if "name" in y:
                        tmp[y["name"]] = y["amount"]
                    else:
                        tmp[y[1]] = y[2]
                data[k] = tmp
            else:
                data[k] = [table2dict(y) for x, y in v.items()]
        else:
            data[k] = table2dict(v)

    return dict(data)
