class DependencyAnalyzer:
    """Unified dependency analyzer with forward/reverse graphs and cycle detection."""
    
    # DFS vertex states for cycle detection
    UNVISITED = 0
    VISITING = 1
    VISITED = 2
    
    def __init__(self, hash_table=None, expressions=None):
        """Initialize with either hash_table or expressions dict."""
        self._hash_table = hash_table
        self._expressions = expressions  # dict of var -> expression string
        self._defined_variables = set()
        self._forward_graph = {}
        self._reverse_graph = {}
        self._undefined_vars = None
        self._cycles = None
        self._vars_in_cycles = None
        self._build_graphs()
    
    def _build_graphs(self):
        """Build both forward and reverse dependency graphs."""
        # Build forward graph from hash_table or expressions dict
        if self._hash_table is not None:
            for variable, dask_obj in self._hash_table.items():
                if dask_obj is not None:
                    dependencies = self._extract_dependencies(dask_obj.expression)
                    dependencies.discard(variable)
                    
                    self._defined_variables.add(variable)
                    self._forward_graph[variable] = dependencies
                    
                    for dep in dependencies:
                        if dep not in self._forward_graph:
                            self._forward_graph[dep] = set()
        elif self._expressions is not None:
            for variable, expr_tokens in self._expressions.items():
                dependencies = self._extract_dependencies(expr_tokens)
                dependencies.discard(variable)
                
                self._defined_variables.add(variable)
                self._forward_graph[variable] = dependencies
                
                for dep in dependencies:
                    if dep not in self._forward_graph:
                        self._forward_graph[dep] = set()
        
        # Build reverse graph (transpose)
        for var in self._forward_graph:
            self._reverse_graph[var] = set()
        
        for var, deps in self._forward_graph.items():
            for dep in deps:
                if dep not in self._reverse_graph:
                    self._reverse_graph[dep] = set()
                self._reverse_graph[dep].add(var)
    
    @staticmethod
    def _extract_dependencies(tokens):
        """Extract variable dependencies from expression tokens."""
        return {token for token in tokens if token.isalpha()}
    
    def get_dependencies(self, variable):
        """Get direct dependencies of a variable."""
        return self._forward_graph.get(variable, set()).copy()
    
    def get_all_dependencies(self, variable):
        """Get all dependencies using BFS (transitive closure)."""
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
    
    def get_dependents(self, variable):
        """Get direct dependents of a variable."""
        return self._reverse_graph.get(variable, set()).copy()
    
    def get_all_dependents(self, variable):
        """Get all dependents with distances using BFS."""
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
    
    def detect_cycles(self):
        """Detect all cycles using DFS with vertex coloring."""
        if self._cycles is not None:
            return self._vars_in_cycles, self._cycles
        
        state = {node: self.UNVISITED for node in self._forward_graph}
        self._vars_in_cycles = set()
        self._cycles = []
        
        def dfs(node, path):
            state[node] = self.VISITING
            
            for neighbor in self._forward_graph.get(node, set()):
                if neighbor not in state:
                    continue
                
                if state[neighbor] == self.VISITING:
                    cycle = self._reconstruct_cycle(path, neighbor)
                    self._cycles.append(cycle)
                    self._vars_in_cycles.update(cycle[:-1])
                    
                elif state[neighbor] == self.UNVISITED:
                    dfs(neighbor, path + [neighbor])
            
            state[node] = self.VISITED
        
        for node in self._forward_graph:
            if state[node] == self.UNVISITED:
                dfs(node, [node])
        
        return self._vars_in_cycles, self._cycles
    
    def _reconstruct_cycle(self, path, cycle_start):
        """Reconstruct cycle path from DFS traversal."""
        try:
            start_idx = path.index(cycle_start)
            return path[start_idx:] + [cycle_start]
        except ValueError:
            return [cycle_start, path[-1], cycle_start]
    
    def get_undefined_variables(self):
        """Find variables referenced but never defined."""
        if self._undefined_vars is not None:
            return self._undefined_vars
        
        all_referenced = set()
        for deps in self._forward_graph.values():
            all_referenced.update(deps)
        
        self._undefined_vars = all_referenced - self._defined_variables
        return self._undefined_vars
    
    def get_defined_variables(self):
        return self._defined_variables.copy()
    
    def get_total_variables(self):
        return len(self._defined_variables)
    
    def get_total_edges(self):
        return sum(len(deps) for deps in self._forward_graph.values())
    
    def has_cycles(self):
        _, cycles = self.detect_cycles()
        return len(cycles) > 0
    
    def has_undefined(self):
        return len(self.get_undefined_variables()) > 0
    
    def variable_exists(self, variable):
        return variable in self._defined_variables
    
    def variable_is_referenced(self, variable):
        return variable in self._forward_graph
    
    def get_expression_string(self, variable):
        if self._hash_table is not None:
            dask_obj = self._hash_table[variable]
            if dask_obj:
                return ''.join(dask_obj.expression)
        elif self._expressions is not None:
            if variable in self._expressions:
                return ''.join(self._expressions[variable])
        return "?"


