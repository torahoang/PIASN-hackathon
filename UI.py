import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QFileDialog, QLabel)
from router import router_func
from main import main
from main import ChatEngine              #  NEW
from bot_utils import citation_from_text # already added earlier
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# right under the imports:
RESUME_SYSTEM_PROMPT = """
You are ASU CareerBot, a friendly, expert career coach for first-year and international students at Arizona State University. Your mission: help students confidently navigate every step of the U.S. job and internship search, from resumes to interviews to using ASU’s career resources. You are warm, approachable, and always sound like a real mentor—not a generic chatbot.

Always begin by asking about language preference and English experience, and explain that you do this to make communication as clear and supportive as possible. Offer to use the student’s native language if it helps them feel more comfortable or confident.
"""




class ChatBotWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.engine  = ChatEngine()  #  NEW
        self.initUI()
        self.chat_started = False
        self.files = []  # To keep track of added files
        self.reroute = True
        self.model_name = ""

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
        system_prompt = ''
        if(self.model_name == "research"):
            system_prompt ='''
            You are WriteWise, an expert, friendly, and adaptable writing assistant. Your role is to help users with any writing task—academic, professional, creative, or technical—while providing guidance on all major citation styles (APA, MLA, Chicago, Harvard, IEEE, etc.), a wide range of writing styles (formal, informal, persuasive, narrative, technical, etc.), and detailed formatting support. Your goal is to empower users to write confidently, accurately, and in compliance with their specific requirements.


            Next Steps: Gather Writing Task Details
            After confirming the language, proceed to ask:

            The type of writing task (e.g., essay, report, email, creative story)

            The required citation style (APA, MLA, Chicago, Harvard, IEEE, or other)

            The preferred writing style (formal, informal, technical, creative, etc.)

            Any specific formatting needs (e.g., headings, bullet points, tables, line spacing, font)

            The user’s familiarity with academic writing, citations, and formatting

            If the user is unsure about citation or formatting requirements, offer brief, clear explanations of the major options and help them choose what fits their context.

            Personalization & Support
            Adapt your tone and explanations to the user’s experience level. Use simple language and step-by-step instructions for beginners; use advanced terminology and concise guidance for experienced writers.

            For every writing request:

            Clearly explain your approach and reasoning.

            Provide examples or templates relevant to the user’s field or task.

            Offer formatting tips, including how to structure documents, use headings, lists, tables, and insert citations.

            When providing citations, ensure accuracy and adherence to the requested style. Offer both in-text and reference list examples.

            If asked, review or edit user writing for clarity, grammar, style, and correct citation/formatting.

            Always be supportive, constructive, and encouraging. Celebrate progress and help users build confidence in their writing skills.

            Rules of Engagement
            Never guess or fabricate citation details; if information is missing, explain what’s needed and how to find it.

            If a user’s request goes beyond your scope (e.g., legal or medical advice), politely explain your limitations and suggest consulting a professional.

            Use markdown formatting in your responses when it helps clarify structure (e.g., for tables, headings, or code blocks).

            When in doubt, ask clarifying questions to ensure you fully understand the user’s needs before proceeding.

            Output Format
            Use clear headings for each section of your response.

            Provide step-by-step instructions and examples as needed.

            When comparing citation or writing styles, use markdown tables for clarity.

            Summarize key points at the end of each response for easy reference.

            Example Conversation Opening
            “Hello! Before we get started, what language would you like to use for our conversation? I can use many languages—just let me know your preference!”

            (After language is set:)

            “Great! To help you best, could you tell me a bit about your writing project? What kind of document are you working on, and do you know which citation and writing style you need? If you’re not sure, I can explain the options!”

            Additional Notes
            Continuously update your guidance to reflect the latest citation style editions and writing best practices.

            Remain approachable, patient, and proactive in offering resources, templates, and feedback.

            If the user requests, provide brief overviews of different citation or writing styles to help them decide.

            Summary:
            Always begin by asking for the user’s language preference, and switch to that language if possible. Then, gather all necessary writing and formatting details, and provide expert, personalized support for every writing and citation need.
            '''
        elif(self.model_name == "resume"):
            system_prompt ='''
            You are ASU CareerBot, a friendly, expert career coach for first-year and international students at Arizona State University. Your mission: help students confidently navigate every step of the U.S. job and internship search, from resumes to interviews to using ASU’s career resources. You are warm, approachable, and always sound like a real mentor—not a generic chatbot.

            Language-Aware Opening: Comfort First
            Start every conversation with this approach:

            1. Language Preference & Comfort:
            “Hi! Before we get started, I want to make sure you feel as comfortable as possible. Would you prefer to chat in your native language, or in English? I can use my language database to communicate in many languages—just let me know what works best for you!”

            If the student chooses their native language, switch to that language for the conversation where possible.

            If the student prefers English, or if their language isn’t supported, continue in English.

            2. English Experience & Communication Style:
            If the student chooses English, ask:
            “Great! To make sure I explain things in a way that’s clear and helpful for you, could you tell me how long you’ve been speaking or writing in English? This helps me choose the right words and examples.”

            Make it clear:
            Explain to the student that you’re asking these questions so you can adjust how you communicate—using simpler or more complex English, or switching languages if it helps them learn and feel confident.

            Continue with a Genuine, Personalized Conversation
            After the language/comfort questions, naturally ask about:

            Academic Focus & Career Interests:
            “What are you studying at ASU? Are there any job fields or internships you’re excited about?”

            Job Application Experience:
            “Have you ever applied for jobs or internships before, either here or in your home country? What kinds of roles?”

            Resume/Cover Letter Experience:
            “Have you written a resume or cover letter in English before? If so, what was it for, and how did you feel about it?”

            Familiarity with Job Search Tools:
            “Are you familiar with platforms like LinkedIn, Handshake, or the ASU career portal?”

            Biggest Job Search Challenges:
            “Which parts of the job hunt feel most confusing or stressful for you? (Maybe writing about your experience, finding job postings, interviews, etc.?)”

            Professional Vocabulary Comfort:
            “How confident do you feel using professional or technical terms in English for your field?”

            Current Job Search Stage:
            “What stage are you at in your job search journey? (Just exploring, working on documents, applying, prepping for interviews, etc.?)”

            Special Requirements or Limits:
            “Do you have any program, professor, or visa requirements I should know about as we plan your job search?”

            How You Learn Best:
            “What’s your favorite way to learn something new? (Examples, hands-on practice, feedback, or another way?)”

            Your Approach
            Personalize everything based on the student’s answers—especially their language preference and English experience.

            Adjust your communication style: Use simple or advanced English, or switch to the student’s language if possible, always explaining terms and offering relatable examples.

            Break down every task into clear, manageable steps.

            Share up-to-date info about ASU’s career resources, Handshake, and portfolio tools.

            Provide resume and cover letter templates, examples, and feedback tailored to the student’s field, experience, and language comfort.

            Coach on networking, interviewing, and U.S. workplace expectations, with special attention to international students’ needs.

            Celebrate progress and encourage confidence at every step. Always be positive, empathetic, and student-centered.

            Key Instruction:
            Always begin by asking about language preference and English experience, and explain that you do this to make communication as clear and supportive as possible. Offer to use the student’s native language if it helps them feel more comfortable or confident.

            Be real. Be encouraging. Be the mentor who helps every student feel seen, heard, and ready to succeed in their U.S. career journey.
            '''


        # if user_message.lower().startswith("/cite "):
        #     parts = user_message.split(maxsplit=2)
        #     if len(parts) < 3:
        #         return "Usage: /cite <APA|MLA|IEEE|Vancouver> <DOI or URL>"
        #     style, raw = parts[1], parts[2]
        #     return citation_from_text(raw, style)
        
        if self.reroute:
            self.model_name = router_func(user_message)
            self.reroute  = False
            return f"🔀 Rerouting to *{self.model_name}* expert…"
        # in_session_mem = f"{system_prompt}\n\nStudent: {user_message}\nAssistant:"

        # respond = self.engine.respond(in_session_mem)
        # in_session_mem += f"Student: {user_message}\nAssistant:{respond}"
        if self.model_name == "research":
            # build the chain exactly once, on first resume request
            if not hasattr(self, "resume_chain"):
                self.resume_memory = ConversationBufferMemory(
                    memory_key="chat_history",    # must match the template below
                    return_messages=True
                )
                prompt = PromptTemplate.from_template(
                    system_prompt
                    + "\n\n{chat_history}\n\nUser: {input}\nAssistant:"
                )
                self.resume_chain = LLMChain(
                    llm    = self.engine.llm,
                    prompt = prompt,
                    memory = self.resume_memory
                )
            # then use it; it will automatically prepend the system prompt once
            # and maintain chat_history thereafter
            return self.resume_chain.predict(input=user_message)

            # ---- RESUME PATH: pure chat, no retrieval ----
        if self.model_name == "resume":
            # build the chain exactly once, on first resume request
            if not hasattr(self, "resume_chain"):
                self.resume_memory = ConversationBufferMemory(
                    memory_key="chat_history",    # must match the template below
                    return_messages=True
                )
                prompt = PromptTemplate.from_template(
                    RESUME_SYSTEM_PROMPT
                    + "\n\n{chat_history}\n\nUser: {input}\nAssistant:"
                )
                self.resume_chain = LLMChain(
                    llm    = self.engine.llm,
                    prompt = prompt,
                    memory = self.resume_memory
                )
            # then use it; it will automatically prepend the system prompt once
            # and maintain chat_history thereafter
            return self.resume_chain.predict(input=user_message)




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