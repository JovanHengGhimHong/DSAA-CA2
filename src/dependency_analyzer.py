"""
Dependency Analyzer Module for DASK Expression Evaluator

This module provides comprehensive dependency analysis including:
- Dependency graph construction (adjacency list representation)
- Circular dependency detection using DFS with vertex coloring
- Reverse dependency queries using graph transpose and BFS

================================================================================
COMPLEXITY ANALYSIS
================================================================================
Let V = number of variables, E = number of dependency edges

| Operation                    | Time Complexity | Space Complexity |
|------------------------------|-----------------|------------------|
| Build dependency graph       | O(V + E)        | O(V + E)         |
| Build reverse graph          | O(V + E)        | O(V + E)         |
| Detect cycles (DFS)          | O(V + E)        | O(V)             |
| Find undefined variables     | O(E)            | O(V)             |
| Get direct dependents        | O(1) average    | O(1)             |
| Get all dependents (BFS)     | O(V + E)        | O(V)             |
| Full analysis                | O(V + E)        | O(V + E)         |
================================================================================
"""


class DependencyAnalyzer:
    """
    Unified dependency analyzer that provides both forward and reverse
    dependency analysis with cycle detection.
    
    This class encapsulates:
    - Forward dependency graph (what does X depend on?)
    - Reverse dependency graph (what depends on X?)
    - Cycle detection using DFS coloring algorithm
    - Undefined variable detection
    
    Design Pattern: Facade - provides a simplified interface to the
    complex subsystem of graph operations.
    """
    
    # DFS vertex states for cycle detection
    UNVISITED = 0
    VISITING = 1   # In current recursion stack (gray)
    VISITED = 2    # Fully processed (black)
    
    def __init__(self, hash_table):
        """
        Initialize the analyzer and build both dependency graphs.
        
        Args:
            hash_table: HashTable containing variable -> Dask object mappings
            
        Time Complexity: O(V + E) for building both graphs
        Space Complexity: O(V + E) for storing adjacency lists
        """
        self._hash_table = hash_table
        self._defined_variables = set()
        
        # Forward graph: variable -> set of variables it depends on
        self._forward_graph = {}
        
        # Reverse graph: variable -> set of variables that depend on it
        self._reverse_graph = {}
        
        # Analysis results (computed lazily)
        self._undefined_vars = None
        self._cycles = None
        self._vars_in_cycles = None
        
        # Build the graphs
        self._build_graphs()
    
    # ==========================================================================
    # GRAPH CONSTRUCTION
    # ==========================================================================
    
    def _build_graphs(self):
        """
        Build both forward and reverse dependency graphs from the hash table.
        
        Time Complexity: O(V + E)
        Space Complexity: O(V + E)
        """
        # First pass: build forward graph and collect defined variables
        for variable, dask_obj in self._hash_table.items():
            if dask_obj is not None:
                dependencies = self._extract_dependencies(dask_obj.expression)
                dependencies.discard(variable)  # Remove self-reference
                
                self._defined_variables.add(variable)
                self._forward_graph[variable] = dependencies
                
                # Ensure all referenced variables exist in graph
                for dep in dependencies:
                    if dep not in self._forward_graph:
                        self._forward_graph[dep] = set()
        
        # Second pass: build reverse graph (transpose)
        for var in self._forward_graph:
            self._reverse_graph[var] = set()
        
        for var, deps in self._forward_graph.items():
            for dep in deps:
                if dep not in self._reverse_graph:
                    self._reverse_graph[dep] = set()
                self._reverse_graph[dep].add(var)
    
    @staticmethod
    def _extract_dependencies(tokens):
        """
        Extract variable dependencies from expression tokens.
        
        A token is a variable if it consists only of alphabetic characters.
        
        Args:
            tokens: List of expression tokens
            
        Returns:
            Set of variable names
            
        Time Complexity: O(n) where n = number of tokens
        """
        return {token for token in tokens if token.isalpha()}
    
    # ==========================================================================
    # FORWARD DEPENDENCY QUERIES
    # ==========================================================================
    
    def get_dependencies(self, variable):
        """
        Get the direct dependencies of a variable (what it depends on).
        
        Args:
            variable: Variable name to query
            
        Returns:
            Set of variable names, or empty set if not found
            
        Time Complexity: O(1) average
        """
        return self._forward_graph.get(variable, set()).copy()
    
    def get_all_dependencies(self, variable):
        """
        Get all dependencies of a variable (transitive closure).
        Uses BFS to traverse the dependency chain.
        
        Args:
            variable: Variable name to query
            
        Returns:
            Set of all variables this variable depends on (directly or indirectly)
            
        Time Complexity: O(V + E)
        """
        if variable not in self._forward_graph:
            return set()
        
        visited = set()
        queue = list(self._forward_graph.get(variable, set()))
        
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                queue.extend(self._forward_graph.get(current, set()) - visited)
        
        return visited
    
    # ==========================================================================
    # REVERSE DEPENDENCY QUERIES
    # ==========================================================================
    
    def get_dependents(self, variable):
        """
        Get direct dependents of a variable (what depends on it).
        
        Args:
            variable: Variable name to query
            
        Returns:
            Set of variable names that directly depend on this variable
            
        Time Complexity: O(1) average
        """
        return self._reverse_graph.get(variable, set()).copy()
    
    def get_all_dependents(self, variable):
        """
        Get all dependents of a variable with their distances (BFS).
        
        Args:
            variable: Variable name to query
            
        Returns:
            Tuple of (all_dependents: set, levels: dict mapping var -> distance)
            
        Time Complexity: O(V + E)
        Space Complexity: O(V)
        """
        if variable not in self._reverse_graph:
            return set(), {}
        
        visited = set()
        levels = {}
        queue = [(variable, 0)]
        
        while queue:
            current, level = queue.pop(0)
            
            for dependent in self._reverse_graph.get(current, set()):
                if dependent not in visited:
                    visited.add(dependent)
                    levels[dependent] = level + 1
                    queue.append((dependent, level + 1))
        
        return visited, levels
    
    # ==========================================================================
    # CYCLE DETECTION (DFS with Coloring)
    # ==========================================================================
    
    def detect_cycles(self):
        """
        Detect all cycles in the dependency graph using DFS with vertex coloring.
        
        Algorithm:
        - White (UNVISITED): Not yet visited
        - Gray (VISITING): Currently in recursion stack
        - Black (VISITED): Fully processed
        
        A back edge to a gray vertex indicates a cycle.
        
        Returns:
            Tuple of (variables_in_cycles: set, cycle_paths: list of lists)
            
        Time Complexity: O(V + E)
        Space Complexity: O(V) for state tracking
        """
        if self._cycles is not None:
            return self._vars_in_cycles, self._cycles
        
        state = {node: self.UNVISITED for node in self._forward_graph}
        self._vars_in_cycles = set()
        self._cycles = []
        
        def dfs(node, path):
            """DFS with cycle detection and path tracking."""
            state[node] = self.VISITING
            
            for neighbor in self._forward_graph.get(node, set()):
                if neighbor not in state:
                    continue  # Undefined variable
                
                if state[neighbor] == self.VISITING:
                    # Back edge found - cycle detected!
                    cycle = self._reconstruct_cycle(path, neighbor)
                    self._cycles.append(cycle)
                    self._vars_in_cycles.update(cycle[:-1])  # Exclude duplicate end
                    
                elif state[neighbor] == self.UNVISITED:
                    dfs(neighbor, path + [neighbor])
            
            state[node] = self.VISITED
        
        # Run DFS from each unvisited node
        for node in self._forward_graph:
            if state[node] == self.UNVISITED:
                dfs(node, [node])
        
        return self._vars_in_cycles, self._cycles
    
    def _reconstruct_cycle(self, path, cycle_start):
        """
        Reconstruct cycle path from DFS traversal.
        
        Args:
            path: Current DFS path
            cycle_start: Node where cycle begins
            
        Returns:
            List representing the cycle (e.g., ['A', 'B', 'C', 'A'])
        """
        try:
            start_idx = path.index(cycle_start)
            return path[start_idx:] + [cycle_start]
        except ValueError:
            return [cycle_start, path[-1], cycle_start]
    
    # ==========================================================================
    # UNDEFINED VARIABLE DETECTION
    # ==========================================================================
    
    def get_undefined_variables(self):
        """
        Find variables that are referenced but never defined.
        
        Returns:
            Set of undefined variable names
            
        Time Complexity: O(E) to scan all edges
        """
        if self._undefined_vars is not None:
            return self._undefined_vars
        
        all_referenced = set()
        for deps in self._forward_graph.values():
            all_referenced.update(deps)
        
        self._undefined_vars = all_referenced - self._defined_variables
        return self._undefined_vars
    
    # ==========================================================================
    # ACCESSOR METHODS
    # ==========================================================================
    
    def get_defined_variables(self):
        """
        Get set of all defined variable names.
        
        Returns:
            Set of defined variable names
        """
        return self._defined_variables.copy()
    
    def get_total_variables(self):
        """
        Get total number of defined variables.
        
        Returns:
            Integer count of defined variables
        """
        return len(self._defined_variables)
    
    def get_total_edges(self):
        """
        Get total number of dependency edges.
        
        Returns:
            Integer count of edges in the dependency graph
        """
        return sum(len(deps) for deps in self._forward_graph.values())
    
    def has_cycles(self):
        """
        Check if the dependency graph has any cycles.
        
        Returns:
            Boolean - True if cycles exist
        """
        _, cycles = self.detect_cycles()
        return len(cycles) > 0
    
    def has_undefined(self):
        """
        Check if there are any undefined variable references.
        
        Returns:
            Boolean - True if undefined references exist
        """
        return len(self.get_undefined_variables()) > 0
    
    def variable_exists(self, variable):
        """Check if a variable is defined."""
        return variable in self._defined_variables
    
    def variable_is_referenced(self, variable):
        """Check if a variable is referenced anywhere."""
        return variable in self._forward_graph
    
    # ==========================================================================
    # EXPRESSION HELPERS
    # ==========================================================================
    
    def get_expression_string(self, variable):
        """Get the expression string for a variable."""
        dask_obj = self._hash_table[variable]
        if dask_obj:
            return ''.join(dask_obj.expression)
        return "?"


