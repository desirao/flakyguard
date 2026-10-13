"""Test AST-aware code chunking module."""

from tools.rag.chunking import ASTChunker, CodeChunk


def test_chunk_simple_function():
    code = '''
def calculate_tax(amount: float, rate: float = 0.18) -> float:
    """Calculate the tax amount based on gross value."""
    return amount * rate
'''
    chunker = ASTChunker()
    chunks = chunker.chunk_code(code, file_path="finance.py")
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.name == "calculate_tax"
    assert chunk.chunk_type == "function"
    assert "amount" in chunk.parameters
    assert "rate" in chunk.parameters
    assert "Calculate the tax" in chunk.docstring
    assert chunk.start_line == 2


def test_chunk_class_with_methods():
    code = '''
class PaymentProcessor:
    """Handles external transaction billing."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def charge(self, amount: float) -> bool:
        """Execute charge transaction."""
        return True
'''
    chunker = ASTChunker()
    chunks = chunker.chunk_code(code, file_path="processor.py")
    # 1 class chunk + 2 method chunks
    assert len(chunks) == 3
    names = [c.name for c in chunks]
    assert "PaymentProcessor" in names
    assert "__init__" in names
    assert "charge" in names

    # Verify method metadata
    charge_chunk = next(c for c in chunks if c.name == "charge")
    assert charge_chunk.parent_class == "PaymentProcessor"
    assert charge_chunk.chunk_type == "method"


def test_chunk_syntax_error_fallback():
    broken_code = "def invalid_syntax(:"
    chunker = ASTChunker()
    chunks = chunker.chunk_code(broken_code, file_path="broken.py")
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "raw_block"
    assert chunks[0].content == broken_code
