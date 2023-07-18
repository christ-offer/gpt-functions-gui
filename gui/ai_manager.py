from main import ChatbotGUI
from tokenizer.tokens import calculate_cost
from chatbot import run_conversation
import tkinter as tk
import markdown
import tiktoken
import requests

chatbot_gui = ChatbotGUI()

class AIManager:
    def run_chat(self, event=None):
        user_input = chatbot_gui.user_input_text.get("1.0", tk.END).strip()
        encoding = tiktoken.encoding_for_model("gpt-4-0613")
        num_tokens = len(encoding.encode(user_input))
        
        chatbot_gui.total_tokens += num_tokens
        cost = calculate_cost(num_tokens,  model="gpt-4-0613")
        chatbot_gui.total_cost += cost
        
        # update tokens and cost in ui
        #chatbot_gui.total_token_count.set(f"Total tokens: {chatbot_gui.total_tokens}")
        #chatbot_gui.total_cost_of_input.set(f"Total cost: {chatbot_gui.total_cost}$")
        
        html = markdown.markdown(user_input)
        user_input_html = f'<p style="background-color: lightgray;">You: {html}</p><br/>'

        chatbot_gui.current_html += user_input_html
        chatbot_gui.text_area.set_html(chatbot_gui.current_html)

        chatbot_gui.user_input_text.delete("1.0", tk.END)

        chatbot_gui.is_loading = True
        chatbot_gui.loading_label = tk.Label(chatbot_gui.root, text="Loading...", bg="white", font=("Arial", 30))
        chatbot_gui.loading_label.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")  # Place the loading label over the application window
    
        self.handle_model_response(user_input)

    def handle_model_response(self, user_input):
        try:
            response, _, tokens, cost = run_conversation(user_input, chatbot_gui.conversation)
        except requests.exceptions.RequestException as e:  
            response = "Oops! A network error occurred, please try again later."
            print(e)
        except Exception as e:
            response = f"Oops! An error occurred: {str(e)}"
            
        chatbot_gui.root.after(0, chatbot_gui.update_text_area, response)
        chatbot_gui.text_area.see("end")  # Scrolls to the end of the text_area
        
        chatbot_gui.total_tokens += tokens
        chatbot_gui.total_cost += cost
        
        ## Add tokens and cost to chat sidebar
        chatbot_gui.total_token_count.set(f"Total tokens: {chatbot_gui.total_tokens}")
        chatbot_gui.total_cost_of_input.set(f"Total cost: {chatbot_gui.total_cost:.6f}$")

