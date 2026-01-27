"""
Dependency Analyzer Module for DASK Expression Evaluator

This module provides dependency graph construction and circular dependency detection
using DFS with coloring algorithm.

Time Complexity:
- Building graph: O(V + E) where V = number of variables, E = number of dependencies
- Cycle detection: O(V + E) using DFS

Space Complexity: O(V + E) for storing the adjacency list
"""


class DependencyGraph:
    """
    Represents a directed graph of variable dependencies.
    
    Uses an adjacency list representation where:
    - Node = variable name (e.g., "Alpha")
    - Edge Alpha -> Beta means Alpha's expression depends on Beta
    """
    
    # DFS states for cycle detection
    UNVISITED = 0
    VISITING = 1  # Currently in recursion stack
    DONE = 2
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        self.graph = {}  # adjacency list: variable -> set of dependencies
        self.defined_variables = set()  # variables that have been defined
        
    def add_variable(self, variable_name, dependencies):
        """
        Add a variable and its dependencies to the graph.
        
        Args:
            variable_name: The name of the variable being defined
            dependencies: Set/list of variable names this variable depends on
        """
        self.defined_variables.add(variable_name)
        self.graph[variable_name] = set(dependencies)
        
        # Ensure all dependency nodes exist in graph (even if not defined)
        for dep in dependencies:
            if dep not in self.graph:
                self.graph[dep] = set()
    
    def get_undefined_variables(self):
        """
        Find variables that are referenced but never defined.
        
        Returns:
            Set of undefined variable names
        """
        all_referenced = set()
        for deps in self.graph.values():
            all_referenced.update(deps)
        
        return all_referenced - self.defined_variables
    
    def detect_cycles(self):
        """
        Detect all cycles in the dependency graph using DFS with coloring.
        
        Algorithm:
        - UNVISITED (0): Node not yet visited
        - VISITING (1): Node is in current recursion stack (potential cycle)
        - DONE (2): Node fully processed
        
        Returns:
            Tuple of (variables_in_cycles: set, cycle_paths: list of lists)
        """
        state = {node: self.UNVISITED for node in self.graph}
        parent = {}  # To reconstruct cycle paths
        variables_in_cycles = set()
        cycle_paths = []
        
        def dfs(node, path):
            """
            DFS traversal with cycle detection.
            
            Args:
                node: Current node being visited
                path: Current path from root to this node
            """
            state[node] = self.VISITING
            
            for neighbor in self.graph.get(node, set()):
                if neighbor not in state:
                    # Node referenced but not in our graph (undefined)
                    continue
                    
                if state[neighbor] == self.VISITING:
                    # Cycle detected! neighbor is in our current recursion stack
                    cycle = self._reconstruct_cycle(path, node, neighbor)
                    cycle_paths.append(cycle)
                    variables_in_cycles.update(cycle)
                    
                elif state[neighbor] == self.UNVISITED:
                    parent[neighbor] = node
                    dfs(neighbor, path + [neighbor])
            
            state[node] = self.DONE
        
        # Run DFS from each unvisited node
        for node in self.graph:
            if state[node] == self.UNVISITED:
                parent[node] = None
                dfs(node, [node])
        
        return variables_in_cycles, cycle_paths
    
    def _reconstruct_cycle(self, path, current_node, cycle_start):
        """
        Reconstruct the cycle path when a back edge is detected.
        
        Args:
            path: Current DFS path
            current_node: Node where we detected the back edge from
            cycle_start: Node where the cycle begins (already in VISITING state)
            
        Returns:
            List representing the cycle path (e.g., ['Alpha', 'Beta', 'Alpha'])
        """
        # Find where cycle_start appears in the path
        try:
            start_idx = path.index(cycle_start)
            cycle = path[start_idx:] + [cycle_start]
            return cycle
        except ValueError:
            # Fallback if cycle_start not in path (shouldn't happen)
            return [cycle_start, current_node, cycle_start]
    
    def get_dependencies(self, variable):
        """
        Get direct dependencies of a variable.
        
        Args:
            variable: Variable name to query
            
        Returns:
            Set of variable names this variable depends on
        """
        return self.graph.get(variable, set())
    
    def get_all_variables(self):
        """
        Get all variables in the graph (both defined and undefined).
        
        Returns:
            Set of all variable names
        """
        return set(self.graph.keys())


def extract_dependencies_from_tokens(tokens):
    """
    Extract variable dependencies from a list of tokens.
    
    A token is considered a variable if it consists only of alphabetic characters.
    
    Args:
        tokens: List of expression tokens from the tokenizer
        
    Returns:
        Set of variable names that the expression depends on
    """
    dependencies = set()
    for token in tokens:
        # Variables are purely alphabetic (not operators, numbers, or parentheses)
        if token.isalpha():
            dependencies.add(token)
    return dependencies


