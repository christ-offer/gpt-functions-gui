import json
import logging
from typing import Dict, List, Tuple
import re

from tokenizer.tokens import calculate_cost, num_tokens_from_messages
from system_messages.system import (
    function_res_agent, 
    base_system_message,
    )
from agents.function_mapper import FunctionMapper
from agents.function_call_agent import FunctionCallAgent
from agents.base_agent import RegularAgent
from agents.function_response_agent import function_response_agent

from constants import HISTORY_DIR
function_mapper = FunctionMapper()
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
    if function_name not in function_mapper.function_map:
        raise Exception(f"Function {function_name} not found.")
    if function_args is None:
        return function_mapper.function_map[function_name]()
    return function_mapper.function_map[function_name](*function_args.values())

def run_conversation(prompt: str, conversation: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]], int, float]:
    token_count = 0
    conversation_cost = 0
    conversation.append({
        "role": "user",
        "content": prompt,
    })
    
    agents = function_mapper.agents
    command = get_command(prompt)
    if command in agents:
        agent_properties = agents[command]
        print(agent_properties["name"])
        prompt = prompt[agent_properties["command_length"]:].strip()
        if agent_properties["is_function"]:
            response = function_call_agent(
                prompt=prompt,
                conversation=conversation,
                system_message=agent_properties["agent"].system_message,
                function_params=agent_properties["agent"].function_params,
                temperature=agent_properties["agent"].temperature,
                top_p=agent_properties["agent"].top_p,
                frequency_penalty=agent_properties["agent"].frequency_penalty,
                model=agent_properties["agent"].model,
            )
            message = response[0]
            model = agent_properties["agent"].model
            tokens = num_tokens_from_messages(message, model=model)
            cost = calculate_cost(tokens, model=model)
            token_count += tokens
            conversation_cost += cost
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
        if function_name in function_mapper.functions_that_append_to_conversation:
            conversation.append({
                "role": "assistant",
                "content": function_response,  # directly add function response to the conversation
            })
            return function_response, conversation, token_count, conversation_cost  # directly return function response
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
