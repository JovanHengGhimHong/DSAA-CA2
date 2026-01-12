from src.tree_to_json import tree_to_json

def get_dask_data(topological_graph, sorted_map, tree_builder):
    data = {}
    # we get the graph edges
    data['edges'] = list(topological_graph.edges)

    # we get all the nodes
    # we have to derive from graph_edges to due with 'undefined' nodes that are not saved in hash table
    nodes = {i for edge in data['edges'] for i in edge} # set 
    data['nodes'] = list(nodes)

    # we get all the parse trees and each expressions' data
    parse_trees = {}
    meta_data = {}
    for key, dask_obj in sorted_map.items():
      # parse tree
      tree = tree_builder(dask_obj.expression)
      json_tree = tree_to_json(tree)

      parse_trees[key] = json_tree
      meta_data[key] = {
        'expr': ' '.join(dask_obj.expression),
        'value': dask_obj.value if dask_obj.value != None else 'N/A',
      }


    data['parseTrees'] = parse_trees
    data['meta'] = meta_data

    return data