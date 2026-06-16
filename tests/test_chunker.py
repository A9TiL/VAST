import pytest
from src.core.chunker import SlidingWindowChunker

def test_chun_size_and_overlap_validation() :
    '''Test that invalid parameters raise a value error.'''
    with pytest.raises(ValueError):
        
        SlidingWindowChunker(chunk_size=10,chunk_overlap=10)
        
def test_clean_whitespaces():
    '''Test that erratic spacing and newline are normalized'''
    chunker = SlidingWindowChunker(chunk_size=10,chunk_overlap=2)
    raw_text = "This   has   \n  too   \t  much    space."
    cleaned = chunker.clean_whitespace(raw_text)
    
    assert cleaned == "This has too much space."
    
def test_split_text_logic():
    """Test the exact mathematical boundaries of the sliding window."""
    chunker = SlidingWindowChunker(chunk_size=5, chunk_overlap=2)
    metadata = {"source_file": "unit_test.txt"}
    

    text = "A B C D E F G H I"
    
    chunks = chunker.split_text(text, metadata)
    
    # Expected Chunk 1: A B C D E
    # Expected Chunk 2 (Overlap 2): D E F G H
    # Expected Chunk 3 (Overlap 2): G H I
    
    assert len(chunks) == 3
    assert chunks[0]["text"] == "A B C D E"
    assert chunks[1]["text"] == "D E F G H"
    assert chunks[2]["text"] == "G H I"
    
    # Test metadata inheritance
    assert chunks[0]["metadata"]["word_count"] == 5
    assert chunks[0]["metadata"]["source_file"] == "unit_test.txt"