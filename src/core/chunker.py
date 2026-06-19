import re
from typing import List,Dict,Any


# class SlidingWindowChunker :
#     '''Splits the continuous text streams into deterministic , verlapping segments to preserve semantic context across chunk boundaries. '''
    
#     def __init__(self, chunk_size: int , chunk_overlap: int):
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap
        
#         if self.chunk_overlap >= self.chunk_size :
#             raise ValueError("CHUNK_OVERLAP must be strictly less than CHUNK_SIZE.")
        
#     def clean_whitespace(self,text:str) -> str:
#         ''' To remove duplicate spaces,newlines,and carriage returns.'''
#         return " ".join(text.split())
    
#     def split_text(self, text:str , metadata: Dict[str, Any]) -> List[Dict[str, Any]] :
#         ''' Execution of the sliding window algorithm over a string input
            
#             Time Complexity : O(N) where N is the number of words in the text. '''
#         cleaned_text = self.clean_whitespace(text)
#         words = cleaned_text.split(" ")
#         total_words = len(words)
        
#         chunks = []
#         start_idx = 0
#         chunk_sequence = 0
        
#         if total_words <= self.chunk_size :
#             chunks.append(
#                 {
#                     "chunk_id" : f"{metadata.get('source_file')}_ch_{chunk_sequence}",
#                     "text" : cleaned_text,
#                     "metadata" : metadata
#                 }
#             )
#             return chunks
        
#         while start_idx < total_words :
#             end_idx = start_idx + self.chunk_size
#             chunk_words = words[start_idx:end_idx]
            
#             chunk_text = " ".join(chunk_words)
            
#             chunk_entry = {
#                 "chunk_id" : f"{metadata.get('source_file')}_ch_{chunk_sequence}",
#                 "text" : chunk_text,
#                 "metadata" : {
#                     **metadata,
#                     "word_count" : len(chunk_words),
#                     "start_word_index" : start_idx
#                 }
#             }
            
#             chunks.append(chunk_entry)
            
            
#             start_idx += (self.chunk_size - self.chunk_overlap)
#             chunk_sequence += 1
            
#         return chunks


class SemanticChunker:
    '''Intelligently splits text by semantic boundaries (paragraphs and sentences)
    rather than arbitrary character counts to prevent context destruction.'''
    
    def __init__(self,max_chunk_size : int = 1000 , overlap_size:int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size  = overlap_size
        
    def chunk_text(self,text:str,source_metadata:Dict[str,Any]) -> List[Dict[str,Any]] :
        
        text =text.replace('\r\n','\n')
        
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            
            if len(current_chunk) + len(p) + 2 > self.max_chunk_size and current_chunk :
                chunks.append(self._finalize_chunk(current_chunk,source_metadata))
                current_chunk = self._get_overlap(current_chunk)
            
            if len(p) > self.max_chunk_size:
                sentences = re.split(r'(?<=[.!?])\s+',p)
                for sentence in sentences :
                    if len(current_chunk) + len(sentence) + 1 > self.max_chunk_size and current_chunk :
                        chunks.append(self._finalize_chunk(current_chunk,source_metadata))
                        current_chunk = self._get_overlap(current_chunk)
            else:
                current_chunk += p + '\n\n'
                
         # to capture the leftover text remaining .   
        if current_chunk.strip():
            chunks.append(self._finalize_chunk(current_chunk,source_metadata))
            
        return chunks
    
    def _finalize_chunk(self,text :str , metadata:Dict[str,Any]) -> Dict[str,Any] :
        """Packages the text and metadata cleanly."""
        return {
            "text": text.strip(),
            "metadata": metadata
        }
    
    def _get_overlap(self, text: str) -> str:
        """Extracts the last complete sentences to carry over into the next chunk."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        overlap_text = ""
        
        for s in reversed(sentences):
            if len(overlap_text) + len(s) > self.overlap_size:
                break
            overlap_text = s + " " + overlap_text
            
        return overlap_text.strip() + " " if overlap_text else ""

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
    
