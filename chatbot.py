
import openai
from openai.error import OpenAIError
import json
import logging
from typing import Optional, Dict, List, Tuple
import re

from tokenizer.tokens import calculate_cost, num_tokens_from_messages
from system_messages.system import (
    function_res_agent, 
    base_system_message,
    review_agent, 
    brainstorm_agent, 
    ticket_agent, 
    spec_writer, 
    code_writer,
    unit_test_writer,
    suggest_changes_agent
    )
from agents.function_mapper import FunctionMapper
from agents.function_call_agent import FunctionCallAgent
from agents.base_agent import RegularAgent
from agents.function_response_agent import function_response_agent
from constants import HISTORY_DIR
agents = FunctionMapper()
fc = FunctionCallAgent()
ra = RegularAgent()
function_call_agent = fc.call
regular_agent = ra.call

def get_command(prompt):
    """Extract command from prompt if it exists"""
    match = re.search(r"/\w+", prompt)
    if match:
        return match.group(0)
    return None

def call_function(function_name, function_args):
    if function_name not in agents.function_map:
        raise Exception(f"Function {function_name} not found.")
    if function_args is None:
        return agents.function_map[function_name]()
    return agents.function_map[function_name](*function_args.values())

def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]], int, float]:
    token_count = 0
    conversation_cost = 0
    conversation.append({
        "role": "user",
        "content": prompt,
    })
    if get_command(prompt) == "/csv":
        print("CSV Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.csv_handler.system_message, 
            function_params=agents.csv_handler.read_csv_columns_params,
            temperature=agents.csv_handler.temperature,
            top_p=agents.csv_handler.top_p,
            frequency_penalty=agents.csv_handler.frequency_penalty,
            model=agents.csv_handler.model,
            )
        message = response[0]
        model = agents.csv_handler.model
        tokens = num_tokens_from_messages(message, model=agents.csv_handler.model)
        cost = calculate_cost(tokens, model=agents.csv_handler.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/python":
        print("Python Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.python_repl.system_message, 
            function_params=agents.python_repl.python_repl_params,
            temperature=agents.python_repl.temperature,
            top_p=agents.python_repl.top_p,
            frequency_penalty=agents.python_repl.frequency_penalty,
            model=agents.python_repl.model,
            )
        message = response[0]
        model = agents.python_repl.model
        tokens = num_tokens_from_messages(message, model=agents.python_repl.model)
        cost = calculate_cost(tokens, model=agents.python_repl.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/kb":
        print("Knowledge Base Agent")
        prompt = prompt[3:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.kb_handler.system_message, 
            function_params=agents.kb_handler.knowledgebase_params,
            temperature=agents.kb_handler.temperature,
            top_p=agents.kb_handler.top_p,
            frequency_penalty=agents.kb_handler.frequency_penalty,
            model=agents.kb_handler.model,
            )
        message = response[0]
        model = agents.kb_handler.model
        tokens = num_tokens_from_messages(message, model=agents.kb_handler.model)
        cost = calculate_cost(tokens, model=agents.kb_handler.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/history":
        print("History Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.history_handler.system_message, 
            function_params=agents.history_handler.history_params,
            temperature=agents.history_handler.temperature,
            top_p=agents.history_handler.top_p,
            frequency_penalty=agents.history_handler.frequency_penalty,
            model=agents.history_handler.model,
            )
        message = response[0]
        model = agents.history_handler.model
        tokens = num_tokens_from_messages(message, model=agents.history_handler.model)
        cost = calculate_cost(tokens, model=agents.history_handler.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/write":
        print("Write Code Agent")
        prompt = prompt[6:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.file_handler.write_system_message, 
            function_params=agents.file_handler.write_file_params,
            temperature=agents.file_handler.temperature,
            top_p=agents.file_handler.top_p,
            frequency_penalty=agents.file_handler.frequency_penalty,
            model=agents.file_handler.model,
            )
        message = response[0]
        model = agents.file_handler.model
        tokens = num_tokens_from_messages(message, model=agents.file_handler.model)
        cost = calculate_cost(tokens, model=agents.file_handler.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/read":
        print("Read File Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.file_handler.read_system_message, 
            function_params=agents.file_handler.read_file_params,
            temperature=agents.file_handler.temperature,
            top_p=agents.file_handler.top_p,
            frequency_penalty=agents.file_handler.frequency_penalty,
            model=agents.file_handler.model,
            )
        message = response[0]
        model = agents.file_handler.model
        tokens = num_tokens_from_messages(message, model=agents.file_handler.model)
        cost = calculate_cost(tokens, model=agents.file_handler.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/edit":
        print("Edit File Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.file_handler.edit_system_message, 
            function_params=agents.file_handler.edit_file_params,
            temperature=agents.file_handler.temperature,
            top_p=agents.file_handler.top_p,
            frequency_penalty=agents.file_handler.frequency_penalty,
            model=agents.file_handler.model,
            )
        message = response[0]
        model = agents.file_handler.model
        tokens = num_tokens_from_messages(message, model=agents.file_handler.model)
        cost = calculate_cost(tokens, model=agents.file_handler.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/wikidata":
        print("Wikidata Agent")
        prompt = prompt[9:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.wikidata_agent.system_message, 
            function_params=agents.wikidata_agent.wikidata_sparql_query_params,
            temperature=agents.wikidata_agent.temperature,
            top_p=agents.wikidata_agent.top_p,
            frequency_penalty=agents.wikidata_agent.frequency_penalty,
            model=agents.wikidata_agent.model,
            )
        message = response[0]
        model = agents.wikidata_agent.model
        tokens = num_tokens_from_messages(message, model=agents.wikidata_agent.model)
        cost = calculate_cost(tokens, model=agents.wikidata_agent.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/scrape":
        print("Scrape Webpage Agent")
        prompt = prompt[8:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.scraper.system_message, 
            function_params=agents.scraper.scrape_params,
            temperature=agents.scraper.temperature,
            top_p=agents.scraper.top_p,
            frequency_penalty=agents.scraper.frequency_penalty,
            model=agents.scraper.model,
            )
        message = response[0]
        model = agents.scraper.model
        tokens = num_tokens_from_messages(message, model=agents.scraper.model)
        cost = calculate_cost(tokens, model=agents.scraper.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/image":
        print("Image to Text Agent")
        prompt = prompt[7:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.image_agent.system_message, 
            function_params=agents.image_agent.image_to_text_params,
            temperature=agents.image_agent.temperature,
            top_p=agents.image_agent.top_p,
            frequency_penalty=agents.image_agent.frequency_penalty,
            model=agents.image_agent.model,
            )
        message = response[0]
        model = agents.image_agent.model
        tokens = num_tokens_from_messages(message, model=agents.image_agent.model)
        cost = calculate_cost(tokens, model=agents.image_agent.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/help":
        print("Help Agent")
        prompt = prompt[5:].strip()
        response = function_call_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=agents.help_agent.system_message, 
            function_params=agents.help_agent.help_params,
            temperature=agents.help_agent.temperature,
            top_p=agents.help_agent.top_p,
            frequency_penalty=agents.help_agent.frequency_penalty,
            model=agents.help_agent.model,
            )
        message = response[0]
        model = agents.help_agent.model
        tokens = num_tokens_from_messages(message, model=agents.help_agent.model)
        cost = calculate_cost(tokens, model=agents.help_agent.model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/review":
        print("Review Agent")
        prompt = prompt[7:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=review_agent
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/brainstorm":
        print("Brainstorm Agent")
        prompt = prompt[10:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=brainstorm_agent
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/ticket":
        print("Ticket Agent")
        prompt = prompt[7:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation,
            system_message=ticket_agent
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/write_spec":
        print("Write Spec Agent")
        prompt = prompt[11:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=spec_writer
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/write_code":
        print("Write Code Agent")
        prompt = prompt[11:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=code_writer
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/write_tests":
        print("Unit Test Agent")
        prompt = prompt[12:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=unit_test_writer
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/suggest_edits":
        print("Suggest Edits Agent")
        prompt = prompt[14:].strip()
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=suggest_changes_agent
            )
        message = response[0]
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost
    elif get_command(prompt) == "/save":
        print("Save Agent")
        prompt = prompt[5:].strip()
        filename = prompt
        conversation_string = ""
        for entry in conversation:
            conversation_string += f"{entry['role']}:\n{entry['content']}\n\n"
        conversation_string += "\n"
        with open(f"{HISTORY_DIR}/{filename}", "w") as f:
            f.write(conversation_string)
        message = {
            "role": "assistant",
            "content": f"Conversation saved to {filename} in {HISTORY_DIR}",
        }
    else:
        print('Personal Assistant')
        response = regular_agent(
            prompt=prompt, 
            conversation=conversation, 
            system_message=base_system_message,
            )
        message = response[0]    
        model = "gpt-4-0613"
        tokens = num_tokens_from_messages(message, model=model)
        cost = calculate_cost(tokens, model=model)
        token_count += tokens
        conversation_cost += cost

    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])
        print(f"Function name: {function_name}")
        print(f"Function arguments: {function_args}")
        
        function_response = call_function(function_name, function_args)
        
        if function_name in agents.functions_that_append_to_conversation:
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation  # directly return function response
        else:
            logging.info(f"Function response: {function_response}")
            second_response = function_response_agent(
                prompt=prompt, 
                system_message=function_res_agent, 
                function_name=function_name, 
                function_response=function_response, 
                message=message
                )
            conversation.append({
                "role": "assistant",
                "content": second_response["content"],
            }) 
            model = "gpt-3.5-turbo-16k-0613"

            tokens = num_tokens_from_messages(second_response, model=model)
            cost = calculate_cost(tokens, model=model)
            token_count += tokens
            conversation_cost += cost
            print(f'Cost of run: {conversation_cost}$')
            return second_response["content"], conversation, token_count, conversation_cost
    else:
        conversation.append({
            "role": "assistant",
            "content": message["content"],
        })
        print(f'Cost of run: {conversation_cost}$')
        return message["content"], conversation, token_count, conversation_cost
