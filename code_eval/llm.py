import requests
import logging

# 设置日志的配置：日志级别为INFO，日志格式包括时间戳、日志级别和日志消息
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseLLM:
    def __init__(self, model_name, options={}):
        self.model_name = model_name
        self.options = options

    def generate(self, prompt):
        raise NotImplementedError("This method should be implemented by subclasses.")

class Starcoder2LLM(BaseLLM):
    def __init__(self, model_name, options={}):
        llm_options = {
            "stop": ["\n","<fim_prefix>","<fim_suffix>","<fim_middle>","<|endoftext|>","<file_sep>"]
        }
        # 将llm_options合并到options中
        options.update(llm_options)
        super().__init__(model_name, options)

    def generate(self, prompt):
        url = "http://127.0.0.1:11434/api/generate"
        headers = {'Content-Type': 'application/json'}       
        data = {
            "model": self.model_name,
            "prompt": f"<fim_prefix>{prompt}<fim_suffix><fim_middle>",
            "options": self.options,
            "stream": False
        }
        logging.info(f"开始调用Ollama模型====")
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"调用模型结束，获取结果====")
        if response.status_code == 200:
            response_data = response.json()
            if 'response' in response_data:
                return response_data['response']
            else:
                print("No 'response' in response.")
                return None
        else:
            print("Error calling ollama:", response.text)
            return None

class XinferenceLLM(BaseLLM):
    def __init__(self, model_name, options={}):
        llm_options = {
            "stop": ["\n","<fim_prefix>","<fim_suffix>","<fim_middle>","<|endoftext|>","<file_sep>"]
        }
        # 将llm_options合并到options中
        options.update(llm_options)
        super().__init__(model_name, options)

    def generate(self, prompt):
        url = "http://aiptes.vanke.com/qwen/v1/completions"
        headers = {'Content-Type': 'application/json'}       
        data = {
            "model": self.model_name,
            "prompt": f"<fim_prefix>{prompt}<fim_suffix><fim_middle>",
            # "options": self.options,
            "stream": False
        }
        data.update(self.options)

        logging.info(f"开始调用Xinference模型====")
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"调用模型结束，获取结果====")
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data:
                return response_data['choices'][0]['text']
            else:
                print("No 'response' in response.")
                return None
        else:
            print("Error calling ollama:", response.text)
            return None

class CodeGemmaLLM(BaseLLM):
    def __init__(self, model_name, options={}):
        llm_options = {
            "stop": ["\n","<|fim_prefix|>","<|fim_suffix|>","<|fim_middle|>","<|endoftext|>","<|file_separator|>"]
        }
        # 将llm_options合并到options中
        options.update(llm_options)
        super().__init__(model_name, options)

    def generate(self, prompt):
        url = "http://127.0.0.1:11434/api/generate"
        headers = {'Content-Type': 'application/json'}       
        data = {
            "model": self.model_name,
            "prompt": f"<|fim_prefix|>{prompt}<|fim_middle|>",
            "options": self.options,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            if 'response' in response_data:
                return response_data['response']
            else:
                print("No 'response' in response.")
                return None
        else:
            print("Error calling ollama:", response.text)
            return None
