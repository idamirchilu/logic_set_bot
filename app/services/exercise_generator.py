import random
import logging
from sympy import symbols, simplify_logic
from sympy.sets import FiniteSet, Union, Intersection

logger = logging.getLogger(__name__)

class ExerciseGenerator:
    def __init__(self):
        self.logic_exercises = [
            self.generate_simplification_exercise,
            self.generate_truth_table_exercise,
            self.generate_equivalence_exercise
        ]
        
        self.set_exercises = [
            self.generate_set_operation_exercise,
            self.generate_set_relation_exercise,
            self.generate_cartesian_product_exercise
        ]
    
    def generate_exercise(self, exercise_type: str, difficulty: int = 1):
        """Generate a random exercise based on type and difficulty"""
        if exercise_type == "logic":
            generator = random.choice(self.logic_exercises)
        else:
            generator = random.choice(self.set_exercises)
        
        return generator(difficulty)
    
    def generate_simplification_exercise(self, difficulty: int):
        """Generate a logic simplification exercise"""
        variables = random.sample(['p', 'q', 'r', 's'], min(2 + difficulty, 4))
        p, q, r, s = symbols('p q r s')
        
        # Different patterns based on difficulty
        if difficulty == 1:
            # Simple patterns
            patterns = [
                f"({p} & {q}) | ({p} & ~{q})",
                f"({p} | {q}) & ({p} | ~{q})",
                f"{p} | (~{p} & {q})"
            ]
        elif difficulty == 2:
            # Medium complexity
            patterns = [
                f"({p} | {q}) & (~{p} | {q}) & ({p} | ~{q})",
                f"({p} & {q}) | ({p} & ~{q}) | (~{p} & {q})",
                f"({p} >> {q}) & ({q} >> {p})"
            ]
        else:
            # Higher complexity
            patterns = [
                f"({p} | {q} | {r}) & ({p} | {q} | ~{r}) & ({p} | ~{q} | {r})",
                f"({p} >> ({q} >> {r})) >> (({p} >> {q}) >> ({p} >> {r}))",
                f"~(~{p} & ~{q}) & ~(~{p} & ~{r}) & ~(~{q} & ~{r})"
            ]
        
        expression = random.choice(patterns)
        simplified = simplify_logic(eval(expression))
        
        return {
            "question": f"عبارت منطقی زیر را ساده کنید: {expression}",
            "answer": str(simplified),
            "type": "logic",
            "difficulty": difficulty
        }
    
    def generate_truth_table_exercise(self, difficulty: int):
        """Generate a truth table exercise"""
        variables = random.sample(['p', 'q', 'r'], min(2 + difficulty // 2, 3))
        p, q, r = symbols('p q r')
        
        if difficulty == 1:
            expression = f"{p} & {q}"
        elif difficulty == 2:
            expression = f"{p} >> {q}"
        else:
            expression = f"({p} >> {q}) | ({q} >> {r})"
        
        return {
            "question": f"جدول درستی برای عبارت زیر ایجاد کنید: {expression}",
            "answer": expression,
            "type": "logic",
            "difficulty": difficulty
        }
    
    def generate_equivalence_exercise(self, difficulty: int):
        """Generate a logic equivalence exercise"""
        p, q = symbols('p q')
        
        equivalences = [
            (f"{p} & {q}", f"{q} & {p}", "معادل است"),
            (f"{p} | {q}", f"{q} | {p}", "معادل است"),
            (f"{p} & {q}", f"{p} | {q}", "معادل نیست"),
            (f"~({p} & {q})", f"~{p} | ~{q}", "معادل است"),  # De Morgan
            (f"~({p} | {q})", f"~{p} & ~{q}", "معادل است")   # De Morgan
        ]
        
        expr1, expr2, is_equivalent = random.choice(equivalences)
        
        return {
            "question": f"آیا عبارت {expr1} با عبارت {expr2} معادل است؟",
            "answer": "بله" if is_equivalent == "معادل است" else "خیر",
            "type": "logic",
            "difficulty": difficulty
        }
    
    def generate_set_operation_exercise(self, difficulty: int):
        """Generate a set operation exercise"""
        sets = {
            'A': FiniteSet(1, 2, 3, 4),
            'B': FiniteSet(3, 4, 5, 6),
            'C': FiniteSet(2, 4, 6, 8),
            'D': FiniteSet(1, 3, 5, 7)
        }
        
        operations = [
            ("A ∪ B", "اجتماع"),
            ("A ∩ B", "اشتراک"),
            ("A - B", "تفاضل")
        ]
        
        if difficulty > 1:
            operations.extend([
                ("(A ∪ B) ∩ C", "عبارت ترکیبی"),
                ("(A - B) ∪ C", "عبارت ترکیبی")
            ])
        
        operation, op_type = random.choice(operations)
        
        # Calculate answer
        if "∪" in operation:
            result = sets['A'].union(sets['B'])
        elif "∩" in operation:
            result = sets['A'].intersect(sets['B'])
        elif "-" in operation:
            result = sets['A'] - sets['B']
        else:
            # For complex expressions
            result = "محاسبه دستی مورد نیاز"
        
        return {
            "question": f"{operation} را محاسبه کنید که در آن A = {{1, 2, 3, 4}}, B = {{3, 4, 5, 6}}, C = {{2, 4, 6, 8}}",
            "answer": str(result),
            "type": "set_theory",
            "difficulty": difficulty
        }
    
    def generate_set_relation_exercise(self, difficulty: int):
        """Generate a set relation exercise"""
        sets = {
            'A': FiniteSet(1, 2, 3),
            'B': FiniteSet(1, 2, 3, 4, 5),
            'C': FiniteSet(2, 4),
            'D': FiniteSet(1, 3, 5)
        }
        
        relations = [
            ("A ⊆ B", "زیرمجموعه"),
            ("C ⊆ B", "زیرمجموعه"),
            ("A ⊂ B", "زیرمجموعه سره"),
            ("A ⊆ C", "زیرمجموعه نادرست")
        ]
        
        relation, rel_type = random.choice(relations)
        
        # Determine answer
        if "A ⊆ B" in relation:
            answer = "صحیح" if sets['A'].is_subset(sets['B']) else "غلط"
        elif "C ⊆ B" in relation:
            answer = "صحیح" if sets['C'].is_subset(sets['B']) else "غلط"
        elif "A ⊂ B" in relation:
            answer = "صحیح" if sets['A'].is_proper_subset(sets['B']) else "غلط"
        else:  # A ⊆ C
            answer = "صحیح" if sets['A'].is_subset(sets['C']) else "غلط"
        
        return {
            "question": f"تعیین کنید که آیا عبارت زیر صحیح است یا غلط: {relation} که در آن A = {{1, 2, 3}}, B = {{1, 2, 3, 4, 5}}, C = {{2, 4}}",
            "answer": answer,
            "type": "set_theory",
            "difficulty": difficulty
        }
    
    def generate_cartesian_product_exercise(self, difficulty: int):
        """Generate a Cartesian product exercise"""
        sets = {
            'A': FiniteSet(1, 2),
            'B': FiniteSet('a', 'b'),
            'C': FiniteSet('x', 'y')
        }
        
        if difficulty == 1:
            operation = "A × B"
            result = sets['A'] * sets['B']
        else:
            operation = "A × B × C"
            result = "محاسبه دستی مورد نیاز"  # SymPy doesn't support triple product directly
        
        return {
            "question": f"{operation} را محاسبه کنید که در آن A = {{1, 2}}, B = {{'a', 'b'}}, C = {{'x', 'y'}}",
            "answer": str(result),
            "type": "set_theory",
            "difficulty": difficulty
        }