
class CommandTree(object):

    def __init__(self, data, children=None):
        if children:
            self.children = children
        else:
            self.children = []

        self.data = data

    def add_children(self, child):
        self.children.append(child)

    def get_child(self, name):
        """
        returns the CommandTree of the name corresponding to
        the name provided
        the name should be a string
        """
        for kid in self.children:
            if kid.data == name:
                return kid
        else:
            raise ValueError("No such child: {}".format(name))
