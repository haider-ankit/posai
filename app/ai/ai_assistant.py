import io
from contextlib import redirect_stdout
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
        verbose=True # Keep verbose as True
    )
    
    try:
        # We use a system message to guide its behavior without breaking the template
        query = (
            f"Analyze the available database tables and their schema carefully. "
            f"Then, using the available tools, answer this question: {user_question}\n"
            f"Provide only the factual answer to the question, without any additional explanation, "
            f"conversational text, or internal thoughts."
        )
        
        # Redirect stdout to a StringIO object to capture the verbose output
        # This prevents it from being printed to the console.
        f = io.StringIO()
        with redirect_stdout(f):
            response = agent_executor.invoke({"input": query})
        
        # The captured verbose output is now in 'f.getvalue()' but is not printed.
        # You can choose to log 'f.getvalue()' to a file or discard it.

        return response["output"][0]["text"]
    except Exception as e:
        return f"AI Error: {str(e)}"
    

print(ask_pos_ai("What kinds of beverages are in stock?"))