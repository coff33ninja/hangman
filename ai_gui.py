from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QWidget, QComboBox, QMessageBox, QInputDialog
)
from PyQt6.QtCore import QThread, pyqtSignal
import sys
from ai_manager import AIManager


class ResearchThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, ai_manager, topic):
        super().__init__()
        self.ai_manager = ai_manager
        self.topic = topic

    def run(self):
        results = self.ai_manager.research_topic(self.topic)
        self.result_ready.emit(results)


class AIGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Training Assistant")
        self.setGeometry(100, 100, 800, 600)

        # Initialize AI Manager
        self.ai_manager = AIManager()

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

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

    def ask_ai_question(self):
        """
        Ask the AI a question and display its answer.
        """
        question = self.question_input.text().strip()
        if not question:
            QMessageBox.warning(self, "Input Error", "Please enter a question.")
            return

        answer = self.ai_manager.answer_question(question)
        self.answer_display.setText(answer)

    def research_topic(self):
        """
        Research a topic in a separate thread and display the results.
        """
        topic = self.research_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Input Error", "Please enter a topic to research.")
            return

        self.research_button.setEnabled(False)  # Disable the button while researching

        def display_results(results):
            self.research_display.setText(results)
            self.research_button.setEnabled(True)  # Re-enable the button

        self.ai_manager.research_topic_async(topic, display_results)

    def submit_feedback(self):
        """
        Submit feedback to improve AI training.
        """
        feedback = self.feedback_input.text().strip()
        if not feedback:
            QMessageBox.warning(self, "Input Error", "Please enter feedback.")
            return

        # Example: Save feedback to training data
        self.ai_manager.training_data.setdefault("feedback", []).append(feedback)
        self.ai_manager.save_training_data()
        QMessageBox.information(self, "Feedback Submitted", "Thank you for your feedback!")
        self.feedback_input.clear()

    def update_category_dropdown(self):
        """
        Update the category dropdown with current categories.
        """
        self.category_dropdown.clear()
        categories = self.ai_manager.training_data.get("categories", [])
        self.category_dropdown.addItems(categories)

    def add_category(self):
        """
        Add a new category to the AI's training data.
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
