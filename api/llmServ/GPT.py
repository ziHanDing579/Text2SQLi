from openai import OpenAI

class GPT():
    def __init__(self, key):
        self.openai = OpenAI(
            api_key = key,
            )
        
    def send_prompt(self, prompt, model, max_tokens):
        pass
    
    
    