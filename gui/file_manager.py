import tkinter as tk
from _tkinter import filedialog
import os
import shutil

from main import ChatbotGUI
from agents.image_agent import ImageAgent
from agents.csv_agent import CSVHandler
image_agent = ImageAgent()
csv_agent = CSVHandler()
chatbot_gui = ChatbotGUI()

from constants import *
DIRECTORIES = [
    KB_DIR, 
    HISTORY_DIR, 
    CSV_DIR, 
    IMG_DIR, 
    CODE_DIR, 
    LOG_DIR, 
    DATA_DIR, 
    PROJECTS_DIR
    ]

class FileManager:
    def __init__(self):
        # Check if directories exist and create them if they don't
        for directory in DIRECTORIES:
            os.makedirs(directory, exist_ok=True)
        
    def upload_image(self):
        image_file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if image_file_path:
            target_directory = IMG_DIR
            target_file_path = os.path.join(target_directory, os.path.basename(image_file_path))
            shutil.copy(image_file_path, target_file_path)
            
            caption = image_agent.image_to_text(image_file_path)
            
            message_html = f'<p style="background-color: lightblue;">Bot: {os.path.basename(image_file_path)} was added to image folder<br/>The caption is: {caption}</p><br/>'

            chatbot_gui.current_html += message_html
            chatbot_gui.text_area.set_html(chatbot_gui.current_html)

            chatbot_gui.conversation.append({
                "role": "assistant",
                "content": f'Bot: Image: {os.path.basename(image_file_path)} was added to image folder\nThe capition is: {caption}\n',  # directly add function response to the conversation
            })
            
    def upload_csv(self):
        csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if csv_file_path:
            target_directory = CSV_DIR
            target_file_path = os.path.join(target_directory, os.path.basename(csv_file_path))
            shutil.copy(csv_file_path, target_file_path)
            
            columns = csv_agent.read_csv_columns(csv_file_path)

            chatbot_gui.text_area.insert(tk.INSERT, f'{columns}\n', "bot")
            chatbot_gui.conversation.append({
                "role": "assistant",
                "content": f'Bot: {os.path.basename(csv_file_path)} was added to CSV folder\nThe columns are: {columns}\n',  # directly add function response to the conversation
            })
