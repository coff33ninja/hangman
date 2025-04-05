from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QWidget, QComboBox, QMessageBox, QInputDialog
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import QThread, pyqtSignal
import sys
from ai_manager import AIManager
import re  # Import regex for sanitizing words
from threading import Thread
import json  # Import JSON for serialization


class ResearchThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, ai_manager, topic):
        super().__init__()
        self.ai_manager = ai_manager
        self.topic = topic

    def run(self):
        """
        Perform research on the topic and emit the results as a string.
        """
        results = self.ai_manager.research_topic(self.topic)
        # Ensure the results are serialized to a string before emitting
        self.result_ready.emit(json.dumps(results, indent=4))


class AIGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Training Assistant")
        self.setGeometry(100, 100, 800, 600)

        # Initialize AI Manager
        self.ai_manager = AIManager()

        # Set up the main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Apply custom styles
        self.apply_styles()

        # Question and Answer Section
        self.question_label = QLabel("Ask the AI a question:")
        self.layout.addWidget(self.question_label)

        self.question_input = QLineEdit()
        self.layout.addWidget(self.question_input)

        self.ask_button = QPushButton("Ask")
        self.ask_button.clicked.connect(self.ask_ai_question)
        self.layout.addWidget(self.ask_button)

        self.answer_label = QLabel("AI's Answer:")
        self.layout.addWidget(self.answer_label)

        self.answer_display = QTextEdit()
        self.answer_display.setReadOnly(True)
        self.layout.addWidget(self.answer_display)

        # Research Section
        self.research_label = QLabel("Research a topic:")
        self.layout.addWidget(self.research_label)

        self.research_input = QLineEdit()
        self.layout.addWidget(self.research_input)

        self.research_button = QPushButton("Research")
        self.research_button.clicked.connect(self.research_topic)
        self.layout.addWidget(self.research_button)

        self.research_display = QTextEdit()
        self.research_display.setReadOnly(True)
        self.layout.addWidget(self.research_display)

        # Training Feedback Section
        self.feedback_label = QLabel("Provide feedback to improve training:")
        self.layout.addWidget(self.feedback_label)

        self.feedback_input = QLineEdit()
        self.layout.addWidget(self.feedback_input)

        self.feedback_button = QPushButton("Submit Feedback")
        self.feedback_button.clicked.connect(self.submit_feedback)
        self.layout.addWidget(self.feedback_button)

        # Category Management Section
        self.category_label = QLabel("Manage Categories:")
        self.layout.addWidget(self.category_label)

        self.category_dropdown = QComboBox()
        self.update_category_dropdown()
        self.layout.addWidget(self.category_dropdown)

        self.add_category_button = QPushButton("Add New Category")
        self.add_category_button.clicked.connect(self.add_category)
        self.layout.addWidget(self.add_category_button)

    def apply_styles(self):
        """
        Apply custom styles to the GUI.
        """
        # Set font
        font = QFont("Arial", 12)
        self.setFont(font)

        # Set background color
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#e0e0e0"))  # Light gray background
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))  # Black text
        self.setPalette(palette)

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #007BFF;  /* Blue button */
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;  /* Darker blue on hover */
            }
        """
        self.setStyleSheet(button_style)

        # Style text inputs and displays
        input_style = """
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #ffffff;  /* White background */
                color: #000000;  /* Black text */
            }
        """
        self.setStyleSheet(self.styleSheet() + input_style)

    def ask_ai_question(self):
        """
        Ask the AI a question, display pulled data, and start training in the background.
        """
        question = self.question_input.text().strip()
        if not question:
            QMessageBox.warning(self, "Input Error", "Please enter a question.")
            return

        # Step 1: Break the question into words
        words = question.lower().split()
        predefined_words = self.ai_manager.predefined_words.keys()  # Load predefined words
        core_words = [word for word in words if word in predefined_words]

        # Step 2: Sanitize focus words (remove punctuation)
        focus_words = [re.sub(r'[^\w\s]', '', word) for word in words if word not in predefined_words]

        # Step 3: Log the breakdown
        print(f"Core words: {core_words}")
        print(f"Focus words: {focus_words}")

        # Step 4: Pull existing data for focus words
        pulled_data = {}
        for word in focus_words:
            if word:  # Ensure the word is not empty after sanitization
                pulled_data[word] = self.ai_manager.pull_existing_data(word)

        # Step 5: Display pulled data in a clean format
        answer = f"Core words: {' '.join(core_words)}\n\n"
        for word, data in pulled_data.items():
            if data:
                answer += f"Pulled data for '{word}':\n"
                answer += self.format_pulled_data(data) + "\n\n"
            else:
                answer += f"No existing data found for '{word}'. Starting research...\n\n"
        self.answer_display.setText(answer)

        # Step 6: Start training in the background
        for word, data in pulled_data.items():
            Thread(target=self.train_word, args=(word, data)).start()

    def train_word(self, word, data):
        """
        Train the AI on the word and its data.
        """
        if not data:
            data = self.ai_manager.research_topic(word)
        self.ai_manager.train_on_word(word, data)
        print(f"Training completed for '{word}'.")

    def format_pulled_data(self, data):
        """
        Format the pulled data into a readable string.
        """
        formatted_data = f"Word: {data.get('word', 'N/A')}\n"
        definitions = data.get('definitions', [])
        if definitions:
            formatted_data += "Definitions:\n"
            for i, definition in enumerate(definitions, 1):
                formatted_data += f"  {i}. ({definition.get('partOfSpeech', 'N/A')}) {definition.get('definition', 'N/A')}\n"
                if definition.get('example'):
                    formatted_data += f"     Example: {definition['example']}\n"
        examples = [ex for ex in data.get('examples', []) if ex]
        if examples:
            formatted_data += "Examples:\n"
            for example in examples:
                formatted_data += f"  - {example}\n"
        synonyms = data.get('synonyms', [])
        if synonyms:
            formatted_data += f"Synonyms: {', '.join(synonyms)}\n"
        antonyms = data.get('antonyms', [])
        if antonyms:
            formatted_data += f"Antonyms: {', '.join(antonyms)}\n"
        related_topics = data.get('related_topics', [])
        if related_topics:
            formatted_data += f"Related Topics: {', '.join(related_topics)}\n"
        return formatted_data

    def research_topic(self):
        """
        Research a topic in a separate thread and display the results.
        """
        topic = self.research_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Input Error", "Please enter a topic to research.")
            return

        self.research_button.setEnabled(False)  # Disable the button while researching

        # Create and start the research thread
        self.research_thread = ResearchThread(self.ai_manager, topic)
        self.research_thread.result_ready.connect(self.display_research_results)
        self.research_thread.start()

    def display_research_results(self, results):
        """
        Display the research results in the main thread.
        """
        self.research_display.setText(results)
        self.research_button.setEnabled(True)  # Re-enable the button

    def submit_feedback(self):
        """
        Submit feedback to improve AI training.
        """
        feedback = self.feedback_input.text().strip()
        if not feedback:
            QMessageBox.warning(self, "Input Error", "Please enter feedback.")
            return

        # Save feedback to training data
        self.ai_manager.training_data.setdefault("feedback", []).append(feedback)
        self.ai_manager.save_training_data()

        # Dynamically retrain the AI with new feedback
        self.ai_manager.retrain()

        QMessageBox.information(self, "Feedback Submitted", "Thank you for your feedback!")
        self.feedback_input.clear()

    def update_category_dropdown(self):
        """
        Update the category dropdown with current categories, including dynamically created ones.
        """
        self.category_dropdown.clear()
        categories = self.ai_manager.training_data.get("categories", [])
        self.category_dropdown.addItems(categories)

    def add_category(self):
        """
        Add a new category to the AI's training data dynamically.
        """
        new_category, ok = QInputDialog.getText(self, "Add Category", "Enter new category name:")
        if ok and new_category.strip():
            if new_category in self.ai_manager.training_data.get("categories", []):
                QMessageBox.warning(self, "Duplicate Category", "This category already exists.")
            else:
                self.ai_manager.training_data.setdefault("categories", []).append(new_category)
                self.ai_manager.save_training_data()
                self.update_category_dropdown()
                QMessageBox.information(self, "Category Added", f"Category '{new_category}' added successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIGui()
    window.show()
    sys.exit(app.exec())
