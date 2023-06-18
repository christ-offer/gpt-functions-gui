import openai
import json
import logging
from typing import Optional, Dict, List, Tuple

from functions import function_params, wikidata_sparql_query, scrape_webpage, write_code_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

system_message = """PersonalAssistant {
  Constraints {
    You are incredibly intelligent and knowledgable
    You think step by step to make sure you have the right solution
    Before submitting SPARQL queries, make sure you fully understand the question
    You only use your functions when they are called
  }
  
  /python [idea] - Uses the python_repl function
  /wikidata [question] - Uses the wikidata_sparql_query function
  /scrape [url] - Uses the scrape_webpage function
  /write_code [idea] - Generates code for the idea, uses the write_code_file function
  /kb_create [content] - Uses the knowledgebase_create_entry function
  /kb_list - Uses the knowledgebase_list_entries function
  /kb_read [entry_name] - Uses the knowledgebase_read_entry function
  /csv [filename] - Uses the read_csv_columns function
  /help - Returns a list of all available functions
}
"""

system_message2 = """ResponseReader {
Role {
    You recive the responses from the functions PersonalAssistant has called and following your interfaces you return the results
}
Constraints {
    You are incredibly intelligent and knowledgable
    You follow the interfaces provided for your responses
}
interface wikidata_sparql_query {
    success?human_readable_result;
    fail?error;
}
interface scrape_webpage {
    success?full_text_content|user_specified;
    fail?error;
}
interface write_code_file  {
    sucess?only_filename;
    fail?error;
}
interface knowledgebase_create_entry[format=markdown] {
    sucess?filename;
    fail?error;
}
interface knowledgebase_list_entries {
    sucess?list;
    fail?error;
}
interface knowledgebase_read_entry {
    sucess?entry_content;
    fail?error;
}
interface read_csv_columns {
    sucess?list_column_names;
    fail?error;
}
interface python_repl {
    sucess?result|saved_file_name;
    fail?error;
}

"""

def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    conversation.append({"role": "system", "content": system_message})
    conversation.append({"role": "user", "content": prompt})
    # Replace this with your actual OpenAI secret key
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=conversation,
        functions=function_params,
        function_call="auto",
    )

    message = response["choices"][0]["message"]

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        logging.info(f"Function name: {function_name}")
        logging.info(f"Function arguments: {function_args}")

        if function_name == "python_repl":
            function_response = python_repl(function_args.get("code"))
        elif function_name in ["knowledgebase_create_entry", "knowledgebase_read_entry", 
                               "knowledgebase_update_entry", "knowledgebase_list_entries", 
                               "read_csv_columns", "write_code_file"]:
            function_response = globals()[function_name](*function_args.values())
        elif function_name == "wikidata_sparql_query":
            function_response = wikidata_sparql_query(function_args.get("query"))
        elif function_name == "scrape_webpage":
            function_response = scrape_webpage(function_args.get("url"))

        logging.info(f"Function response: {function_response}")
        
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": system_message2},
                {"role": "user", "content": prompt},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                },
            ],
        )
        conversation.append(second_response["choices"][0]["message"]) 
        return second_response["choices"][0]["message"]["content"], conversation  # Return the conversation here
    else:
        conversation.append(message)
        return message["content"], conversation

def main():
    print("Welcome to the CLI-chatbot. Type 'exit' to quit.")
    conversation = []
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        try:
            response, conversation = run_conversation(user_input, conversation)
            print(f"Bot: {response}")
        except Exception as e:
            print(f"An error occurred: {e}")
if __name__ == "__main__":
    main()