def build_dependency_graph(hash_table):
    """
    Build a dependency graph from the hash table of DASK expressions.
    
    Args:
        hash_table: HashTable containing variable -> Dask object mappings
        
    Returns:
        DependencyGraph object representing all dependencies
    """
    graph = DependencyGraph()
    
    for variable, dask_obj in hash_table.items():
        if dask_obj is not None:
            # Extract dependencies from the expression tokens
            dependencies = extract_dependencies_from_tokens(dask_obj.expression)
            
            # Remove self-reference if any (a variable shouldn't depend on itself directly)
            dependencies.discard(variable)
            
            graph.add_variable(variable, dependencies)
    
    return graph


def analyze_dependencies(hash_table):
    """
    Perform full dependency analysis on the DASK expressions.
    
    This function:
    1. Builds a dependency graph from the hash table
    2. Lists all variables and their dependencies
    3. Detects undefined variables
    4. Detects and reports circular dependencies
    
    Args:
        hash_table: HashTable containing variable -> Dask object mappings
        
    Returns:
        Dictionary containing analysis results:
        {
            'graph': DependencyGraph object,
            'undefined': set of undefined variables,
            'cycles': list of cycle paths,
            'variables_in_cycles': set of variables involved in cycles
        }
    """
    # Build the dependency graph
    graph = build_dependency_graph(hash_table)
    
    # Find undefined variables
    undefined = graph.get_undefined_variables()
    
    # Detect cycles
    variables_in_cycles, cycle_paths = graph.detect_cycles()
    
    return {
        'graph': graph,
        'undefined': undefined,
        'cycles': cycle_paths,
        'variables_in_cycles': variables_in_cycles
    }


def print_dependency_analysis(hash_table):
    """
    Print a formatted dependency analysis report.
    
    Args:
        hash_table: HashTable containing variable -> Dask object mappings
    """
    print("\n" + "=" * 60)
    print("       DEPENDENCY ANALYSIS & CIRCULAR REFERENCE DETECTION")
    print("=" * 60)
    
    # Perform analysis
    results = analyze_dependencies(hash_table)
    graph = results['graph']
    undefined = results['undefined']
    cycle_paths = results['cycles']
    variables_in_cycles = results['variables_in_cycles']
    
    # Print dependencies for each defined variable
    print("\n--- Variable Dependencies ---")
    defined_vars = sorted(graph.defined_variables, key=str.lower)
    
    if not defined_vars:
        print("No variables defined.")
    else:
        for var in defined_vars:
            deps = graph.get_dependencies(var)
            if deps:
                deps_str = ", ".join(sorted(deps, key=str.lower))
                print(f"  {var} depends on: {deps_str}")
            else:
                print(f"  {var} depends on: (none - independent)")
    
    # Print undefined variables
    print("\n--- Undefined Variables Referenced ---")
    if undefined:
        undefined_str = ", ".join(sorted(undefined, key=str.lower))
        print(f"  Warning! Undefined variables: {undefined_str}")
    else:
        print("  All referenced variables are defined. ✓")
    
    # Print cycle analysis
    print("\n--- Circular Dependency Detection ---")
    if cycle_paths:
        print(f"  ⚠ Found {len(cycle_paths)} cycle(s)!")
        print(f"  Variables involved in cycles: {', '.join(sorted(variables_in_cycles, key=str.lower))}")
        print("\n  Cycle paths detected:")
        for i, cycle in enumerate(cycle_paths, 1):
            cycle_str = " -> ".join(cycle)
            print(f"    {i}. {cycle_str}")
    else:
        print("  No circular dependencies detected. ✓")
    
    print("\n" + "=" * 60)
    
    # Summary
    total_vars = len(defined_vars)
    total_undefined = len(undefined)
    total_cycles = len(cycle_paths)
    total_vars_in_cycles = len(variables_in_cycles)
    
    print(f"Summary: {total_vars} variables defined, "
          f"{total_undefined} undefined references, "
          f"{total_cycles} cycles detected, "
          f"{total_vars_in_cycles} variables involved in cycles")
    print("=" * 60 + "\n")
    
    return results


