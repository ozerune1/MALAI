from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import time
from transformers import BitsAndBytesConfig
'''
print("Loading full model...")
start = time.perf_counter()
llm = HuggingFacePipeline.from_model_id(
    model_id="google/gemma-3-4b-it",
    task="text-generation"
)
full_load = time.perf_counter()

chat_model = ChatHuggingFace(llm=llm)

print("Invoking full model...")
start = time.perf_counter()
print(chat_model.invoke("Write me a poem").content)
full_invoke = time.perf_counter() - start
'''

print("Loading nf4 model...")
start = time.perf_counter()
quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4"
)
llm = HuggingFacePipeline.from_model_id(
    model_id="google/gemma-3-4b-it",
    task="text-generation",
    model_kwargs={
        "quantization_config": quant_config
    }
)
chat_model = ChatHuggingFace(llm=llm)
nf4_load = time.perf_counter()

print("Invoking nf4 model...")
start = time.perf_counter()
print(chat_model.invoke("Write me a poem").content)
nf4_invoke = time.perf_counter() - start

#print(f"Full: {full_load}")
print(f"NF4: {nf4_load} | {nf4_invoke}")