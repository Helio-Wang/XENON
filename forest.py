import json

_OPEN_BRACKET = '('
_CLOSED_BRACKET = ')'
_CHILD_SEPARATOR = ','


class Node:
    """
    Node in a rooted leaf-labeled full binary forest
    """
    def __init__(self, key):
        self.parent = None
        self.left_child = None
        self.right_child = None
        self.key = key
        self.label = str(key)
        self.color = '#555'

    def __repr__(self):
        return self.label

    def add_child(self, child):
        if self.left_child is None:
            self.left_child = child
        else:
            self.right_child = child
        child.parent = self

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return self.left_child is None and self.right_child is None
    
    def leaf_set(self):
        """ Set of leaves in the subtree """
        if self.is_leaf():
            return {self}
        return self.left_child.leaf_set().union(self.right_child.leaf_set())

    def subtree_node_set(self):
        """ all the nodes in the subtree """
        if self.is_leaf():
            return {self}
        subset = self.left_child.subtree_node_set().union(self.right_child.subtree_node_set())
        subset.add(self)
        return subset

    def flatten(self):
        if self.is_leaf():
            return {"name": str(self.label), "color": str(self.color)}
        return {"name": str(self.key), "color": str(self.color),
                "children": [self.left_child.flatten(), self.right_child.flatten()]}



def from_newick(newick, label_prefix=''):
    if newick[-1] == ';':
        newick = newick[:-1]
    key, cursor, brackets = 0, 0, 0
    root = Node(key)
    root.label = label_prefix + str(key)
    key += 1
    current_node = root

    while cursor < len(newick):
        character = newick[cursor]
        if character == _OPEN_BRACKET:
            new_node = Node(key)
            new_node.label = label_prefix + str(key)
            current_node.add_child(new_node)
            current_node = new_node
            key += 1
            cursor += 1
            brackets += 1
        elif character == _CHILD_SEPARATOR:
            new_node = Node(key)
            new_node.label = label_prefix + str(key)
            assert current_node.parent.right_child is None, 'too much children'
            current_node.parent.add_child(new_node)
            current_node = new_node
            key += 1
            cursor += 1
        elif character == _CLOSED_BRACKET:
            current_node = current_node.parent
            cursor += 1
            brackets -= 1
            if brackets < 0:
                return None
        else:
            label = [character]
            cursor += 1
            while cursor < len(newick) and newick[cursor] not in (_CHILD_SEPARATOR, _CLOSED_BRACKET):
                label.append(newick[cursor])
                cursor += 1
            label = ''.join(label).strip()
            current_node.label = label

    return root



def to_json(newick1, newick2, out1, out2):
    root1 = from_newick(newick1, 'p')
    root2 = from_newick(newick2, 'q')

    # build the colors
    leaves = list(root1.leaf_set())
    get_color = {}
    for i, leaf in enumerate(leaves):
        color = i / len(leaves)
        leaf.color = color
        get_color[leaf.label] = color
    for leaf in root2.leaf_set():
        leaf.color = get_color[leaf.label]
    
    with open(out1, 'w') as outfile:
        json.dump(root1.flatten(), outfile)
    with open(out2, 'w') as outfile:
        json.dump(root2.flatten(), outfile)


if __name__ == '__main__':
    with open('input.txt', 'r') as f:
        nw1 = f.readline().rstrip()
        nw2 = f.readline().rstrip()
    
        out1, out2 = 'tree1.json', 'tree2.json'
        to_json(nw1, nw2, out1, out2)