class DependencyAnalyzerUI:
    """
    User interface for the Dependency Analyzer.
    
    Provides an interactive menu system for exploring dependencies,
    detecting cycles, and querying reverse dependencies.
    
    Design Pattern: Facade + Template Method
    """
    
    SUBMENU = """
    +==============================================================+
    |             DEPENDENCY ANALYZER - SUB MENU                   |
    +==============================================================+
    |  1. View all variable dependencies                           |
    |  2. Detect circular references (cycles)                      |
    |  3. Check for undefined variables                            |
    |  4. Query: What does variable X depend on?                   |
    |  5. Query: What depends on variable X? (reverse)             |
    |  6. Full analysis report                                     |
    |  7. Return to main menu                                      |
    +==============================================================+
    """
    
    def __init__(self, hash_table):
        """
        Initialize the UI with a hash table.
        
        Args:
            hash_table: HashTable containing DASK expressions
        """
        self._hash_table = hash_table
        self._analyzer = None
    
    def run(self):
        """
        Run the interactive dependency analyzer submenu.
        
        Returns when user selects option 7 (return to main menu).
        """
        # Build analyzer (lazy initialization)
        self._analyzer = DependencyAnalyzer(self._hash_table)
        
        self._print_header()
        
        while True:
            print(self.SUBMENU)
            choice = input("    Enter choice (1-7): ").strip()
            
            if choice == '1':
                self._show_all_dependencies()
            elif choice == '2':
                self._show_cycle_detection()
            elif choice == '3':
                self._show_undefined_variables()
            elif choice == '4':
                self._query_forward_dependencies()
            elif choice == '5':
                self._query_reverse_dependencies()
            elif choice == '6':
                self._show_full_report()
            elif choice == '7':
                print("\n    Returning to main menu...\n")
                break
            else:
                print("\n    Invalid choice. Please enter 1-7.\n")
            
            input("\n    Press Enter to continue...")
    
    def _print_header(self):
        """Print the analyzer header with stats."""
        print("\n" + "=" * 64)
        print("           DEPENDENCY ANALYZER & CYCLE DETECTOR")
        print("=" * 64)
        print(f"    Variables loaded: {self._analyzer.get_total_variables()}")
        print(f"    Dependency edges: {self._analyzer.get_total_edges()}")
        print("=" * 64)
    
    def _print_section(self, title):
        """Print a section header."""
        print(f"\n    {'-' * 56}")
        print(f"    {title}")
        print(f"    {'-' * 56}")
    
    # ==========================================================================
    # MENU OPTIONS
    # ==========================================================================
    
    def _show_all_dependencies(self):
        """Option 1: Show all variable dependencies."""
        self._print_section("ALL VARIABLE DEPENDENCIES")
        
        defined_vars = sorted(self._analyzer.get_defined_variables(), key=str.lower)
        
        if not defined_vars:
            print("    No variables defined.")
            return
        
        for var in defined_vars:
            deps = self._analyzer.get_dependencies(var)
            exp_str = self._analyzer.get_expression_string(var)
            
            if deps:
                deps_str = ", ".join(sorted(deps, key=str.lower))
                print(f"    {var} = {exp_str}")
                print(f"        --> depends on: {deps_str}")
            else:
                print(f"    {var} = {exp_str}")
                print(f"        --> (independent - no dependencies)")
    
    def _show_cycle_detection(self):
        """Option 2: Detect and display circular references."""
        self._print_section("CIRCULAR DEPENDENCY DETECTION")
        
        vars_in_cycles, cycles = self._analyzer.detect_cycles()
        
        if not cycles:
            print("    [OK] No circular dependencies detected!")
            print("    All expressions can be evaluated in topological order.")
            return
        
        print(f"    [WARNING] Found {len(cycles)} cycle(s)!\n")
        
        print("    Variables involved in cycles:")
        for var in sorted(vars_in_cycles, key=str.lower):
            exp_str = self._analyzer.get_expression_string(var)
            print(f"        - {var} = {exp_str}")
        
        print("\n    Cycle paths detected:")
        for i, cycle in enumerate(cycles, 1):
            cycle_str = " -> ".join(cycle)
            print(f"        {i}. {cycle_str}")
        
        print(f"\n    Impact: {len(vars_in_cycles)} variable(s) cannot be evaluated")
    
    def _show_undefined_variables(self):
        """Option 3: Show undefined variable references."""
        self._print_section("UNDEFINED VARIABLE CHECK")
        
        undefined = self._analyzer.get_undefined_variables()
        
        if not undefined:
            print("    [OK] All referenced variables are defined!")
            return
        
        print(f"    [WARNING] Found {len(undefined)} undefined variable(s):\n")
        
        for var in sorted(undefined, key=str.lower):
            # Find which variables reference this undefined variable
            referencing = []
            for defined_var in self._analyzer.get_defined_variables():
                if var in self._analyzer.get_dependencies(defined_var):
                    referencing.append(defined_var)
            
            print(f"        - '{var}' is referenced by: {', '.join(referencing)}")
    
    def _query_forward_dependencies(self):
        """Option 4: Query what a variable depends on."""
        self._print_section("FORWARD DEPENDENCY QUERY")
        
        var = input("    Enter variable name: ").strip()
        
        if not var:
            print("    No variable entered.")
            return
        
        if not self._analyzer.variable_exists(var):
            if self._analyzer.variable_is_referenced(var):
                print(f"    '{var}' is referenced but not defined.")
            else:
                print(f"    Variable '{var}' not found.")
            return
        
        exp_str = self._analyzer.get_expression_string(var)
        print(f"\n    {var} = {exp_str}")
        
        # Direct dependencies
        direct = self._analyzer.get_dependencies(var)
        print(f"\n    Direct dependencies ({len(direct)}):")
        if direct:
            for dep in sorted(direct, key=str.lower):
                status = "[DEFINED]" if self._analyzer.variable_exists(dep) else "[UNDEFINED]"
                print(f"        - {dep} {status}")
        else:
            print("        (none - this is an independent variable)")
        
        # All dependencies (transitive)
        all_deps = self._analyzer.get_all_dependencies(var)
        indirect = all_deps - direct
        
        if indirect:
            print(f"\n    Indirect dependencies ({len(indirect)}):")
            for dep in sorted(indirect, key=str.lower):
                status = "[DEFINED]" if self._analyzer.variable_exists(dep) else "[UNDEFINED]"
                print(f"        - {dep} {status}")
        
        print(f"\n    Total: {len(all_deps)} dependency(ies)")
    
    def _query_reverse_dependencies(self):
        """Option 5: Query what depends on a variable (reverse)."""
        self._print_section("REVERSE DEPENDENCY QUERY")
        
        var = input("    Enter variable name: ").strip()
        
        if not var:
            print("    No variable entered.")
            return
        
        if not self._analyzer.variable_exists(var):
            if self._analyzer.variable_is_referenced(var):
                print(f"    '{var}' is referenced but not defined.")
            else:
                print(f"    Variable '{var}' not found.")
            return
        
        exp_str = self._analyzer.get_expression_string(var)
        print(f"\n    Query: What depends on '{var}'?")
        print(f"    {var} = {exp_str}")
        
        # Direct dependents
        direct = self._analyzer.get_dependents(var)
        print(f"\n    Direct dependents ({len(direct)}):")
        if direct:
            for dep in sorted(direct, key=str.lower):
                dep_exp = self._analyzer.get_expression_string(dep)
                print(f"        - {dep} = {dep_exp}")
        else:
            print("        (none - this is a leaf variable)")
        
        # All dependents with levels
        all_deps, levels = self._analyzer.get_all_dependents(var)
        
        if all_deps - direct:
            max_level = max(levels.values()) if levels else 0
            for lvl in range(2, max_level + 1):
                vars_at_level = sorted([v for v, l in levels.items() if l == lvl], key=str.lower)
                if vars_at_level:
                    print(f"\n    Level {lvl} dependents ({len(vars_at_level)}):")
                    for dep in vars_at_level:
                        dep_exp = self._analyzer.get_expression_string(dep)
                        print(f"        - {dep} = {dep_exp}")
        
        # Impact summary
        print(f"\n    Impact Summary:")
        print(f"        If '{var}' changes, {len(all_deps)} variable(s) would need re-evaluation")
        if all_deps:
            print(f"        Affected: {', '.join(sorted(all_deps, key=str.lower))}")
    
    def _show_full_report(self):
        """Option 6: Show comprehensive analysis report."""
        self._print_section("FULL DEPENDENCY ANALYSIS REPORT")
        
        # Stats
        print(f"\n    STATISTICS")
        print(f"    {'.' * 50}")
        print(f"    Total variables defined:     {self._analyzer.get_total_variables()}")
        print(f"    Total dependency edges:      {self._analyzer.get_total_edges()}")
        
        undefined = self._analyzer.get_undefined_variables()
        print(f"    Undefined references:        {len(undefined)}")
        
        vars_in_cycles, cycles = self._analyzer.detect_cycles()
        print(f"    Cycles detected:             {len(cycles)}")
        print(f"    Variables in cycles:         {len(vars_in_cycles)}")
        
        # Health check
        print(f"\n    HEALTH CHECK")
        print(f"    {'.' * 50}")
        
        if not undefined and not cycles:
            print("    [OK] Graph is healthy - all expressions can be evaluated!")
        else:
            if undefined:
                print(f"    [!] Undefined variables: {', '.join(sorted(undefined, key=str.lower))}")
            if cycles:
                print(f"    [!] Circular references detected in: {', '.join(sorted(vars_in_cycles, key=str.lower))}")
        
        # Dependency overview
        print(f"\n    DEPENDENCY OVERVIEW")
        print(f"    {'.' * 50}")
        
        # Find independent variables (no dependencies)
        independent = [v for v in self._analyzer.get_defined_variables() 
                       if not self._analyzer.get_dependencies(v)]
        if independent:
            print(f"    Independent (base) variables: {', '.join(sorted(independent, key=str.lower))}")
        
        # Find leaf variables (nothing depends on them)
        leaves = [v for v in self._analyzer.get_defined_variables() 
                  if not self._analyzer.get_dependents(v)]
        if leaves:
            print(f"    Leaf (output) variables:      {', '.join(sorted(leaves, key=str.lower))}")
        
        # Most connected variables
        max_deps = 0
        most_deps = []
        for var in self._analyzer.get_defined_variables():
            deps = len(self._analyzer.get_dependencies(var))
            if deps > max_deps:
                max_deps = deps
                most_deps = [var]
            elif deps == max_deps and deps > 0:
                most_deps.append(var)
        
        if most_deps and max_deps > 0:
            print(f"    Most dependencies ({max_deps}):        {', '.join(sorted(most_deps, key=str.lower))}")
        
        max_dependents = 0
        most_dependents = []
        for var in self._analyzer.get_defined_variables():
            deps, _ = self._analyzer.get_all_dependents(var)
            if len(deps) > max_dependents:
                max_dependents = len(deps)
                most_dependents = [var]
            elif len(deps) == max_dependents and len(deps) > 0:
                most_dependents.append(var)
        
        if most_dependents and max_dependents > 0:
            print(f"    Most impact ({max_dependents} affected):     {', '.join(sorted(most_dependents, key=str.lower))}")
        
        # Complexity info
        print(f"\n    COMPLEXITY ANALYSIS")
        print(f"    {'.' * 50}")
        print(f"    Graph representation:        Adjacency List")
        print(f"    Cycle detection algorithm:   DFS with vertex coloring")
        print(f"    Traversal algorithm:         BFS (for transitive queries)")
        print(f"    Time complexity:             O(V + E) = O({self._analyzer.get_total_variables()} + {self._analyzer.get_total_edges()})")
        print(f"    Space complexity:            O(V + E)")


def run_dependency_analyzer(hash_table):
    """
    Main entry point for the dependency analyzer feature.
    
    Args:
        hash_table: HashTable containing DASK expressions
    """
    if len(list(hash_table.items())) == 0:
        print("\n    No DASK expressions loaded. Please add expressions first.\n")
        return
    
    ui = DependencyAnalyzerUI(hash_table)
    ui.run()
