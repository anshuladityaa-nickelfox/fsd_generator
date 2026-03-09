import traceback
import groq
import google.generativeai as genai

class GroqClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = groq.Groq(api_key=api_key) if api_key else None
        
    def generate(self, prompt, system_prompt):
        if not self.client:
            raise ValueError("Groq API key not provided.")
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.2,
                response_format={"type": "json_object"} if "You MUST output ONLY a valid JSON object" in system_prompt else None
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            raise e

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=None  # Can be passed in generation or init in latest SDK, but we wrap below
            )
        else:
            self.model = None

    def generate(self, prompt, system_prompt):
        if not self.model:
            raise ValueError("Gemini API key not provided.")
        # Construct full prompt with system prepended as standard fallback if system_instruction is tricky
        full_prompt = f"System Instructions: {system_prompt}\n\nTask:\n{prompt}"
        try:
            # Depending on SDK version, we can use model.generate_content
            response = self.model.generate_content(full_prompt)
            if not response.parts:
                 return response.text
            return response.text
        except Exception as e:
             # Wait and try once more or raise
             print(f"Gemini API Error: {e}")
             raise e

class AutoClient:
    def __init__(self, groq_key, gemini_key):
        self.groq_key = groq_key
        self.gemini_key = gemini_key

    def generate(self, prompt, system_prompt):
        last_error = ""
        # Try Groq first
        if self.groq_key:
            try:
                client = GroqClient(self.groq_key)
                return client.generate(prompt, system_prompt)
            except Exception as e:
                last_error += f"Groq Error: {e}\n"
                
        # Fallback to Gemini
        if self.gemini_key:
            try:
                client = GeminiClient(self.gemini_key)
                return client.generate(prompt, system_prompt)
            except Exception as e:
                last_error += f"Gemini Error: {e}\n"
                
        raise ValueError(f"Generation failed. Errors:\n{last_error}")
