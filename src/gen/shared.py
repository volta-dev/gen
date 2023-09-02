# finds the exchange name in the ast
def get_exchange(tree):
    for child in tree.children:
        if child.data == 'exchange':
            unquoted = child.children[0].value[1:-1]
            return unquoted[0].upper() + unquoted[1:]
        else:
            result = get_exchange(tree)
            if result:
                return result
    return None