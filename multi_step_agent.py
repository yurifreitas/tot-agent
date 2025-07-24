import os
import re
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_openai import AzureChatOpenAI
from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
from mcp import StdioServerParameters
from acp_sdk.server import create_app
from acp_sdk.server.agent import agent
from acp_sdk.models import Message, MessagePart
from fastapi.middleware.cors import CORSMiddleware
from collections.abc import AsyncGenerator
from typing import TypedDict

load_dotenv()
barcode_server = StdioServerParameters(command="uv", args=["run", "info_reader_server.py"])
class AgentState(TypedDict):
    input: str
    intent: str
    subintent: str
    thought: str
    raw_thought: str
    commands: list[str]
    final_thought: str

# Azure OpenAI settings
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version=AZURE_VERSION,
    deployment_name=AZURE_DEPLOYMENT,
    temperature=0.3
)


# Prompts
intent_prompt = PromptTemplate.from_template("""
Classifique a intenção geral da seguinte mensagem:
"{input}"

Responda com uma única palavra: info_extract, duvida, mercado
""")

subintent_prompt = PromptTemplate.from_template("""
Baseado na intenção "{intent}" e na mensagem "{input}", qual é a sub-intenção mais específica?
""")

expansion_prompts = {
    "info_extract": PromptTemplate.from_template("""
Usuário disse: "{input}"

Crie um pensamento que possivelmente contenha comandos como #extract_info_from_image(url)
"""),
    "duvida": PromptTemplate.from_template("""
Usuário disse: "{input}"

Responda com um pensamento informativo. Pode usar #get_balance.
"""),
    "mercado": PromptTemplate.from_template("""
Usuário disse: "{input}"

Forneça um pensamento sobre mercado. Pode usar #get_price("BTCUSDT")
""")
}

def chain_runner(template, output_key):
    return template | llm | (lambda x: {output_key: x.content.strip()})

intent_chain = chain_runner(intent_prompt, "intent")
subintent_chain = chain_runner(subintent_prompt, "subintent")
expansion_chains = {k: chain_runner(v, "thought") for k, v in expansion_prompts.items()}

def expand(state):
    intent = state["intent"]
    return expansion_chains[intent].invoke(state)

def extract_mcp_calls(state):
    thought = state["thought"]
    cmds = re.findall(r"#\w+(\\(.*?\\))?", thought)
    return {
        "raw_thought": thought,
        "commands": cmds,
        "final_thought": thought
    }

graph = StateGraph(AgentState)

graph.add_node("classify_intent", intent_chain)
graph.add_node("define_subintent", subintent_chain)
graph.add_node("expand_thought", RunnableLambda(expand))
graph.add_node("extract_mcp", RunnableLambda(extract_mcp_calls))

graph.set_entry_point("classify_intent")
graph.add_edge("classify_intent", "define_subintent")
graph.add_edge("define_subintent", "expand_thought")
graph.add_edge("expand_thought", "extract_mcp")
graph.set_finish_point("extract_mcp")

flow = graph.compile()

# ACP Agent
model = LiteLLMModel(
    model_id="ollama_chat/phi4",
    api_base="http://localhost:11434",
    num_ctx=8192,
)

@agent(name="multi_step_agent", description="Agente Tree of Thoughts com ferramentas MCP")
async def multi_step_agent(input: list[Message], context) -> AsyncGenerator:
    user_input = input[0].parts[0].content
    result = flow.invoke({"input": user_input})
    raw = result["raw_thought"]
    commands = result["commands"]

    if commands:
        with ToolCollection.from_mcp(barcode_server, trust_remote_code=True) as tools:
            tc_agent = ToolCallingAgent(tools=[*tools.tools], model=model)
            result = tc_agent.run(input[0].parts[0].content)
            yield Message(parts=[MessagePart(content=result)])
    else:
        yield Message(parts=[MessagePart(content=raw)])


