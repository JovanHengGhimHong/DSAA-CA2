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
    6. Exit
'''
print(start_msg)
print(menu_msg)

# We always create a parse tree object and hash table to store variables
parser = DASK_ParseTree()
hash_table = HashTable(100)

# Main Loop
choice = input("Enter choice: ")
while choice != '6':
  # Expression Storing/Modify
  if choice == '1':
    print("Enter the DASK expression you want to add/modify:")
    print("For example: a=(1+2)\n")
    DASK = input()
    key , exp = DASK.strip().split('=', 1)

    # Parse tree build and evaluate
    hash_table[key] = Dask(key , exp, None)

  # evaluuation
  elif choice == '2':

    pass
  print(choice)

  # re-input
  print(menu_msg)
  choice = input("Enter choice: ")
  