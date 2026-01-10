class BinaryTree:
    def __init__(self, key, left=None, right=None):
        self.left_tree = left
        self.right_tree = right
        self.key = key

    def setKey(self, key):
        self.key = key
        return

    def getKey(self):
        return self.key

    def getLeftTree(self):
        return self.left_tree
    
    def getRightTree(self):
        return self.right_tree

    def insertLeft(self, tree):
        if self.left_tree == None:
            self.left_tree = tree

        else:
            # there alr is a tree
            self.left_tree.insertLeft(tree)

        return

    def insertRight(self , tree):
        if self.right_tree == None:
            self.right_tree = tree
        else:
            self.right_tree.insertRight(tree)
        return

    def print_tree_inorder(self, level=0):
      if self.getLeftTree() is not None:
        self.getLeftTree().print_tree_inorder(level + 1)

      print('.' * level + str(self.getKey()))

      if self.getRightTree() is not None:
        self.getRightTree().print_tree_inorder(level + 1)
