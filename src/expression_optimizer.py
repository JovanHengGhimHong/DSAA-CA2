from structures.BinaryTree import BinaryTree
from structures.Stack import Stack


class ExpressionOptimizer:
    """Optimizes and simplifies DASK expressions using algebraic rules."""
    
    def __init__(self):
        self.operations = ['+', '-', '/', '*', '**', '++', '//']
        self.optimizations_applied = []
    
    def optimize(self, tree):
        """Main optimization method. Returns an optimized copy of the tree."""
        self.optimizations_applied = []
        return self._optimize_node(tree)
    
    def _optimize_node(self, node):
        """Recursively optimize using post-order traversal."""
        if node is None:
            return None
        
        left = node.getLeftTree()
        right = node.getRightTree()
        op = node.getKey()
        
        # Leaf node - return as-is
        if left is None and right is None:
            return BinaryTree(op)
        
        # Optimize subtrees first (post-order)
        optimized_left = self._optimize_node(left)
        optimized_right = self._optimize_node(right)
        
        return self._apply_rules(op, optimized_left, optimized_right)
    
    def _is_number(self, value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _get_number(self, value):
        return float(value)
    
    def _is_leaf(self, node):
        return node.getLeftTree() is None and node.getRightTree() is None
    
    def _get_leaf_value(self, node):
        if self._is_leaf(node):
            return node.getKey()
        return None
    
    def _create_number_node(self, value):
        if value == int(value):
            return BinaryTree(str(int(value)))
        return BinaryTree(str(value))
    
    def _apply_rules(self, op, left, right):
        """Apply algebraic simplification rules."""
        left_val = self._get_leaf_value(left)
        right_val = self._get_leaf_value(right)
        
        left_is_num = self._is_number(left_val) if left_val else False
        right_is_num = self._is_number(right_val) if right_val else False
        
        # Constant Folding
        if left_is_num and right_is_num:
            result = self._evaluate_constants(op, self._get_number(left_val), self._get_number(right_val))
            if result is not None:
                self.optimizations_applied.append(f"Constant folding: ({left_val} {op} {right_val}) => {result}")
                return self._create_number_node(result)
        
        # Addition identity rules
        if op == '+':
            if right_is_num and self._get_number(right_val) == 0:
                self.optimizations_applied.append(f"Identity: ({left_val or 'expr'} + 0) => {left_val or 'expr'}")
                return left
            if left_is_num and self._get_number(left_val) == 0:
                self.optimizations_applied.append(f"Identity: (0 + {right_val or 'expr'}) => {right_val or 'expr'}")
                return right
        
        # Subtraction rules
        if op == '-':
            if right_is_num and self._get_number(right_val) == 0:
                self.optimizations_applied.append(f"Identity: ({left_val or 'expr'} - 0) => {left_val or 'expr'}")
                return left
            if left_val and right_val and left_val == right_val:
                self.optimizations_applied.append(f"Self-cancellation: ({left_val} - {right_val}) => 0")
                return BinaryTree('0')
        
        # Multiplication rules
        if op == '*':
            if right_is_num and self._get_number(right_val) == 1:
                self.optimizations_applied.append(f"Identity: ({left_val or 'expr'} * 1) => {left_val or 'expr'}")
                return left
            if left_is_num and self._get_number(left_val) == 1:
                self.optimizations_applied.append(f"Identity: (1 * {right_val or 'expr'}) => {right_val or 'expr'}")
                return right
            if right_is_num and self._get_number(right_val) == 0:
                self.optimizations_applied.append(f"Zero rule: ({left_val or 'expr'} * 0) => 0")
                return BinaryTree('0')
            if left_is_num and self._get_number(left_val) == 0:
                self.optimizations_applied.append(f"Zero rule: (0 * {right_val or 'expr'}) => 0")
                return BinaryTree('0')
        
        # Division rules
        if op == '/':
            if right_is_num and self._get_number(right_val) == 1:
                self.optimizations_applied.append(f"Identity: ({left_val or 'expr'} / 1) => {left_val or 'expr'}")
                return left
            if left_is_num and self._get_number(left_val) == 0:
                if not (right_is_num and self._get_number(right_val) == 0):
                    self.optimizations_applied.append(f"Zero rule: (0 / {right_val or 'expr'}) => 0")
                    return BinaryTree('0')
            if left_val and right_val and left_val == right_val:
                self.optimizations_applied.append(f"Self-cancellation: ({left_val} / {right_val}) => 1")
                return BinaryTree('1')
        
        # Power rules
        if op == '**':
            if right_is_num and self._get_number(right_val) == 1:
                self.optimizations_applied.append(f"Identity: ({left_val or 'expr'} ** 1) => {left_val or 'expr'}")
                return left
            if right_is_num and self._get_number(right_val) == 0:
                self.optimizations_applied.append(f"Power rule: ({left_val or 'expr'} ** 0) => 1")
                return BinaryTree('1')
            if left_is_num and self._get_number(left_val) == 1:
                self.optimizations_applied.append(f"Power rule: (1 ** {right_val or 'expr'}) => 1")
                return BinaryTree('1')
            if left_is_num and self._get_number(left_val) == 0:
                if right_is_num and self._get_number(right_val) > 0:
                    self.optimizations_applied.append(f"Power rule: (0 ** {right_val}) => 0")
                    return BinaryTree('0')
        
        # No simplification - return new node with optimized children
        new_node = BinaryTree(op)
        new_node.left_tree = left
        new_node.right_tree = right
        return new_node
    
    def _evaluate_constants(self, op, left_val, right_val):
        """Evaluate operation on two constant values."""
        try:
            if op == '+':
                return left_val + right_val
            elif op == '-':
                return left_val - right_val
            elif op == '*':
                return left_val * right_val
            elif op == '/':
                if right_val != 0:
                    return left_val / right_val
                return None
            elif op == '**':
                return left_val ** right_val
            else:
                return None
        except:
            return None
    
    def get_optimizations(self):
        """Return list of optimizations applied."""
        return self.optimizations_applied


def tree_to_expression(tree, parenthesize=True):
    """Convert parse tree to string expression."""
    if tree is None:
        return ""
    
    left = tree.getLeftTree()
    right = tree.getRightTree()
    key = tree.getKey()
    
    if left is None and right is None:
        return str(key)
    
    left_expr = tree_to_expression(left, parenthesize)
    right_expr = tree_to_expression(right, parenthesize)
    
    if parenthesize:
        return f"({left_expr} {key} {right_expr})"
    else:
        return f"{left_expr} {key} {right_expr}"


class ExpressionOptimizerUI:
    """Interactive UI for the Expression Optimizer feature."""
    
    def __init__(self, hash_table, parser):
        self.hash_table = hash_table
        self.parser = parser
        self.optimizer = ExpressionOptimizer()
    
    def display_menu(self):
        menu = '''
+===============================================================+
|            Expression Optimizer / Simplifier                  |
+===============================================================+
|  1. Optimize a single expression (by variable name)          |
|  2. Optimize all expressions                                 |
|  3. Optimize a custom expression (enter manually)            |
|  4. Show optimization rules                                  |
|  5. Return to main menu                                      |
+===============================================================+
'''
        print(menu)
    
    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == '1':
                self._optimize_single()
            elif choice == '2':
                self._optimize_all()
            elif choice == '3':
                self._optimize_custom()
            elif choice == '4':
                self._show_rules()
            elif choice == '5':
                print("\nReturning to main menu...")
                break
            else:
                print("\nInvalid choice. Please enter 1-5.")
            
            input("\nPress Enter to continue...")
    
    def _optimize_single(self):
        print("\n" + "=" * 50)
        print("OPTIMIZE SINGLE EXPRESSION")
        print("=" * 50)
        
        variables = [var for var, _ in self.hash_table.items()]
        if not variables:
            print("\nNo expressions stored. Please add expressions first.")
            return
        
        print("\nAvailable variables:", ", ".join(sorted(variables)))
        var_name = input("\nEnter variable name to optimize: ").strip()
        
        dask_obj = self.hash_table[var_name]
        if dask_obj is None:
            print(f"\nVariable '{var_name}' not found.")
            return
        
        original_tokens = dask_obj.expression
        original_expr = ''.join(original_tokens)
        original_tree = self.parser.buildParseTree(original_tokens)
        
        optimized_tree = self.optimizer.optimize(original_tree)
        optimized_expr = tree_to_expression(optimized_tree)
        optimizations = self.optimizer.get_optimizations()
        
        print("\n" + "-" * 50)
        print(f"Variable: {var_name}")
        print("-" * 50)
        print(f"\nOriginal Expression:  {original_expr}")
        print(f"Optimized Expression: {optimized_expr}")
        
        if optimizations:
            print(f"\nOptimizations Applied ({len(optimizations)}):")
            for i, opt in enumerate(optimizations, 1):
                print(f"  {i}. {opt}")
        else:
            print("\nNo optimizations possible - expression is already optimal!")
        
        print("\n" + "-" * 50)
        print("Original Tree Structure:")
        print("-" * 50)
        original_tree.print_tree_inorder()
        
        print("\n" + "-" * 50)
        print("Optimized Tree Structure:")
        print("-" * 50)
        optimized_tree.print_tree_inorder()
        
        # Ask if user wants to update the stored expression
        if optimizations:
            update = input("\nUpdate stored expression with optimized version? (Y/N): ").strip().upper()
            if update == 'Y':
                optimized_tokens = self.parser.tokenizer(optimized_expr)
                dask_obj.expression = optimized_tokens
                self.hash_table[var_name] = dask_obj
                print(f"Expression for '{var_name}' has been updated!")
            else:
                print("Expression not updated.")
    
    def _optimize_all(self):
        print("\n" + "=" * 50)
        print("OPTIMIZE ALL EXPRESSIONS")
        print("=" * 50)
        
        variables = [(var, dask_obj) for var, dask_obj in self.hash_table.items()]
        if not variables:
            print("\nNo expressions stored. Please add expressions first.")
            return
        
        total_optimizations = 0
        optimized_count = 0
        
        print("\n{:<10} {:<25} {:<25} {:<5}".format("Variable", "Original", "Optimized", "Opts"))
        print("-" * 70)
        
        for var, dask_obj in sorted(variables, key=lambda x: x[0].lower()):
            original_tokens = dask_obj.expression
            original_expr = ''.join(original_tokens)
            original_tree = self.parser.buildParseTree(original_tokens)
            
            optimized_tree = self.optimizer.optimize(original_tree)
            optimized_expr = tree_to_expression(optimized_tree)
            optimizations = self.optimizer.get_optimizations()
            
            num_opts = len(optimizations)
            total_optimizations += num_opts
            if num_opts > 0:
                optimized_count += 1
            
            orig_display = original_expr[:22] + "..." if len(original_expr) > 25 else original_expr
            opt_display = optimized_expr[:22] + "..." if len(optimized_expr) > 25 else optimized_expr
            
            print("{:<10} {:<25} {:<25} {:<5}".format(var, orig_display, opt_display, num_opts))
        
        print("-" * 70)
        print(f"\nSummary:")
        print(f"  Total expressions: {len(variables)}")
        print(f"  Expressions optimized: {optimized_count}")
        print(f"  Total optimizations applied: {total_optimizations}")
        
        # Ask if user wants to update all stored expressions
        if optimized_count > 0:
            update = input(f"\nUpdate all {optimized_count} optimizable expression(s)? (Y/N): ").strip().upper()
            if update == 'Y':
                updated = 0
                for var, dask_obj in variables:
                    original_tokens = dask_obj.expression
                    original_tree = self.parser.buildParseTree(original_tokens)
                    optimized_tree = self.optimizer.optimize(original_tree)
                    optimizations = self.optimizer.get_optimizations()
                    
                    if optimizations:
                        optimized_expr = tree_to_expression(optimized_tree)
                        optimized_tokens = self.parser.tokenizer(optimized_expr)
                        dask_obj.expression = optimized_tokens
                        self.hash_table[var] = dask_obj
                        updated += 1
                
                print(f"{updated} expression(s) have been updated!")
            else:
                print("Expressions not updated.")
    
    def _optimize_custom(self):
        print("\n" + "=" * 50)
        print("OPTIMIZE CUSTOM EXPRESSION")
        print("=" * 50)
        
        print("\nEnter a DASK expression to optimize.")
        print("Example: ((x + 0) * (1 + 2))")
        expression = input("\nExpression: ").strip()
        
        if not expression:
            print("\nNo expression entered.")
            return
        
        if not self.parser.verify_expression(expression):
            print("\nInvalid expression format. Please use proper DASK syntax.")
            print("Example: ((a + b) * c) or (x + 0)")
            return
        
        tokens = self.parser.tokenizer(expression)
        original_tree = self.parser.buildParseTree(tokens)
        optimized_tree = self.optimizer.optimize(original_tree)
        optimized_expr = tree_to_expression(optimized_tree)
        optimizations = self.optimizer.get_optimizations()
        
        print("\n" + "-" * 50)
        print(f"Original Expression:  {expression}")
        print(f"Optimized Expression: {optimized_expr}")
        
        if optimizations:
            print(f"\nOptimizations Applied ({len(optimizations)}):")
            for i, opt in enumerate(optimizations, 1):
                print(f"  {i}. {opt}")
            print("\nStep-by-step transformation:")
            print(f"  Start: {expression}")
            print(f"  End:   {optimized_expr}")
        else:
            print("\nNo optimizations possible - expression is already optimal!")
        
        print("\n" + "-" * 50)
        print("Original Parse Tree (inorder):")
        original_tree.print_tree_inorder()
        
        print("\n" + "-" * 50)
        print("Optimized Parse Tree (inorder):")
        optimized_tree.print_tree_inorder()
    
    def _show_rules(self):
        rules = '''
+===========================================================================+
|                     EXPRESSION OPTIMIZATION RULES                         |
+===========================================================================+
|                                                                           |
|  IDENTITY RULES:                                                         |
|    x + 0 = x       0 + x = x       x - 0 = x                             |
|    x * 1 = x       1 * x = x       x / 1 = x       x ** 1 = x            |
|                                                                           |
|  ZERO RULES:                                                             |
|    x * 0 = 0       0 * x = 0       0 / x = 0       0 ** x = 0            |
|                                                                           |
|  POWER RULES:                                                            |
|    x ** 0 = 1      1 ** x = 1                                            |
|                                                                           |
|  SELF-CANCELLATION:                                                      |
|    x - x = 0       x / x = 1                                             |
|                                                                           |
|  CONSTANT FOLDING:                                                       |
|    (2 + 3) = 5     (4 * 5) = 20    (10 / 2) = 5                          |
|                                                                           |
+===========================================================================+
'''
        print(rules)


def run_expression_optimizer(hash_table, parser):
    """Entry point for the Expression Optimizer feature."""
    ui = ExpressionOptimizerUI(hash_table, parser)
    ui.run()
