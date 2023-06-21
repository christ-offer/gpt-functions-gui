import openai
import json
import logging
from typing import Optional, Dict, List, Tuple

from system import system_message, system_message2
from functions import function_params, wikidata_sparql_query, scrape_webpage, write_file, knowledgebase_create_entry, knowledgebase_list_entries, knowledgebase_read_entry, python_repl, read_csv_columns, image_to_text, read_file, edit_file, list_history_entries, write_history_entry, read_history_entry, query_wolframalpha

conversation = []

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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
        print(f"Function name: {function_name}")
        print(f"Function arguments: {function_args}")

        if function_name == "python_repl":
            function_response = python_repl(function_args.get("code"))
        elif function_name == "query_wolframalpha":
            function_response = query_wolframalpha(function_args.get("query"))
        elif function_name == "knowledgebase_read_entry":
            function_response = knowledgebase_read_entry(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "read_history_entry":
            function_response = read_history_entry(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "write_history_entry":
            function_response = write_history_entry(*function_args.values())
        elif function_name == "list_history_entries":
            function_response = list_history_entries(*function_args.values())
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "knowledgebase_list_entries":
            function_response = knowledgebase_list_entries()
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation
        elif function_name in ["knowledgebase_create_entry","knowledgebase_update_entry", "read_csv_columns", "write_file"]:
            function_response = globals()[function_name](*function_args.values())
        elif function_name == "wikidata_sparql_query":
            function_response = wikidata_sparql_query(function_args.get("query"))
        elif function_name == "scrape_webpage":
            function_response = scrape_webpage(function_args.get("url"))
        elif function_name == "image_to_text":
            function_response = image_to_text(function_args.get("filename"))
        elif function_name == "read_file":
            function_response = read_file(function_args.get("filename"))
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        elif function_name == "edit_file":
            filename = function_args.get("filepath")
            changes = function_args.get("changes")
            function_response = edit_file(filename, changes)

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

# CLI
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
