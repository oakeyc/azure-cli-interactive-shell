
class CommandTree(object):

    def __init__(self, data, children=None):
        self.data = data
        self.children = children

    def get_child(self, child_name, tree):
        for kid in tree:
            if kid.data == child_name:
                return kid
        raise ValueError("Value not in this tree")

    def add_child(self, child):
        self.children.append(child)

    def has_child(self, name):
        if self.children is None:
            return False
        return any(kid.data == name for kid in self.children)

class CommandHead(CommandTree):
    """ represents the head of the tree, no data"""

    def __init__(self, children=None):
        CommandTree.__init__(self, None, children=[])

    def get_subbranch(self, data):
        data_split = data.split()
        kids = self.children
        for word in data_split:
            kid = self.get_child(word, kids)
            kids = kid.children

        return self.get_subbranch_help(kids, [])

    def get_subbranch_help(self, to_check, acc):
        check_next = []
        if to_check is None:
            return acc
        for branch in to_check:
            if branch is None:
                continue
            else:
                acc.append(branch.data)
                check_next.extend(branch.children)
        self.get_subbranch_help(check_next, acc)
        return acc


class CommandBranch(CommandTree):
    """ represents a branch of the tree """

    def __init__(self, data, children=None):
        CommandTree.__init__(self, data, children)
