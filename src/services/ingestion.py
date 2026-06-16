import os
from pathlib import Path
from typing import List,Dict,Any
from config.settings import PRIMARY_REPO_DIR , SUPPORTED_EXTENSIONS

class DocumentDiscovery:
    '''
    Handles scanning the local storage layers to locate ,vaidate,and extract raw text fromm target domains.
    '''
    
    def __init__(self,target_dir : Path = PRIMARY_REPO_DIR):
        self.target_dir = target_dir
        
    def discover_files (self) -> List[Path] :
        ''' Scans the directory for valid extensions specified in config. '''
        
        valid_files = []
        
        if not self.target_dir.exists():
            print(f"[Warning] Target directory {self.target_directory} doesn't exist.")
            return valid_files
        
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                file_path = Path(root)/file
                if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                    valid_files.append(file_path)
                    
        return valid_files
    
    def extract_raw_documents(self) -> List[Dict[str,Any]] :
        '''Reads the file contents and store them with their metadata. '''
        file_paths = self.discover_files()
        raw_documents = []
        
        for path in file_paths :
            try :
                with open(path,"r" ,encoding="utf-8")  as f :
                    content = f.read()
                    
                document_entry = {
                    "source_file" : path.name,
                    "absolute_path" : str(path),
                    "raw_text" : content
                }
                
                raw_documents.append(document_entry)
                print(f"[Success] Successfully extracted data from : {path.name}")
            except Exception as e :
                print(f"[Error] Failed to read file {path.name} . Reason : {e}")
        return raw_documents
    
if __name__ == "__main__":
    discoverer = DocumentDiscovery ()
    docs = discoverer.extract_raw_documents()
    print(f"\nTotal documents loaded into memory : {len(docs)}\n")
    for doc in docs :
        print(f"source_file: {doc['source_file']}")
        print(f"text_content: {doc['raw_text']}\n" + "-"*40)