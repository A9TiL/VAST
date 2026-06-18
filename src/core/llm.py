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
        """Takes the user's question and the database context, and asks the LLM to write an answer
        using strict data-extraction guardrails."""
        
        system_instruction = (
            """You are VAST, an enterprise data-extraction assistant.
        Your sole purpose is to answer the user's question based STRICTLY and EXCLUSIVELY on the provided CONTEXT.
        
        CRITICAL RULES:
        1. You must not use any outside knowledge, pre-training data, or assumptions.
        2. If the CONTEXT does not contain the answer, or if the CONTEXT is empty, you must reply EXACTLY with: "I'm sorry, but I don't have any documents in my vault to answer about this topic."
        3. Do not attempt to guess, infer, or provide partial answers outside the text.
        4. If the context contains the answer, be concise, professional, and directly address the user's question."""
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