class ReverseDependencyGraph:
    """
    Represents the reverse dependency graph (transpose of the dependency graph).
    
    In this graph:
    - Edge A -> B means "A is used by B" (B depends on A)
    - This allows answering: "Which variables depend on X?"
    
    Time Complexity:
    - Building reverse graph: O(V + E)
    - Finding direct dependents: O(1) average
    - Finding all dependents (transitive): O(V + E) using BFS/DFS
    """
    
    def __init__(self):
        """Initialize an empty reverse dependency graph."""
        self.reverse_graph = {}  # variable -> set of variables that depend on it
        self.all_variables = set()
    
    def build_from_dependency_graph(self, dep_graph):
        """
        Build the reverse graph from a DependencyGraph.
        
        Args:
            dep_graph: DependencyGraph object
        """
        self.all_variables = dep_graph.defined_variables.copy()
        
        # Initialize all nodes
        for var in self.all_variables:
            self.reverse_graph[var] = set()
        
        # Reverse the edges
        for var in dep_graph.defined_variables:
            for dependency in dep_graph.get_dependencies(var):
                if dependency not in self.reverse_graph:
                    self.reverse_graph[dependency] = set()
                # dependency is used by var
                self.reverse_graph[dependency].add(var)
    
    def get_direct_dependents(self, variable):
        """
        Get variables that directly depend on the given variable.
        
        Args:
            variable: Variable name to query
            
        Returns:
            Set of variable names that directly use this variable
        """
        return self.reverse_graph.get(variable, set())
    
    def get_all_dependents(self, variable):
        """
        Get all variables that depend on the given variable (transitive closure).
        Uses BFS to find all downstream dependents.
        
        Args:
            variable: Variable name to query
            
        Returns:
            Tuple of (all_dependents: set, dependency_levels: dict)
            where dependency_levels maps variable -> distance from source
        """
        if variable not in self.reverse_graph:
            return set(), {}
        
        visited = set()
        levels = {}  # variable -> level (distance from source)
        queue = [(variable, 0)]
        
        while queue:
            current, level = queue.pop(0)
            
            for dependent in self.reverse_graph.get(current, set()):
                if dependent not in visited:
                    visited.add(dependent)
                    levels[dependent] = level + 1
                    queue.append((dependent, level + 1))
        
        return visited, levels


def build_reverse_dependency_graph(hash_table):
    """
    Build a reverse dependency graph from the hash table.
    
    Args:
        hash_table: HashTable containing variable -> Dask object mappings
        
    Returns:
        ReverseDependencyGraph object
    """
    # First build the forward dependency graph
    dep_graph = build_dependency_graph(hash_table)
    
    # Build and return the reverse graph
    reverse_graph = ReverseDependencyGraph()
    reverse_graph.build_from_dependency_graph(dep_graph)
    
    return reverse_graph, dep_graph


def print_reverse_dependency_query(hash_table, query_variable):
    """
    Print a formatted reverse dependency query report.
    Shows which variables depend on the queried variable.
    
    Args:
        hash_table: HashTable containing variable -> Dask object mappings
        query_variable: The variable to query dependents for
        
    Returns:
        Dictionary with query results
    """
    print("\n" + "=" * 60)
    print("              REVERSE DEPENDENCY QUERY")
    print("=" * 60)
    print(f"\n  Query: Which variables depend on '{query_variable}'?")
    print("-" * 60)
    
    # Build the reverse dependency graph
    reverse_graph, forward_graph = build_reverse_dependency_graph(hash_table)
    
    # Check if variable exists
    if query_variable not in forward_graph.defined_variables:
        if query_variable in forward_graph.get_all_variables():
            print(f"\n  ⚠ '{query_variable}' is referenced but not defined.")
        else:
            print(f"\n  ✗ Variable '{query_variable}' not found in expressions.")
        print("=" * 60 + "\n")
        return {'found': False, 'direct': set(), 'all': set()}
    
    # Get direct dependents
    direct_dependents = reverse_graph.get_direct_dependents(query_variable)
    
    # Get all transitive dependents
    all_dependents, levels = reverse_graph.get_all_dependents(query_variable)
    
    # Print direct dependents
    print("\n--- Direct Dependents (Level 1) ---")
    if direct_dependents:
        for dep in sorted(direct_dependents, key=str.lower):
            dask_obj = hash_table[dep]
            exp_str = ''.join(dask_obj.expression) if dask_obj else "?"
            print(f"  • {dep} = {exp_str}")
    else:
        print(f"  No variables directly depend on '{query_variable}'.")
        print(f"  ('{query_variable}' is a leaf variable - not used by others)")
    
    # Print transitive dependents by level
    if all_dependents - direct_dependents:
        print("\n--- Indirect Dependents (Level 2+) ---")
        
        # Group by level
        max_level = max(levels.values()) if levels else 0
        for lvl in range(2, max_level + 1):
            vars_at_level = [v for v, l in levels.items() if l == lvl]
            if vars_at_level:
                print(f"  Level {lvl}:")
                for dep in sorted(vars_at_level, key=str.lower):
                    dask_obj = hash_table[dep]
                    exp_str = ''.join(dask_obj.expression) if dask_obj else "?"
                    print(f"    • {dep} = {exp_str}")
    
    # Impact summary
    print("\n--- Impact Summary ---")
    total_affected = len(all_dependents)
    print(f"  If '{query_variable}' changes:")
    if total_affected > 0:
        print(f"    → {total_affected} variable(s) would be affected")
        print(f"    → Affected: {', '.join(sorted(all_dependents, key=str.lower))}")
    else:
        print(f"    → No other variables would be affected")
    
    print("\n" + "=" * 60 + "\n")
    
    return {
        'found': True,
        'direct': direct_dependents,
        'all': all_dependents,
        'levels': levels
    }
