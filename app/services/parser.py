import re
import logging
from sympy import symbols, sympify, SympifyError
from sympy.logic import simplify_logic
from sympy.sets import FiniteSet, Union, Intersection, Complement, ProductSet

logger = logging.getLogger(__name__)

class LogicSetParser:
    def __init__(self):
        # Extended symbol mapping with more symbols
        self.symbols_map = {
            # Logic operators
            'و': '&', 'and': '&', '∧': '&', '⋀': '&',
            'یا': '|', 'or': '|', '∨': '|', '⋁': '|',
            'نقیض': '~', 'not': '~', '¬': '~', '∼': '~', '!': '~',
            'آنگاه': '>>', 'then': '>>', '→': '>>', '⇒': '>>', '⊃': '>>', '->': '>>',
            'اگر و فقط اگر': '==', 'iff': '==', '↔': '==', '⇔': '==', '<->': '==',
            'xor': '^', '⊕': '^',
            
            # Set operators
            'اجتماع': 'Union', 'union': 'Union', '∪': 'Union',
            'اشتراک': 'Intersection', 'intersection': 'Intersection', '∩': 'Intersection',
            'مکمل': 'Complement', 'complement': 'Complement', '′': 'Complement', "'": 'Complement', '∁': 'Complement',
            'تفاضل': 'Complement', 'difference': '-', '\\': '-',
            'حاصلضرب': 'ProductSet', 'product': 'ProductSet', '×': 'ProductSet', '⊗': 'ProductSet',
        }
        
        # Common sets
        self.common_sets = {
            'طبیعی': 'Naturals', 'N': 'Naturals', 'ℕ': 'Naturals',
            'صحیح': 'Integers', 'Z': 'Integers', 'ℤ': 'Integers',
            'گویا': 'Rationals', 'Q': 'Rationals', 'ℚ': 'Rationals',
            'حقیقی': 'Reals', 'R': 'Reals', 'ℝ': 'Reals',
            'مختلط': 'Complexes', 'C': 'Complexes', 'ℂ': 'Complexes',
        }
    
    def clean_input(self, text: str) -> str:
        """Clean input text by removing problematic characters"""
        # Remove bullet points and other non-ASCII characters that might cause issues
        text = re.sub(r'[•·∙‣⁃]', ' ', text)  # Remove various bullet characters
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.strip()
        return text
    
    def parse_logic_expression(self, text: str):
        """Parse logical expressions with extended symbol support"""
        try:
            # Clean the input first
            text = self.clean_input(text)
            
            # Replace all known symbols
            for persian, english in self.symbols_map.items():
                text = text.replace(persian, english)
            
            # Extract variables from expression
            variables = set(re.findall(r'\b[a-zA-Z]\b', text))
            if not variables:
                variables = set(re.findall(r'\b[pqr]\b', text))
                if not variables:
                    variables = set(re.findall(r'\b[a-z]\b', text))
            
            # Create symbols
            syms = symbols(' '.join(variables))
            syms_dict = {str(sym): sym for sym in syms}
            
            # Convert to sympy expression
            expr = sympify(text, locals=syms_dict)
            return expr, variables
        
        except (SympifyError, Exception) as e:
            logger.error(f"Error parsing logical expression: {str(e)}")
            raise ValueError(f"خطا در پردازش عبارت منطقی: {str(e)}")
    
    def parse_set_expression(self, text: str):
        """Parse set theory expressions with extended symbol support"""
        try:
            # Clean the input first
            text = self.clean_input(text)
            
            # Replace all known symbols
            for persian, english in self.symbols_map.items():
                text = text.replace(persian, english)
            
            # Replace common sets
            for persian, english in self.common_sets.items():
                text = text.replace(persian, english)
            
            # Extract set definitions
            set_pattern = r'([A-Z])\s*=\s*\{([^}]+)\}'
            sets = dict(re.findall(set_pattern, text))
            
            # Create set objects
            set_objects = {}
            for name, elements in sets.items():
                elements = [elem.strip() for elem in elements.split(',')]
                processed_elements = []
                
                for elem in elements:
                    try:
                        # Try to convert to number
                        if '.' in elem:
                            processed_elements.append(float(elem))
                        else:
                            processed_elements.append(int(elem))
                    except ValueError:
                        # Keep as string if not a number
                        processed_elements.append(elem)
                
                set_objects[name] = FiniteSet(*processed_elements)
            
            # Replace set names with their objects in the expression
            for set_name in set_objects:
                text = text.replace(set_name, f'set_objects["{set_name}"]')
            
            # Define available operations
            operations = {
                "Union": Union,
                "Intersection": Intersection,
                "Complement": Complement,
                "ProductSet": ProductSet,
                "set_objects": set_objects
            }
            
            # Evaluate the expression
            result = eval(text, operations)
            return result
        
        except Exception as e:
            logger.error(f"Error parsing set expression: {str(e)}")
            raise ValueError(f"خطا در پردازش عبارت مجموعه‌ای: {str(e)}")
    
    def simplify_logic(self, expr):
        """Simplify a logical expression"""
        try:
            return simplify_logic(expr)
        except Exception as e:
            logger.error(f"Error simplifying expression: {str(e)}")
            raise ValueError(f"خطا در ساده‌سازی عبارت: {str(e)}")