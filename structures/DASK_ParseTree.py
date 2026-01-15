from structures.BinaryTree import BinaryTree
from structures.Stack import Stack

class DASK_ParseTree:
  def __init__(self):
    self.operations = ['+' , '-' , '/' , '*' , '**' , '++' , '//']


  def verify_expression(self, exp):
    '''
    Returns False if bad, True if ok
    '''
    tokens = self.tokenizer(exp)
    stack = Stack()
    for t in tokens:

      if t == ')':
        # we backtrack the stack
        if stack.is_empty():
          return False

        exp_group = []
        while not stack.is_empty():
          top = stack.pop() 

          if top == '(':
            break
          else:
            exp_group.append(top)

        else:
          # we didnt find a matching (
          return False

        exp_group.reverse()
        # now we have a expression group
        # since we are dealing with binary trees the only exp check is len(3), start end in brackets, 2 values. mid is operator

        if len(exp_group) == 1 and (exp_group[0].isalpha() or exp_group[0].replace('.','',1).isdigit()):
          # single value expression ok
          stack.push('EXP')
          continue

        if len(exp_group) != 3:
          return False
        # operator
        if exp_group[1] not in self.operations:
          return False
        # values
        if not (exp_group[0].isalpha() or exp_group[0].replace('.','',1).isdigit()):
          return False
        if not (exp_group[2].isalpha() or exp_group[2].replace('.','',1).isdigit()):
          return False

        # push a placeholder variabel
        stack.push('EXP')

        
      else:
        stack.push(t)
        

      # we should end with 'EXP' only
    return stack.size() == 1 and stack.pop() == 'EXP'
        
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
      elif i.isdigit() or i == '.':
        if len(tokens) > 0 and (tokens[-1].isdigit() or '.' in tokens[-1]):
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
      # Just a check for single value expressions like (42) or (Pi)
      if len(tokens) == 3:
        # since all exps are paranthesized we just need to check len = 3
        return BinaryTree(tokens[1])


      tree = BinaryTree('?')
      stack = Stack()
      stack.push(tree)

      currentTree = tree

      for t in tokens:
          if t == '(':
              next_branch = BinaryTree('?')
              currentTree.insertLeft(next_branch)
              stack.push(currentTree)
              currentTree = next_branch
          elif t in self.operations:
              currentTree.setKey(t)
              right_branch = BinaryTree('?')
              currentTree.insertRight(right_branch)
              stack.push(currentTree)
              currentTree = right_branch
          elif t == ')':
              currentTree = stack.pop()
          else:
              currentTree.setKey(t)
              currentTree = stack.pop()

      return tree

  def evaluate(self , tree, hash_table):
      # post traversal
      leftTree = tree.getLeftTree()
      rightTree = tree.getRightTree()
      op = tree.getKey()

      # main evaluation
      if leftTree != None and rightTree != None:
        left_val = self.evaluate(leftTree, hash_table)
        if left_val is None:
            return None

        right_val = self.evaluate(rightTree, hash_table)
        if right_val is None:
            return None

        if op == '+':
            return left_val + right_val
        if op == '-':
            return left_val - right_val
        if op == '/':
            return left_val / right_val
        if op == '*':
            return left_val * right_val
        if op == '**':
            return left_val ** right_val
        if op == '++':
            return self.summative(left_val) + self.summative(right_val)
        if op == '//':
            return self.summative(left_val) / self.summative(right_val)



        return None  # unknown operator
      
      # there is left right expression that evals to None and current is op
      if op in self.operations:
        return None
      
      if op.isalpha():
        # query variable value from table
        return hash_table[op].value if hash_table[op] != None else None

      return float(op)

if __name__ == '__main__':
  exp = "((a + b) * (c - d))"
  exp = "(24)"
  parser = DASK_ParseTree()
  tokens = parser.tokenizer(exp)
  print("Is expression valid? ", parser.verify_expression(tokens))
