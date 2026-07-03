import re
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

# TAHAP 1: ANALISIS LEKSIKAL

class TokenType(Enum):
    """Jenis-jenis token yang dikenali"""
    WHILE = "WHILE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    SEMICOLON = "SEMICOLON"
    ASSIGN = "ASSIGN"
    REL_OP = "REL_OP"
    ARITH_OP = "ARITH_OP"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    EOF = "EOF"

@dataclass
class Token:
    """Struktur untuk menyimpan token"""
    type: TokenType
    value: str
    line: int
    column: int

class LexicalAnalyzer:
    """Menganalisis leksikal: mengubah kode menjadi token"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        
        # Pola untuk mengenali token
        self.token_patterns = [
            (TokenType.WHILE, r'while'),
            (TokenType.LPAREN, r'\('),
            (TokenType.RPAREN, r'\)'),
            (TokenType.LBRACE, r'\{'),
            (TokenType.RBRACE, r'\}'),
            (TokenType.SEMICOLON, r';'),
            (TokenType.ASSIGN, r'='),
            (TokenType.REL_OP, r'<=|>=|==|!=|<|>'),
            (TokenType.ARITH_OP, r'[+\-*/]'),
            (TokenType.IDENTIFIER, r'[a-zA-Z][a-zA-Z0-9]*'),
            (TokenType.NUMBER, r'[0-9]+'),
        ]
        
        # Gabungkan semua pola
        self.regex = re.compile(
            '|'.join(f'(?P<{token_type.name}>{pattern})' 
                     for token_type, pattern in self.token_patterns)
        )

    def tokenize(self) -> List[Token]:
        """Memecah kode menjadi token-token"""
        tokens = []
        
        for match in self.regex.finditer(self.source_code):
            token_type = TokenType[match.lastgroup]
            value = match.group()
            tokens.append(Token(token_type, value, self.line, self.column))
            self.column += len(value)
        
        tokens.append(Token(TokenType.EOF, "EOF", self.line, self.column))
        return tokens
    
    def print_tokens(self, tokens: List[Token]):
        """Mencetak hasil analisis leksikal"""
        print("\n" + "="*60)
        print("TAHAP 1: ANALISIS LEKSIKAL")
        print("="*60)
        print(f"{'TIPE':<15} {'NILAI':<15} {'BARIS':<6} {'KOLOM':<6}")
        print("-"*60)
        for token in tokens:
            print(f"{token.type.value:<15} {token.value:<15} {token.line:<6} {token.column:<6}")
        print("="*60)

# TAHAP 2: ANALISIS SINTAKSIS

@dataclass
class ASTNode:
    """Node dasar untuk AST"""
    pass

@dataclass
class ProgramNode(ASTNode):
    """Node untuk program"""
    statements: List[ASTNode]

@dataclass
class WhileLoopNode(ASTNode):
    """Node untuk while loop"""
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class AssignmentNode(ASTNode):
    """Node untuk assignment"""
    identifier: str
    expression: ASTNode

@dataclass
class BinaryOpNode(ASTNode):
    """Node untuk operasi biner"""
    operator: str
    left: ASTNode
    right: ASTNode

@dataclass
class IdentifierNode(ASTNode):
    """Node untuk identifier/variabel"""
    name: str

@dataclass
class NumberNode(ASTNode):
    """Node untuk angka"""
    value: int

class Parser:
    """Menganalisis sintaksis: membentuk AST dari token"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_pos = 0
        self.errors = []
    
    def current_token(self) -> Token:
        """Mendapatkan token saat ini"""
        if self.current_pos < len(self.tokens):
            return self.tokens[self.current_pos]
        return None
    
    def peek_next_token(self) -> Token:
        """Melihat token berikutnya"""
        pos = self.current_pos + 1
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def eat(self, expected_type: TokenType) -> Token:
        """Mengonsumsi token yang diharapkan"""
        token = self.current_token()
        if token and token.type == expected_type:
            self.current_pos += 1
            return token
        else:
            expected = expected_type.value
            found = token.type.value if token else "EOF"
            error = f"Error di baris {token.line if token else '?'}: Diharapkan '{expected}', ditemukan '{found}'"
            self.errors.append(error)
            raise SyntaxError(error)
    
    def parse(self) -> ProgramNode:
        """Mulai parsing"""
        statements = []
        while self.current_token() and self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        if self.errors:
            print("\n❌ ERROR SINTAKSIS:")
            for error in self.errors:
                print(f"  {error}")
            raise SyntaxError("Parsing gagal")
        
        return ProgramNode(statements)
    
    def parse_statement(self):
        """Parsing satu statement"""
        token = self.current_token()
        
        if token.type == TokenType.WHILE:
            return self.parse_while_loop()
        elif token.type == TokenType.IDENTIFIER:
            next_token = self.peek_next_token()
            if next_token and next_token.type == TokenType.ASSIGN:
                return self.parse_assignment()
            else:
                self.errors.append(f"Error di baris {token.line}: Diharapkan assignment")
                self.current_pos += 1
                return None
        else:
            self.current_pos += 1
            return None
    
    def parse_while_loop(self) -> WhileLoopNode:
        """Parsing while loop"""
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        body = []
        while self.current_token() and self.current_token().type != TokenType.RBRACE:
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
        self.eat(TokenType.RBRACE)
        return WhileLoopNode(condition, body)
    
    def parse_assignment(self) -> AssignmentNode:
        """Parsing assignment"""
        identifier_token = self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        expression = self.parse_expression()
        self.eat(TokenType.SEMICOLON)
        return AssignmentNode(identifier_token.value, expression)
    
    def parse_expression(self) -> ASTNode:
        """Parsing expression"""
        left = self.parse_primary()
        
        token = self.current_token()
        if token and token.type in [TokenType.REL_OP, TokenType.ARITH_OP]:
            operator = token.value
            self.current_pos += 1
            right = self.parse_primary()
            return BinaryOpNode(operator, left, right)
        
        return left
    
    def parse_primary(self) -> ASTNode:
        """Parsing primary expression"""
        token = self.current_token()
        if token.type == TokenType.IDENTIFIER:
            self.current_pos += 1
            return IdentifierNode(token.value)
        elif token.type == TokenType.NUMBER:
            self.current_pos += 1
            return NumberNode(int(token.value))
        else:
            error = f"Error di baris {token.line}: Diharapkan identifier atau angka"
            self.errors.append(error)
            raise SyntaxError(error)
    
    def print_ast(self, node: ASTNode, indent: int = 0):
        """Mencetak AST dengan format pohon"""
        indent_str = "  " * indent
        
        if isinstance(node, ProgramNode):
            print("Program:")
            for stmt in node.statements:
                self.print_ast(stmt, indent + 1)
        
        elif isinstance(node, WhileLoopNode):
            print(f"{indent_str}While Loop:")
            print(f"{indent_str}  Kondisi:")
            self.print_ast(node.condition, indent + 2)
            print(f"{indent_str}  Body:")
            for stmt in node.body:
                self.print_ast(stmt, indent + 2)
        
        elif isinstance(node, AssignmentNode):
            print(f"{indent_str}Assignment: {node.identifier} =")
            self.print_ast(node.expression, indent + 1)
        
        elif isinstance(node, BinaryOpNode):
            print(f"{indent_str}Operasi: {node.operator}")
            print(f"{indent_str}  Kiri:")
            self.print_ast(node.left, indent + 2)
            print(f"{indent_str}  Kanan:")
            self.print_ast(node.right, indent + 2)
        
        elif isinstance(node, IdentifierNode):
            print(f"{indent_str}Variabel: {node.name}")
        
        elif isinstance(node, NumberNode):
            print(f"{indent_str}Angka: {node.value}")

