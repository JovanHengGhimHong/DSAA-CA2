import os
import networkx as nx
from structures.DASK_ParseTree import DASK_ParseTree
from structures.SortedMap import SortedMap
from structures.HashTable import HashTable, Dask
from src.get_dask_data import get_dask_data
from src.build_html import build_html
from src.clear import clear
from src.validators import input_file_path, dask_input, yes_no_input
from src.dependency_analyzer import print_dependency_analysis, print_reverse_dependency_query


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
  Please select your choice ('1' , '2', '3' , '4' , '5' , '6', '7', '8', '9', '10'):
    1. Add/Modify DASK Expressions
    2. Display current DASK expressions
    3. Evaluate a single DASK variable
    4. Read DASK expressions from file
    5. Sort DASK expressions
    6. DASK Report - Jovan
    7. Temp DASK Variable Visualizer - Jovan
    8. Analyze dependencies & detect circular references
    9. Reverse dependency query
    10. Exit
'''
print(start_msg)
print(menu_msg)

# We always create a parse tree object and hash table to store variables
parser = DASK_ParseTree()
hash_table = HashTable(100)
topological_graph = nx.DiGraph()

def add_dask_expresssion(key, exp):
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
while choice != '10':
  # Expression Storing/Modify
  if choice == '1':
    print("Enter the DASK expression you want to add/modify:")
    print("For example: a=(1+2)\n")
    key, exp = dask_input("Enter DASK expression: ")
    add_dask_expresssion(key, exp)

  # evaluuation
  elif choice == '2':
    show_dask_expressions(hash_table, topological_graph)

  # evaluate single expression from hash
  elif choice == '3':
    print("Enter the variable you want to evaluate:")
    var = input().strip()
    dask_obj = hash_table[var]

    # validate proper variable
    while dask_obj == None:
      print(f'Variable {var} does not exist!')
      print('Please enter another variable: \n')
      var = input().strip()
      dask_obj = hash_table[var]

    tree = parser.buildParseTree(dask_obj.expression)
    value = parser.evaluate(tree, hash_table)

    print('\nExpression Tree (Inorder):')
    tree.print_tree_inorder()
    print(f'Value of variable "{var}" is {value}')

  # read from file and add dask to table
  elif choice == '4':
    filename = input_file_path("Please enter input file: ")

    with open(filename, 'r') as f:
      lines = f.readlines()

      for line in lines:
        key , exp = line.strip().split('=', 1)

        # skip invalid expressions
        if not parser.verify_expression(exp):
          print(f'Invalid DASK for {key} = {exp}. Skipping...')
          continue

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

        exp_str = ''.join(dask_obj.expression)
        f.write(f'{var}={exp_str}\n')
    f.close()

    print('>>>Sorting of DASK expressions completed!')

  # Jovan - DASK Report
  elif choice == '6':
    output_path = input("Please enter output HTML file path: ")

    while output_path.strip() == '' or not output_path.lower().endswith('.html'):
      print('That is not a valid HTMl path. Please try again!\n')
      output_path = input("Please enter output HTML file path: ")
            
    # get data
    data = get_dask_data(topological_graph, show_dask_expressions(hash_table, topological_graph, output=False), parser.buildParseTree)

    # build html
    build_html(data, output_path)

    print(f'DASK Report generated successfully at {output_path}!')

    # query open
    open_query = yes_no_input('Do you want to open the report now? (y/n): ')

    if open_query.lower() == 'y':
      os.startfile(output_path)

  # Jovan - Temp DASK Variable Visualizer
  elif choice == '7':
    clear()
    show_dask_expressions(hash_table, topological_graph)
    print('\nPlease enter expressions to visualize DASK Variables (q to quit):')
    expression = 0
    pending_keys = []

    while expression != 'q':
      key , expression = dask_input("Enter DASK expression: ", allow_quit=True)
      
      # add dask 'temp'
      pending_keys.append(key)
      add_dask_expresssion(key, expression)
      clear()


      # custom print
      sorted_map = show_dask_expressions(hash_table, topological_graph, output=False)
      for var, dask_obj in sorted_map.items():
        if var in pending_keys:
          print(f'***{var}={dask_obj}***')
        else:
          print(f'{var}={dask_obj}')

      # reprompt
      print('\nPlease enter expressions to visualize DASK Variables (q to quit):')
      key, expression = dask_input("Enter DASK expression: ", allow_quit=True)

    # show 'pending' expressions to add
    if len(pending_keys) > 0:
      print('\nThe following expressions were not added:')
      print('***********************************************')
      for pk in pending_keys:
        dask_obj = hash_table[pk]
        print(f'{pk}={dask_obj}')

      add_expressions = yes_no_input('Do you want to add these expressions? (y/n): ')

      if add_expressions.lower() == 'n':
        # remove since theyre alr stored
        for pk in pending_keys:
          del hash_table[pk]

          # handle graph edges 
          if pk in topological_graph:
            topological_graph.remove_node(pk)

    clear()

  # Dependency Analysis & Circular Reference Detection
  elif choice == '8':
    if len(list(hash_table.items())) == 0:
      print("No DASK expressions loaded. Please add expressions first.")
    else:
      print_dependency_analysis(hash_table)

  # Reverse Dependency Query
  elif choice == '9':
    if len(list(hash_table.items())) == 0:
      print("No DASK expressions loaded. Please add expressions first.")
    else:
      print("Enter the variable you want to query:")
      print("(This will show which variables depend on it)\n")
      query_var = input("Variable name: ").strip()
      
      while not query_var:
        print("Please enter a valid variable name.")
        query_var = input("Variable name: ").strip()
      
      print_reverse_dependency_query(hash_table, query_var)
    
  # invalid
  else:
    print('That is not a valid choice. Please try again.')

  # re-input
  input('Press enter key, to continue... ')
  print(menu_msg)
  choice = input("Enter choice: ")
  