class DependencyAnalyzerUI:
    """User interface for the Dependency Analyzer."""
    
    SUBMENU = """
    +==============================================================+
    |             DEPENDENCY ANALYZER - SUB MENU                   |
    +==============================================================+
    |  1. View all variable dependencies                           |
    |  2. Check for undefined variables                            |
    |  3. Query: What does variable X depend on?                   |
    |  4. Query: What depends on variable X? (reverse)             |
    |  5. Full analysis report                                     |
    |  6. Load & analyze from file (supports cycles)               |
    |  7. Return to main menu                                      |
    +==============================================================+
    """
    
    def __init__(self, hash_table):
        self._hash_table = hash_table
        self._analyzer = None
    
    def run(self):
        self._analyzer = DependencyAnalyzer(self._hash_table)
        self._print_header()
        
        while True:
            print(self.SUBMENU)
            choice = input("    Enter choice (1-7): ").strip()
            
            if choice == '1':
                self._show_all_dependencies()
            elif choice == '2':
                self._show_undefined_variables()
            elif choice == '3':
                self._query_forward_dependencies()
            elif choice == '4':
                self._query_reverse_dependencies()
            elif choice == '5':
                self._show_full_report()
            elif choice == '6':
                self._load_and_analyze_file()
            elif choice == '7':
                print("\n    Returning to main menu...\n")
                break
            else:
                print("\n    Invalid choice. Please enter 1-9.\n")
            
            input("\n    Press Enter to continue...")
    
    def _print_header(self):
        print("\n" + "=" * 64)
        print("           DEPENDENCY ANALYZER & CYCLE DETECTOR")
        print("=" * 64)
        print(f"    Variables loaded: {self._analyzer.get_total_variables()}")
        print(f"    Dependency edges: {self._analyzer.get_total_edges()}")
        print("=" * 64)
    
    def _print_section(self, title):
        print(f"\n    {'-' * 56}")
        print(f"    {title}")
        print(f"    {'-' * 56}")
    
    def _show_all_dependencies(self):
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
    
    def _show_undefined_variables(self):
        self._print_section("UNDEFINED VARIABLE CHECK")
        
        undefined = self._analyzer.get_undefined_variables()
        
        if not undefined:
            print("    [OK] All referenced variables are defined!")
            return
        
        print(f"    [WARNING] Found {len(undefined)} undefined variable(s):\n")
        
        for var in sorted(undefined, key=str.lower):
            referencing = []
            for defined_var in self._analyzer.get_defined_variables():
                if var in self._analyzer.get_dependencies(defined_var):
                    referencing.append(defined_var)
            
            print(f"        - '{var}' is referenced by: {', '.join(referencing)}")
    
    def _query_forward_dependencies(self):
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
        
        direct = self._analyzer.get_dependencies(var)
        print(f"\n    Direct dependencies ({len(direct)}):")
        if direct:
            for dep in sorted(direct, key=str.lower):
                status = "[DEFINED]" if self._analyzer.variable_exists(dep) else "[UNDEFINED]"
                print(f"        - {dep} {status}")
        else:
            print("        (none - this is an independent variable)")
        
        all_deps = self._analyzer.get_all_dependencies(var)
        indirect = all_deps - direct
        
        if indirect:
            print(f"\n    Indirect dependencies ({len(indirect)}):")
            for dep in sorted(indirect, key=str.lower):
                status = "[DEFINED]" if self._analyzer.variable_exists(dep) else "[UNDEFINED]"
                print(f"        - {dep} {status}")
        
        print(f"\n    Total: {len(all_deps)} dependency(ies)")
    
    def _query_reverse_dependencies(self):
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
        
        direct = self._analyzer.get_dependents(var)
        print(f"\n    Direct dependents ({len(direct)}):")
        if direct:
            for dep in sorted(direct, key=str.lower):
                dep_exp = self._analyzer.get_expression_string(dep)
                print(f"        - {dep} = {dep_exp}")
        else:
            print("        (none - this is a leaf variable)")
        
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
        
        print(f"\n    Impact Summary:")
        print(f"        If '{var}' changes, {len(all_deps)} variable(s) would need re-evaluation")
        if all_deps:
            print(f"        Affected: {', '.join(sorted(all_deps, key=str.lower))}")
    
    def _show_full_report(self):
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
        
        independent = [v for v in self._analyzer.get_defined_variables() 
                       if not self._analyzer.get_dependencies(v)]
        if independent:
            print(f"    Independent (base) variables: {', '.join(sorted(independent, key=str.lower))}")
        
        leaves = [v for v in self._analyzer.get_defined_variables() 
                  if not self._analyzer.get_dependents(v)]
        if leaves:
            print(f"    Leaf (output) variables:      {', '.join(sorted(leaves, key=str.lower))}")
        
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
    
    def _load_and_analyze_file(self):
        """Load expressions from file and analyze (supports cycles)."""
        self._print_section("LOAD & ANALYZE FROM FILE")
        
        print("    This loads expressions directly for analysis without")
        print("    adding them to the main program (supports cycles).\n")
        
        filepath = input("    Enter file path: ").strip()
        
        if not filepath:
            print("    No file path entered.")
            return
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"    File not found: {filepath}")
            return
        except Exception as e:
            print(f"    Error reading file: {e}")
            return
        
        # Parse expressions from file
        expressions = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            
            key, exp = line.split('=', 1)
            key = key.strip()
            # Simple tokenizer for dependencies
            tokens = []
            current = ''
            for char in exp:
                if char.isalpha():
                    current += char
                else:
                    if current:
                        tokens.append(current)
                        current = ''
            if current:
                tokens.append(current)
            expressions[key] = tokens
        
        if not expressions:
            print("    No valid expressions found in file.")
            return
        
        # Create analyzer for file expressions
        file_analyzer = DependencyAnalyzer(expressions=expressions)
        
        print(f"\n    Loaded {len(expressions)} expressions from file.")
        print(f"    Dependency edges: {file_analyzer.get_total_edges()}")
        
        # Check for cycles
        vars_in_cycles, cycles = file_analyzer.detect_cycles()
        
        print(f"\n    CYCLE DETECTION RESULTS")
        print(f"    {'.' * 50}")
        
        if cycles:
            print(f"    [WARNING] Found {len(cycles)} cycle(s)!")
            print(f"    Variables in cycles: {len(vars_in_cycles)}")
            
            print("\n    Cycle paths:")
            for i, cycle in enumerate(cycles, 1):
                cycle_str = " -> ".join(cycle)
                print(f"        {i}. {cycle_str}")
            
            print(f"\n    Variables involved:")
            for var in sorted(vars_in_cycles, key=str.lower):
                exp_str = file_analyzer.get_expression_string(var)
                print(f"        - {var} = {exp_str}")
        else:
            print("    [OK] No circular dependencies detected!")
        
        # Check for undefined
        undefined = file_analyzer.get_undefined_variables()
        if undefined:
            print(f"\n    UNDEFINED VARIABLES")
            print(f"    {'.' * 50}")
            print(f"    Found {len(undefined)}: {', '.join(sorted(undefined, key=str.lower))}")
        
        # Show all dependencies
        print(f"\n    ALL DEPENDENCIES")
        print(f"    {'.' * 50}")
        for var in sorted(file_analyzer.get_defined_variables(), key=str.lower):
            deps = file_analyzer.get_dependencies(var)
            exp_str = file_analyzer.get_expression_string(var)
            if deps:
                print(f"    {var} = {exp_str}")
                print(f"        --> depends on: {', '.join(sorted(deps, key=str.lower))}")
            else:
                print(f"    {var} = {exp_str}")
                print(f"        --> (independent)")


def run_dependency_analyzer(hash_table):
    """Main entry point for the dependency analyzer feature."""
    ui = DependencyAnalyzerUI(hash_table)
    ui.run()
