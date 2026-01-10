import networkx as nx
from structures.DASK_ParseTree import DASK_ParseTree
from structures.HashTable import HashTable, Dask

start_msg = '''
*******************************************************************************
*                                                                             *
*                   ST1507 DSAA: DASK Expression Evaluator!                   *
*-----------------------------------------------------------------------------*
*     - Author: Jovan Heng (2401418) & Joen Choo (-)                          *
*     - Class: DAAA 2A 22                                                     *
*                                                                             *
*******************************************************************************
'''
menu_msg = '''
  Please select your choice ('1' , '2', '3' , '4' , '5' , '6'):
    1. Add/Modify DASK Expressions
    2. Display current DASK expressions
    6. Exit
'''
print(start_msg)
print(menu_msg)

# We always create a parse tree object and hash table to store variables
parser = DASK_ParseTree()
hash_table = HashTable(100)
topological_graph = nx.DiGraph()

# Main Loop
choice = input("Enter choice: ")
while choice != '6':
  # Expression Storing/Modify
  if choice == '1':
    print("Enter the DASK expression you want to add/modify:")
    print("For example: a=(1+2)\n")
    DASK = input()
    key , exp = DASK.strip().split('=', 1)
    tokens = parser.tokenizer(exp)

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

  # evaluuation
  elif choice == '2':
    print('CURRENT EXPRESSION:')
    print('***************************************')

    # print the independent ones first
    for var, dask_obj in hash_table.items():
      if dask_obj.independent:
        print(f'{var}={dask_obj}')

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

      print(f'{var}={dask_obj}')


  # re-input
  print('\n'*3)
  input('Press enter key, to continue... ')
  print(menu_msg)
  choice = input("Enter choice: ")
  