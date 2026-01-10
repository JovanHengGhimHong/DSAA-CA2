import networkx as nx
from structures.DASK_ParseTree import DASK_ParseTree
from structures.SortedMap import SortedMap
from structures.HashTable import HashTable, Dask

start_msg = '''
*******************************************************************************
*                                                                             *
*                   ST1507 DSAA: DASK Expression Evaluator!                   *
*-----------------------------------------------------------------------------*
*     - Author: Jovan Heng (2401418) & Joen Choo (2415828)                          *
*     - Class: DAAA 2A 22                                                     *
*                                                                             *
*******************************************************************************
'''
menu_msg = '''
  Please select your choice ('1' , '2', '3' , '4' , '5' , '6'):
    1. Add/Modify DASK Expressions
    2. Display current DASK expressions
    3. Evaluate a single DASK variable
    4. Read DASK expressions from file
    5. Sort DASK expressions
    6. Exit
'''
print(start_msg)
print(menu_msg)

# We always create a parse tree object and hash table to store variables
parser = DASK_ParseTree()
hash_table = HashTable(100)
topological_graph = nx.DiGraph()

def add_dask_expresssion(key, exp):
    tokens = parser.tokenizer(exp)
    print(key , tokens)

    # Parse tree build and evaluate
    hash_table[key] = Dask(expression=tokens, value=None)

    # Adding to topological graph
    # key relies on t
    added_edges = [topological_graph.add_edge(t, key) for t in tokens if t.isalpha()]

    # independent
    if len(added_edges) == 0:
      dask_obj = hash_table[key]
      dask_obj.independent = True

      # this becomes an expression that we can immediately evaluate
      tree = parser.buildParseTree(dask_obj.expression)
      value = parser.evaluate(tree, hash_table)
      dask_obj.value = value

      # update
      hash_table[key] = dask_obj
    return

def show_dask_expressions(hash_table, topological_graph, sorting_key=lambda x: x.lower(), output=True):
    # since we want to output sorted alphabetically we can use a sorted map
    sorted_map = SortedMap(sorting_function=sorting_key)

    if output:
      print('CURRENT EXPRESSION:')
      print('***************************************')

    # print the independent ones first
    for var, dask_obj in hash_table.items():
      if dask_obj.independent:
        sorted_map[var] = dask_obj

    # iteratively calcuate
    sorted_graph = list(nx.topological_sort(topological_graph))
    for var in sorted_graph:
      dask_obj = hash_table[var]
      if dask_obj == None:
        # skip the ones that dont exist
        continue

      if dask_obj.independent:
        # skip independent ones
        continue

      # calcuate value
      tree = parser.buildParseTree(dask_obj.expression)
      value = parser.evaluate(tree, hash_table)

      # Update the dask thingy
      dask_obj.value = value
      hash_table[var] = dask_obj

      # add to sorted map
      sorted_map[var] = dask_obj

    # output all
    if output:
      for var, dask_obj in sorted_map.items():
        print(f'{var}={dask_obj}')
    return sorted_map

#################################
# Main Loop
#################################
choice = input("Enter choice: ")
while choice != '6':
  # Expression Storing/Modify
  if choice == '1':
    print("Enter the DASK expression you want to add/modify:")
    print("For example: a=(1+2)\n")
    DASK = input()
    key , exp = DASK.strip().split('=', 1)
    add_dask_expresssion(key, exp)

  # evaluuation
  elif choice == '2':
    show_dask_expressions(hash_table, topological_graph)

  # evaluate single expression from hash
  elif choice == '3':
    print("Enter the variable you want to evaluate:")
    var = input().strip()
    dask_obj = hash_table[var]

    if dask_obj == None:
      print(f'Variable {var} does not exist!')
    else:
      tree = parser.buildParseTree(dask_obj.expression)
      value = parser.evaluate(tree, hash_table)

      print('\nExpression Tree (Inorder):')
      tree.print_tree_inorder()
      print(f'Value of variable "{var}" is {value}')

  # read from file and add dask to table
  elif choice == '4':
    filename = input("Please enter input file: ")
    with open(filename, 'r') as f:
      lines = f.readlines()

      for line in lines:
        key , exp = line.strip().split('=', 1)
        add_dask_expresssion(key, exp)

    f.close()
    
    # print current expressions
    show_dask_expressions(hash_table, topological_graph)

  # sort expressions based on result values
  elif choice == '5':
    filename = input("Please enter output file: ")
    sorted_map = show_dask_expressions(hash_table, topological_graph, sorting_key=lambda x: -hash_table[x].value if hash_table[x].value != None else float('inf'), output=False)
    with open(filename, 'w') as f:
      prev = float('-inf')
      for var, dask_obj in sorted_map.items():
        if dask_obj.value != prev:
          f.write(f'\n*** Expressions with value => {dask_obj.value}\n')
          prev = dask_obj.value

        f.write(f'{var}={''.join(dask_obj.expression)}\n')
    f.close()

    print('>>>Sorting of DASK expressions completed!')


  # re-input
  print('\n'*3)
  input('Press enter key, to continue... ')
  print(menu_msg)
  choice = input("Enter choice: ")
  