import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton)


class ChatBotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.chat_started = False

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Simple Chat Bot')
        self.setGeometry(300, 300, 400, 500)

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Chat messages will appear here...")

        # Create input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here and press Enter")
        self.input_field.returnPressed.connect(self.send_message)

        # Create new chat button
        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.clicked.connect(self.restart_chat)

        # Add widgets to layout
        main_layout.addWidget(self.chat_display)
        main_layout.addWidget(self.input_field)
        main_layout.addWidget(self.new_chat_button)

        # Set the layout
        self.setLayout(main_layout)

        # Start a new chat
        self.restart_chat()

    def send_message(self):
        user_message = self.input_field.text().strip()
        if user_message:
            # Display user message
            self.chat_display.append(f"<b>You:</b> {user_message}")

            # Clear input field
            self.input_field.clear()

            # Generate and display bot response
            # In a real application, you would call your chatbot's logic here
            bot_response = self.get_bot_response(user_message)
            self.chat_display.append(f"<b>Bot:</b> {bot_response}")

    def get_bot_response(self, user_message):
        # This is a placeholder for actual chatbot logic
        # In a real application, you would implement more sophisticated response generation
        if "hello" in user_message.lower():
            return "Hello there! How can I help you today?"
        elif "bye" in user_message.lower():
            return "Goodbye! Have a nice day!"
        else:
            return "I'm a simple demo bot. I don't have many responses programmed yet."

    def restart_chat(self):
        # Clear the chat display
        self.chat_display.clear()

        # Reset chat state
        self.chat_started = True

        # Display welcome message
        welcome_message = "Welcome to the chat bot! Type a message to begin."
        self.chat_display.append(f"<b>Bot:</b> {welcome_message}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_window = ChatBotWindow()
    chat_window.show()
    sys.exit(app.exec_())
