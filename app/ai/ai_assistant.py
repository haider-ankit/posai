from langchain_aws import ChatBedrock
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

def ask_pos_ai(user_question):
    # Path to your database
    db = SQLDatabase.from_uri("sqlite:///database/posai.db")
    
    # Amazon Nova Micro
    llm = ChatBedrock(
        model_id="amazon.nova-micro-v1:0",
        region_name="us-east-1",
        model_kwargs={"temperature": 0}
    )
    
    # 'tool-calling' is the key here. It handles all prompt variables 
    # automatically and stops the 'Observation' infinite loop.
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling", 
        verbose=True
    )
    
    try:
        # We use a system message to guide its behavior without breaking the template
        query = f"Using the available tools, answer this question: {user_question}"
        response = agent_executor.invoke({"input": query})
        return response["output"]
    except Exception as e:
        return f"AI Error: {str(e)}"
    

ask_pos_ai("How many products are in stock?")