# TAHAP 3: ANALISIS SEMANTIK

class SymbolTable:
    """Tabel simbol untuk menyimpan informasi variabel"""
    
    def __init__(self):
        self.symbols = {}
    
    def declare(self, name: str, var_type: str = "int"):
        """Mendeklarasikan variabel"""
        if name not in self.symbols:
            self.symbols[name] = {"type": var_type, "initialized": False}
            return True
        return False
    
    def lookup(self, name: str) -> bool:
        """Mengecek apakah variabel sudah dideklarasikan"""
        return name in self.symbols
    
    def set_initialized(self, name: str):
        """Menandai variabel sudah diinisialisasi"""
        if name in self.symbols:
            self.symbols[name]["initialized"] = True
    
    def is_initialized(self, name: str) -> bool:
        """Mengecek apakah variabel sudah diinisialisasi"""
        return self.symbols.get(name, {}).get("initialized", False)

class SemanticAnalyzer:
    """Menganalisis semantik: memeriksa logika program"""
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
    
    def analyze(self, node: ASTNode):
        """Mulai analisis semantik"""
        self.visit(node)
        
        if self.errors:
            print("\n❌ ERROR SEMANTIK:")
            for error in self.errors:
                print(f"  {error}")
            raise ValueError("Analisis semantik gagal")
        else:
            print("\n✅ Analisis Semantik: Tidak ada error")
    
    def visit(self, node: ASTNode):
        """Mengunjungi node AST"""
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.visit(stmt)
        
        elif isinstance(node, WhileLoopNode):
            self.visit(node.condition)
            for stmt in node.body:
                self.visit(stmt)
        
        elif isinstance(node, AssignmentNode):
            if not self.symbol_table.lookup(node.identifier):
                self.errors.append(f"Variabel '{node.identifier}' belum dideklarasikan")
            else:
                self.symbol_table.set_initialized(node.identifier)
            self.visit(node.expression)
        
        elif isinstance(node, BinaryOpNode):
            self.visit(node.left)
            self.visit(node.right)
        
        elif isinstance(node, IdentifierNode):
            if not self.symbol_table.lookup(node.name):
                self.errors.append(f"Variabel '{node.name}' belum dideklarasikan")
            elif not self.symbol_table.is_initialized(node.name):
                self.errors.append(f"Variabel '{node.name}' belum diinisialisasi")
        
        elif isinstance(node, NumberNode):
            pass
    
    def print_symbol_table(self):
        """Mencetak tabel simbol"""
        print("\n" + "="*60)
        print("TABEL SIMBOL")
        print("="*60)
        print(f"{'Variabel':<15} {'Tipe':<10} {'Terinisialisasi':<15}")
        print("-"*60)
        for name, info in self.symbol_table.symbols.items():
            print(f"{name:<15} {info['type']:<10} {str(info['initialized']):<15}")
        print("="*60)

