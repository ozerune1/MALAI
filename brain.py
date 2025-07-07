import os
from langchain import hub
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langchain_google_vertexai.model_garden import ChatAnthropicVertex
from langchain_google_vertexai.model_garden_maas.llama import VertexModelGardenLlama
from langchain_google_vertexai.model_garden_maas.mistral import VertexModelGardenMistral
from langchain_google_vertexai.gemma import GemmaChatVertexAIModelGarden
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_aws import ChatBedrockConverse
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFacePipeline
from transformers import BitsAndBytesConfig
from langchain.agents import create_react_agent, AgentExecutor
from dotenv import load_dotenv
from api import refresh_access_token, search_anime, anime_details, ranked_anime, seasonal_anime, get_user_anime_list, update_anime_list, delete_anime_from_list, user_details, search_manga, manga_details, ranked_manga, get_user_manga_list, update_manga_list, delete_manga_from_list, get_forum_boards, get_forum_topics, read_forum_topic

def MALAI(query, provider, model, hf_model):

    load_dotenv()

    if provider == "Ollama":
        llm = ChatOllama(
            base_url=os.getenv("OLLAMA_HOST"),
            model=model
        ) 

    if provider == "Groq":
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        llm = ChatGroq(
            model=model
        )    

    if provider == "Gemini":
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    
    if provider == "Vertex":
        llm = ChatVertexAI(
            model_name=model
        )

    if provider == "Vertex Anthropic":
        llm = ChatAnthropicVertex(
            model=model
        )

    if provider == "Vertex Llama":
        llm = VertexModelGardenLlama(
            model=model
        )
    
    if provider == "Vertex Mistral":
        llm = VertexModelGardenMistral(
            model=model
        )
    
    if provider == "Vertex Gemma":
        llm = GemmaChatVertexAIModelGarden(
            model_name=model
        )

    if provider == "Azure OpenAI":
        llm = AzureChatOpenAI(
            azure_deployment=model,
            api_version="2025-01-01-preview"
        )

    if provider == "Azure":
        llm = AzureAIChatCompletionsModel(
        endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT"),
        credential=os.getenv("AZURE_FOUNDRY_API_KEY"),
        model=model,
        api_version="2024-05-01-preview"
    )
        
    if provider == "AWS On Demand" or provider == "AWS Inference":
        llm = ChatBedrockConverse(
            model_id=model
        )
    
    if provider == "OpenAI":
        llm = ChatOpenAI(
            model_name=model
        )

    if provider == "Anthropic":
        llm = ChatAnthropic(
            model=model
        )
    
    if provider == "Mistral":
        llm = ChatMistralAI(
            model=model
        )

    if provider == "HuggingFace Endpoint":
        endpoint = HuggingFaceEndpoint(
            repo_id=model
        )

        llm = ChatHuggingFace(
            llm=endpoint
        )

    if provider == "HuggingFace Local":
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4"
        )
        llm = HuggingFacePipeline.from_model_id(
            model_id=model,
            task="text-generation",
            model_kwargs={
                "quantization_config": quant_config
            }
        )

    prompt = hub.pull("hwchase17/react")
    tools = [refresh_access_token, search_anime, anime_details, ranked_anime, seasonal_anime, get_user_anime_list, update_anime_list, delete_anime_from_list, user_details, search_manga, manga_details, ranked_manga, get_user_manga_list, update_manga_list, delete_manga_from_list, get_forum_boards, get_forum_topics, read_forum_topic]

    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=False)

    response = agent_executor.invoke({
        "input": query
    })

    return response["output"]