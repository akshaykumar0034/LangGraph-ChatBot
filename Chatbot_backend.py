from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

class ChatState(TypedDict):
    
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):

    messages = state['messages']

    response = model.invoke(messages).content

    return {"messages": [AIMessage(content=response)]}


checkpointer = InMemorySaver()

graph = StateGraph(ChatState)

# Add Graph
graph.add_node("Chat Node", chat_node)

# Add Edge
graph.add_edge(START, "Chat Node")
graph.add_edge("Chat Node", END)

chatbot = graph.compile(checkpointer=checkpointer)


