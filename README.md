

**Building a Flask API with LangChain and Azure OpenAI**

This project demonstrates how to build a Flask API that integrates with LangChain and Azure OpenAI. The API allows users to interact with a language model through various endpoints. The main components of the project are as follows:

1. **Import Necessary Libraries**: 
   - Flask for building the API.
   - AzureChatOpenAI and ChatPromptTemplate from LangChain for interacting with the OpenAI API.
   - `dotenv` for loading environment variables.
   - Other standard libraries like `os`, `datetime`, and `uuid`.

2. **Environment Variable Configuration**:
   - Loads environment variables from a `.env` file.
   - Validates the presence of required environment variables for Azure OpenAI.

3. **Initialize Azure OpenAI Model**:
   - Creates an instance of `AzureChatOpenAI` with specified parameters.
   - Handles errors during initialization.

4. **Prompt Template and Chain Creation**:
   - Defines a prompt template using `ChatPromptTemplate`.
   - Combines the prompt template and language model into a processing pipeline.

5. **Define API Endpoints**:
   - `/ask`: Accepts a POST request with a question and session ID, processes the question using the language model, and returns the response.
   - `/history`: Retrieves the chat history for a specific session.
   - `/sessions`: Lists all active session IDs.
   - `/generate-session`: Generates a new session ID.
   - `/clear-all-history`: Clears the chat history for all sessions.

6. **Running the app.py program will**:
   - Starts the Flask server on port 3000, binding to all network interfaces.

The API allows for managing chat sessions, storing chat history, and interacting with the Azure OpenAI model through structured prompts.
