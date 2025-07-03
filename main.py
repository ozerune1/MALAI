import os
from dotenv import load_dotenv
import gradio as gr
from brain import MALAI
from models import groq_models, ollama_models, gemini_models, vertex_models, vertex_anthropic_models, vertex_llama_models, vertex_mistral_models, vertex_gemma_models, azure_openai_models, azure_models, aws_demand_models, aws_inference_models, openai_models, anthropic_models, mistral_models

load_dotenv()

providers = []

if os.getenv("OLLAMA_HOST"):
   providers.append("Ollama")

if os.getenv("GROQ_API_KEY"):
   providers.append("Groq")

if os.getenv("GEMINI_API_KEY"):
   providers.append("Gemini")

if os.getenv("vertex-creds.json"):
   if len(vertex_models) > 0:
      providers.append("Vertex")
   if len(vertex_anthropic_models) > 0:
      providers.append("Vertex Anthropic")
   if len(vertex_llama_models) > 0:
      providers.append("Vertex Llama")
   if len(vertex_mistral_models) > 0:
      providers.append("Vertex Mistral")
   if len(vertex_gemma_models) > 0:
      providers.append("Vertex Gemma")
if os.getenv("AZURE_OPENAI_ENDPOINT"):
   providers.append("Azure OpenAI")
if os.getenv("AZURE_INFERENCE_ENDPOINT"):
   providers.append("Azure")
if os.getenv("AWS_ACCESS_KEY_ID"):
   providers.append("AWS On Demand")
   providers.append("AWS Inference")
if os.getenv("OPENAI_API_KEY"):
   providers.append("OpenAI")
if os.getenv("ANTHROPIC_API_KEY"):
   providers.append("Anthropic")
if os.getenv("MISTRAL_API_KEY"):
   providers.append("Mistral")
if os.getenv("HUGGINGFACEHUB_API_TOKEN"):
   providers.append("HuggingFace Endpoints")
   providers.append("HuggingFace Local")

providers.sort()

def update_models(provider):
   if provider == "Groq":
      return gr.Dropdown(choices=groq_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Ollama":
      return gr.Dropdown(choices=ollama_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Gemini":
      return gr.Dropdown(choices=gemini_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Vertex":
      return gr.Dropdown(choices=vertex_models, value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Vertex Anthropic":
      return gr.Dropdown(choices=vertex_anthropic_models, value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Vertex Llama":
      return gr.Dropdown(choices=vertex_llama_models, value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Vertex Mistral":
      return gr.Dropdown(choices=vertex_mistral_models, value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Vertex Gemma":
      return gr.Dropdown(choices=vertex_gemma_models, value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Azure OpenAI":
      return gr.Dropdown(choices=azure_openai_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Azure":
      return gr.Dropdown(choices=azure_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "AWS On Demand":
      return gr.Dropdown(choices=aws_demand_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "AWS Inference":
      return gr.Dropdown(choices=aws_inference_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "OpenAI":
      return gr.Dropdown(choices=openai_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Anthropic":
      return gr.Dropdown(choices=anthropic_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "Mistral":
      return gr.Dropdown(choices=mistral_models(), value=None, interactive=True, visible=True), gr.Textbox(label="Model", visible=False)
   elif provider == "HuggingFace Endpoints":
      return gr.Dropdown([], value=None, interactive=False, visible=False), gr.Textbox(label="Model", visible=True, interactive=True)
   elif provider == "HuggingFace Local":
      return gr.Dropdown([], value=None, interactive=False, visible=False), gr.Textbox(label="Model", visible=True, interactive=True)

with gr.Blocks() as demo:
   with gr.Row():
      provider = gr.Dropdown(providers, label="Provider", value=None)
      model = gr.Dropdown([], label="Model", interactive=False)
      hf_model = gr.Textbox(label="Model", visible=False)
   query = gr.Textbox(label="Input")
   output = gr.Textbox(label="Output")
   send = gr.Button("Send")

   provider.change(
      fn=update_models,
      inputs=provider,
      outputs=[model, hf_model]
   )

   send.click(fn=MALAI, inputs=[query, provider, model, hf_model], outputs=output, api_name="send")
   query.submit(fn=MALAI, inputs=[query, provider, model, hf_model], outputs=output, api_name="send")

if __name__ == "__main__":
   demo.launch(share=True)
