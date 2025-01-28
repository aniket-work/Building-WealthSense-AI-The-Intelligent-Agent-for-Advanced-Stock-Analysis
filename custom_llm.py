from typing import Optional, List, Any, Dict
import ollama

class OllamaLLM:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self._verbose = True

    def create_chat_completion(self, prompt: str, **kwargs) -> str:
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            print(f"Ollama chat completion error: {e}")
            return str(e)

    def complete(self, prompt: str, **kwargs) -> str:
        return self.create_chat_completion(prompt, **kwargs)

    def generate(self, prompts: List[str], **kwargs) -> List[str]:
        return [self.complete(prompt, **kwargs) for prompt in prompts]

    def __call__(self, prompt: str, **kwargs) -> str:
        return self.complete(prompt, **kwargs)

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, value: str):
        self._model_name = value