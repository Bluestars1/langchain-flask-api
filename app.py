#Building a Flask API with LangChain and Azure OpenAI Part1
#Import necessary libraries
from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import datetime
import uuid

"""
    These import provide: - Flask: The web framework for building our API
    request and jsonify: These are used to handle incoming requests and send responses
    AzureChatOpenAI: This is the class that handles the interaction with the OpenAI API this is LangChains interface in this case to Azure OpenAI
    ChatPromptTemplate: For creating structured prompts for the OpenAI API
    load_dotenv: For loading environment variables from a .env file
    os: For accessing environment variables
"""
# Load environment variables from .env file
load_dotenv()
    
#Create an instance of the Flask class - Initialize Flask app
app = Flask(__name__)
"""
        This code loads environment variables from our .env file and creates an new instance of the Flask class. 
        The Flask class is the main class in the Flask web framework. It creates a new Flask application instance.
        It is used to create web applications in Python.
"""
# Initialized chat history storage with session ID
chat_histories = {}
MAX_HISTORY_LENGTH=10

# Section 1: Define the API routes - Configure and Validate Azure OpenAI Environment Variables
required_vars = {
    "AZURE_OPENAI_API_KEY": "API key",
    "AZURE_OPENAI_ENDPOINT": "endpoint",
    "AZURE_OPENAI_API_VERSION": "API version",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "Deployment name"
}
for var, desc in required_vars.items():
    if not os.getenv(var):
        raise ValueError(f"Missing {desc} in environment variables. Check your .env file.") 
"""
    This code checks if all the required environment variables  are set for the Azure OpenAI API are set. 
    If any of the required environment variables are missing, an error is raised with a helpful message.
    
"""
 # Section 2: Initialize the Azure OpenAI Model with LangChain - an instance of the AzureChatOpenAI class
try:
    llm = AzureChatOpenAI(
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        temperature=0.7,
        max_tokens=500
        )
except Exception as e:
        raise RuntimeError(f"Failed to initialize AzureChatOpenAI: {str(e)}") 
"""
    This code initializes the Azure OpenAI model with LangChain.
    It Creates and instance of AzureChatOpenAI with our Azure OpenAI credentials
    Sets temperature to 0.7 for balance of creativity and consistency
    Limits responses to 500 tokens
    Includes error handling to provide clear feedback if initialization fails
 """
 # Section 3: Create a simple prompt template for our AI:Define the API routes - Create a route for the chat endpoint
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant providing concise and accurate answers. Maintain context from the conversation history"),
    ("human", "{question}")
    ])

"""
    This template: Sets a system message that defines the AI's behavior - 
    Creates a placeholder for the user's question.

"""
# Section 4: Create a simple chain that combines our prompt template and language model
chain = prompt_template | llm

"""
    This code creates a processing pipeline that 
    1. Takes the user's question
    2. Formats it using our prompt template 3.
    3. Sends it to the language model 4.
    4. Returns the model's response
"""
# Section 5: Define the REST API Endpoint
@app.route('/ask', methods=['POST'])
def ask_question():
        
    """
    REST API endpoint to ask a question to GPT-4o.
    Expects a JSON payload with a question field and a session id.
    Returns the model's response as JSON.
    """
    global chat_histories

    try:
        # Get JSON data from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # Extract the question from the request
        question = data['question']
        session_id = data.get('session_id', 'default_session')
        print(f"Question received from session {session_id}: {question}")
        #Initialize chat history for the session if it doesn't exist
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        #Get the chat history for this session
        session_history = chat_histories[session_id]


        # Create context from chat history
        context = ""
        if session_history:
           context = "previous conversation:\n"
           for entry in session_history:
               context += f"Human: {entry['question']}\nAI: {entry['answer']}\n"

        # Prepare the question with context if there's history
        contextualized_question = question
        if context:
            contextualized_question = f"{context}Human: {question}"

        # Invoke the chain with the user's question
        response = chain.invoke({
            "question": contextualized_question
        })
        print(f"Response for session: {session_id}:{response.content}")
        #Update chat history
        chat_histories[session_id].append({
            "question": question,
            "answer": response.content,
            "timestamp": str(datetime.datetime.now())
        })

        # Limit chat history to MAX_HISTORY_LENGTH
        if len(chat_histories[session_id]) > MAX_HISTORY_LENGTH:
            chat_histories[session_id] = chat_histories[session_id:][-MAX_HISTORY_LENGTH:]
        # Return the model's response with history

        #  Return the model's response
        return jsonify({
            "answer": response.content,
            "status": "success",
            "session_id": session_id,
            "history":chat_histories[session_id]
        }), 200
    except KeyError as e:
        return jsonify({"error": f"KeyError: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500

"""
        This code accepts a POST request to  /ask that accepts a JSON payload with a question field.
       Validates that a question was provided
       Sends the question to our LangChain pipeline
       Returns the AI's response as JSON
       Includes error handling for various failure scenarios
"""      
# Add this new endpoint after the ask question function
@app.route('/history',methods=['GET'])
def get_history():

    """
    REST API endpoint to get the chat history for a specific session.
    Returns the chat history for the session as JSON.
    """
    session_id = request.args.get('session_id', 'default_session')
    if session_id not in chat_histories:
        return jsonify({
            "history": [],
            "count": 0,
            "session_id": session_id,
            "error": f"No chat history found for session {session_id}"
        }), 200

    return jsonify({
        "history": chat_histories[session_id],
        "count": len(chat_histories[session_id]),
        "session_id": session_id
    }), 200

@app.route('/sessions', methods=['GET'])
def get_sessions():
    """
    REST API endpoint to retrieve all active session IDs.
    Returns a list of all session IDs as JSON.
    """
    return jsonify({
        "sessions": list(chat_histories.keys()),
        "count": len(chat_histories)
    }), 200

@app.route('/generate-session' , methods=['GET'])
def generate_session():
    """
    REST API endpoint to generate a new session ID.
    Returns the new session ID as JSON.
    """
    new_session_id = str(uuid.uuid4())
    return jsonify({

        "session_id": new_session_id,
        "status": "success"
    }), 200

"""
Add this new endpoint to clear the chat history
Returns a confirmation message
"""
@app.route('/clear-all-history', methods=['POST'])
def clear_history():
    """
    REST API endpoint to clear the chat history.
    Returns a confirmation message.
    """
    global chat_histories
    session_count = len(chat_histories)
    chat_histories = []

    return jsonify({
        "message": f"Chat history cleared for all {session_count} sessions",
        "status": "success"
    }), 200

# Section 6: Run the Flask app
"""
This code Starts the Flask server on port 3000
Binds to all network interfaces(0.0.0.0)
Enable
"""
if __name__ == '__main__':
# Start the Flask server on port 3000
    app.run(host='0.0.0.0', port=3000, debug=True)




