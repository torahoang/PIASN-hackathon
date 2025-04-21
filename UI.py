import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QFileDialog, QLabel)
from router import router_func

class ChatBotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.chat_started = False
        self.files = []  # To keep track of added files
        self.reroute = True

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Simple Chat Bot')
        self.setGeometry(300, 300, 400, 550)  # Made slightly taller for file display

        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create horizontal layout for top controls
        top_layout = QHBoxLayout()

        # Create add file button
        self.add_file_button = QPushButton("Add File")
        self.add_file_button.clicked.connect(self.open_file_dialog)
        top_layout.addWidget(self.add_file_button)

        # Create widget to display added files
        self.files_container = QWidget()
        self.files_display = QVBoxLayout(self.files_container)
        top_layout.addWidget(self.files_container)

        # Add top layout to main layout
        main_layout.addLayout(top_layout)

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

    def open_file_dialog(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Text and Docx Files (*.txt *.docx)", options=options)
        if files:
            for file in files:
                if file not in self.files:
                    self.files.append(file)
                    self.add_file_label(file)

    def add_file_label(self, file_path):
        # Create a horizontal layout for each file label and remove button
        file_layout = QHBoxLayout()

        # Create label for file name
        file_name = file_path.split('/')[-1]
        label = QLabel(file_name)

        # Create remove button
        remove_button = QPushButton('x')
        remove_button.setFixedSize(20, 20)
        remove_button.clicked.connect(lambda checked, fp=file_path, fl=file_layout: self.remove_file(fp, fl))

        # Add label and button to layout
        file_layout.addWidget(label)
        file_layout.addWidget(remove_button)
        file_layout.addStretch()

        # Add this layout to the files_display layout
        self.files_display.addLayout(file_layout)

    def remove_file(self, file_path, file_layout):
        # Remove file from list
        if file_path in self.files:
            self.files.remove(file_path)

        # Remove widgets from layout
        while file_layout.count():
            child = file_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Remove the layout itself from the parent layout
        self.files_display.removeItem(file_layout)

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
        if "hello" in user_message.lower():
            return "Hello there! How can I help you today?"
        elif "bye" in user_message.lower():
            return "Goodbye! Have a nice day!"
        else:
            responsed = "this part havent been implement yet"
            if self.reroute:
                model_name = router_func(user_message.lower())
                responsed = "rerouting to " + model_name + " expert"
                self.reroute = False
                print(self.reroute)
            #else:
                    # responsed = connect to model

            return responsed

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
