from structures.BinaryTree import BinaryTree
from structures.HashTable import HashTable

class DASK_ParseTree:
  def __init__(self, size = 100):
    self.operations = ['+' , '-' , '/' , '*' , '**' , '++' , '//']

  def summative(self , a ):
    return a * ( a + 1 ) // 2 

  def tokenizer(self , exp):
    tokens = []
    for i in exp:
      if i in ['(' , ')']:
        tokens.append(i)
      
      elif i in self.operations:
        if len(tokens) > 0 and tokens[-1] in self.operations:
          # build token if multi-char operator
          tokens[-1] = tokens[-1] + i
        else:
          # single char
          tokens.append(i)

      # All same logic as above
      elif i.isdigit():
        if len(tokens) > 0 and tokens[-1].isdigit():
          tokens[-1] = tokens[-1] + i
        else:
          tokens.append(i)
       
      elif i.isalpha():
        if len(tokens) > 0 and tokens[-1].isalpha():
          tokens[-1] = tokens[-1] + i
        else:
          tokens.append(i)
      
      else:
        # not a char what we want
        continue
    return tokens

  def buildParseTree(self, tokens):
      tree = BinaryTree('?')
      stack = []
      stack.append(tree)

      currentTree = tree

      for t in tokens:
          if t == '(':
              next_branch = BinaryTree('?')
              currentTree.insertLeft(next_branch)
              stack.append(currentTree)
              currentTree = next_branch
          elif t in ['+' , '-' , '/' , '*', '**' , '++', '//']:
              currentTree.setKey(t)
              right_branch = BinaryTree('?')
              currentTree.insertRight(right_branch)
              stack.append(currentTree)
              currentTree = right_branch
          elif t == ')':
              currentTree = stack.pop(-1)
          else:
              currentTree.setKey(int(t))
              currentTree = stack.pop(-1)

      return tree

  def evaluate(self , tree, hash_table):
      # post traversal
      leftTree = tree.getLeftTree()
      rightTree = tree.getRightTree()
      op = tree.getKey()

      if leftTree != None and rightTree != None:
          if op == '+':
              return self.evaluate(leftTree) + self.evaluate(rightTree)
          if op == '-':
              return self.evaluate(leftTree) - self.evaluate(rightTree)
          if op == '/':
              return self.evaluate(leftTree) / self.evaluate(rightTree)
          if op == '*':
              return self.evaluate(leftTree) * self.evaluate(rightTree)
          if op == '**':
              return self.evaluate(leftTree) ** self.evaluate(rightTree)
          if op == '++':
              return self.summative(self.evaluate(leftTree)) + self.summative(self.evaluate(rightTree))
          if op == '//':
              return self.summative(self.evaluate(leftTree)) / self.summative(self.evaluate(rightTree))
      
      if op.isalpha():
        # query variable value from table
        return hash_table[op]

      return op

if __name__ == '__main__':
  exp = "( ((10 ++ 5 ) // 3 )) * (Beta - Alpha)"
  parser = DASK_ParseTree()
  tokens = parser.tokenizer(exp)
  print(tokens)
