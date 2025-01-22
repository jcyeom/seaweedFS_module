from langchain.llms import BaseLLM
import requests

class OllamaLLM(BaseLLM):
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        self.model = model

    def _call(self, prompt: str, stop=None, **kwargs):
        url = f"{self.endpoint}/api/models/{self.model}/completion"
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "stop": stop,
            **kwargs
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        return response.json()["text"]

    @property
    def _llm_type(self):
        return "ollama"

# Ollama 연결
ollama_llm = OllamaLLM(endpoint="http://<docker_host>:11434", model="llama")
response = ollama_llm("안녕하세요! 어떻게 도와드릴까요?")
print(response)