# TAHAP 4: GENERASI THREE-ADDRESS CODE

class TACGenerator:
    """Menghasilkan Three-Address Code"""
    
    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
    
    def new_temp(self) -> str:
        """Membuat temporary variable baru"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self) -> str:
        """Membuat label baru"""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    def generate(self, node: ASTNode) -> List[str]:
        """Menghasilkan TAC dari AST"""
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        
        for stmt in node.statements:
            self.visit(stmt)
        
        return self.instructions
    
    def visit(self, node: ASTNode):
        """Mengunjungi node dan menghasilkan TAC"""
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.visit(stmt)
            return None
        
        elif isinstance(node, WhileLoopNode):
            start_label = self.new_label()
            end_label = self.new_label()
            
            self.instructions.append(f"{start_label}:")
            cond_var = self.visit(node.condition)
            self.instructions.append(f"ifFalse {cond_var} goto {end_label}")
            
            for stmt in node.body:
                self.visit(stmt)
            
            self.instructions.append(f"goto {start_label}")
            self.instructions.append(f"{end_label}:")
            return None
        
        elif isinstance(node, AssignmentNode):
            expr_var = self.visit(node.expression)
            if expr_var:
                self.instructions.append(f"{node.identifier} = {expr_var}")
            return None
        
        elif isinstance(node, BinaryOpNode):
            left_var = self.visit(node.left)
            right_var = self.visit(node.right)
            result = self.new_temp()
            
            op_map = {
                '<': 'LT', '>': 'GT', '<=': 'LE', '>=': 'GE',
                '==': 'EQ', '!=': 'NE',
                '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'
            }
            
            tac_op = op_map.get(node.operator, node.operator)
            self.instructions.append(f"{result} = {left_var} {tac_op} {right_var}")
            return result
        
        elif isinstance(node, IdentifierNode):
            return node.name
        
        elif isinstance(node, NumberNode):
            return str(node.value)
        
        return None
    
    def print_tac(self):
        """Mencetak Three-Address Code"""
        print("\n" + "="*60)
        print("TAHAP 4: THREE-ADDRESS CODE (TAC)")
        print("="*60)
        for i, instr in enumerate(self.instructions, 1):
            print(f"{i:3}. {instr}")
        print("="*60)

# COMPILER UTAMA

class WhileCompiler:
    """Compiler utama yang menggabungkan semua tahapan"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens = []
        self.ast = None
        self.tac = []
    
    def compile(self):
        """Menjalankan seluruh proses kompilasi"""
        print("\n" + "="*70)
        print("PROSES KOMPILASI - WHILE LOOP")
        print("="*70)
        print(f"\nKODE SUMBER:\n{self.source_code}\n")
        
        # Tahap 1: Leksikal
        lexer = LexicalAnalyzer(self.source_code)
        self.tokens = lexer.tokenize()
        lexer.print_tokens(self.tokens)
        
        # Tahap 2: Sintaksis
        parser = Parser(self.tokens)
        self.ast = parser.parse()
        
        print("\n" + "="*60)
        print("TAHAP 2: ANALISIS SINTAKSIS (AST)")
        print("="*60)
        parser.print_ast(self.ast)
        
        # Tahap 3: Semantik
        semantic = SemanticAnalyzer()
        # Deklarasikan variabel (simulasi)
        semantic.symbol_table.declare("x")
        semantic.symbol_table.declare("y")
        semantic.symbol_table.declare("i")
        semantic.symbol_table.set_initialized("x")
        semantic.symbol_table.set_initialized("y")
        
        print("\n" + "="*60)
        print("TAHAP 3: ANALISIS SEMANTIK")
        print("="*60)
        semantic.analyze(self.ast)
        semantic.print_symbol_table()
        
        # Tahap 4: TAC
        tac_gen = TACGenerator()
        self.tac = tac_gen.generate(self.ast)
        tac_gen.print_tac()
        
        return {
            "tokens": self.tokens,
            "ast": self.ast,
            "tac": self.tac
        }
        
# PROGRAM UTAMA

def main():
    """Program utama untuk menjalankan compiler"""
    
    # Contoh kode yang akan dikompilasi
    source_code = """
    while (x < 10) {
        y = y + 1;
        x = x + 1;
    }
    """
    
    # Buat compiler dan jalankan
    compiler = WhileCompiler(source_code)
    
    try:
        result = compiler.compile()
        
        # Tampilkan ringkasan
        print("\n" + "="*70)
        print("RINGKASAN HASIL KOMPILASI")
        print("="*70)
        print(f"✓ Jumlah Token: {len(result['tokens'])}")
        print(f"✓ AST: Berhasil dibentuk")
        print(f"✓ Instruksi TAC: {len(result['tac'])}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERROR KOMPILASI: {e}")

# Jalankan program
if __name__ == "__main__":
    main()