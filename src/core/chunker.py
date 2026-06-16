from typing import List,Dict,Any


class SlidingWindowChunker :
    '''Splits the continuous text streams into deterministic , verlapping segments to preserve semantic context across chunk boundaries. '''
    
    def __init__(self, chunk_size: int , chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if self.chunk_overlap >= self.chunk_size :
            raise ValueError("CHUNK_OVERLAP must be strictly less than CHUNK_SIZE.")
        
    def clean_whitespace(self,text:str) -> str:
        ''' To remove duplicate spaces,newlines,and carriage returns.'''
        return " ".join(text.split())
    
    def split_text(self, text:str , metadata: Dict[str, Any]) -> List[Dict[str, Any]] :
        ''' Execution of the sliding window algorithm over a string input
            
            Time Complexity : O(N) where N is the number of words in the text. '''
        cleaned_text = self.clean_whitespace(text)
        words = cleaned_text.split(" ")
        total_words = len(words)
        
        chunks = []
        start_idx = 0
        chunk_sequence = 0
        
        if total_words <= self.chunk_size :
            chunks.append(
                {
                    "chunk_id" : f"{metadata.get('source_file')}_ch_{chunk_sequence}",
                    "text" : cleaned_text,
                    "metadata" : metadata
                }
            )
            return chunks
        
        while start_idx < total_words :
            end_idx = start_idx + self.chunk_size
            chunk_words = words[start_idx:end_idx]
            
            chunk_text = " ".join(chunk_words)
            
            chunk_entry = {
                "chunk_id" : f"{metadata.get('source_file')}_ch_{chunk_sequence}",
                "text" : chunk_text,
                "metadata" : {
                    **metadata,
                    "word_count" : len(chunk_words),
                    "start_word_index" : start_idx
                }
            }
            
            chunks.append(chunk_entry)
            
            
            start_idx += (self.chunk_size - self.chunk_overlap)
            chunk_sequence += 1
            
        return chunks
    

if __name__ == "__main__":
    mock_metadata = {"source_file" : "test_doc.txt"}
    sample_prose = ("One Two Three Four Five Six Seven Eight Nine Ten " "Eleven Twelve Thirteen Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty")
    
    test_chunker = SlidingWindowChunker(chunk_size=10,chunk_overlap=3)
    resulting_chunks = test_chunker.split_text(sample_prose,mock_metadata)
    
    print(f"Generated {len(resulting_chunks)} chunks: \n")
    for chunk in resulting_chunks:
        print(f"ID: {chunk['chunk_id']}")
        print(f"Content : {chunk['text']}")
        print(f"Metadata : {chunk['metadata']}\n" + "-"*40)
    
