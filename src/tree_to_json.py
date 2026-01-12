# converts parse tree to json format
def tree_to_json(tree):
  if tree is None:
      return None
  node = {}
  node['value'] = tree.getKey()
  left = tree.getLeftTree()
  right = tree.getRightTree()

  if left != None:
    node['left'] = tree_to_json(left)

  if right != None:
    node['right'] = tree_to_json(right)

  return node