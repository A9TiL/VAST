import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class LLMService:
    """Handles all the communication with Groq inference engine."""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("[Error] GROQ_API_KEY us missing from the .env file")
        
        self.client= Groq(api_key=api_key)
        
        self.model = "llama-3.1-8b-instant"
        
    def generate_answer(self,query:str,context:str) ->str:
        """Takes the user's question and the database context, and asks the LLM to write an answer."""
        
        system_instruction = (
            "You are VAST, an expert technical assistant. "
            "Use ONLY the provided context to answer the user's question. "
            "Be concise, direct, and professional."
        )
        
        user_message = f"CONTEXT:\n{context}\n\nQUESTION: {query}"
        
        response = self.client.chat.completions.create(
            messages=[
                {"role" : "system" , "content" : system_instruction},
                {"role" : "user" , "content" : user_message}
            ],
            model=self.model,
            temperature=0.0,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
if __name__ == "__main__":
    print("[System] Booting up LLM Engine...")
    llm = LLMService()
    
    # testing with a fake context first
    test_query = "What color is the sky according to the context?"
    test_context = "The sky on planet VAST is a deep neon purple."
    
    print("\n[Query] Sending test prompt to Groq...")
    answer = llm.generate_answer(query=test_query, context=test_context)
    
    print("\n--- LLM Response ---")
    print(answer)