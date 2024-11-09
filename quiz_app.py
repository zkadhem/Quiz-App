import sys
import requests
import html
import random
from typing import List, Optional
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QRadioButton, QMessageBox, QButtonGroup, QLineEdit, QProgressBar, QComboBox,
    QGridLayout, QDialog, QTextEdit
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QTime


# Added Portion:
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
#End of added portion




class Question:
    def __init__(self, prompt: str, correct_answer: str, incorrect_answers: List[str]):
        self.prompt = prompt
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers
        self.user_answer = None  # Store user's answer for review

def fetch_questions(amount: int = 10, category: Optional[int] = None, difficulty: Optional[str] = None) -> List[Question]:
    """Fetch questions from the Open Trivia DB API."""
    url = f"https://opentdb.com/api.php?amount={amount}"
    if category:
        url += f"&category={category}"
    if difficulty:
        url += f"&difficulty={difficulty}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['response_code'] != 0:
            raise ValueError("Failed to fetch questions from the API")
        
        questions = []
        for item in data['results']:
            prompt = html.unescape(item['question'])
            correct_answer = html.unescape(item['correct_answer'])
            incorrect_answers = [html.unescape(ans) for ans in item['incorrect_answers']]
            questions.append(Question(prompt, correct_answer, incorrect_answers))
        return questions
        
    except requests.RequestException as e:
        QMessageBox.critical(None, "Error", f"Error fetching questions: {e}")
        return []
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Unexpected error: {e}")
        return []

class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Quiz App")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(resource_path('quizappicon.png')))  # Set your own icon here
        self.questions = []
        self.score = 0
        self.question_index = 0
        self.current_correct_index = -1
        self.timer = QTimer()
        self.time_limit = 30  # Time limit per question in seconds
        self.remaining_time = self.time_limit
        self.incorrect_questions = []
        self.init_ui()
        self.set_style()
    
    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Welcome Screen Widgets
        self.welcome_widget = QWidget()
        self.welcome_layout = QVBoxLayout()
        self.welcome_widget.setLayout(self.welcome_layout)

        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path('logoquizapp.png'))  # Set your own logo here
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.welcome_label = QLabel("Welcome to the Quiz App!")
        self.welcome_label.setFont(QFont("Arial", 28, QFont.Bold))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        
        self.num_questions_label = QLabel("Number of Questions (1-50):")
        self.num_questions_input = QLineEdit()
        self.num_questions_input.setFixedWidth(100)

        self.category_label = QLabel("Select Category:")
        self.category_combo = QComboBox()
        self.populate_categories()

        self.difficulty_label = QLabel("Select Difficulty:")
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Any", "Easy", "Medium", "Hard"])
        
        self.start_button = QPushButton("Start Quiz")
        self.start_button.clicked.connect(self.start_quiz)
        self.start_button.setFixedWidth(200)
        
        self.welcome_layout.addWidget(self.logo_label)
        self.welcome_layout.addWidget(self.welcome_label)
        self.welcome_layout.addSpacing(20)

        form_layout = QGridLayout()
        form_layout.addWidget(self.num_questions_label, 0, 0)
        form_layout.addWidget(self.num_questions_input, 0, 1)
        form_layout.addWidget(self.category_label, 1, 0)
        form_layout.addWidget(self.category_combo, 1, 1)
        form_layout.addWidget(self.difficulty_label, 2, 0)
        form_layout.addWidget(self.difficulty_combo, 2, 1)
        form_layout.setAlignment(Qt.AlignCenter)
        self.welcome_layout.addLayout(form_layout)

        self.welcome_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        self.welcome_layout.setAlignment(Qt.AlignCenter)
        
        self.main_layout.addWidget(self.welcome_widget)
    
    def populate_categories(self):
        # Categories from the Open Trivia DB API
        categories = {
            0: "Any",
            9: "General Knowledge",
            10: "Entertainment: Books",
            11: "Entertainment: Film",
            12: "Entertainment: Music",
            13: "Entertainment: Musicals & Theatres",
            14: "Entertainment: Television",
            15: "Entertainment: Video Games",
            16: "Entertainment: Board Games",
            17: "Science & Nature",
            18: "Science: Computers",
            19: "Science: Mathematics",
            20: "Mythology",
            21: "Sports",
            22: "Geography",
            23: "History",
            24: "Politics",
            25: "Art",
            26: "Celebrities",
            27: "Animals",
            28: "Vehicles",
            29: "Entertainment: Comics",
            30: "Science: Gadgets",
            31: "Entertainment: Japanese Anime & Manga",
            32: "Entertainment: Cartoon & Animations"
        }
        self.category_combo.addItem("Any", 0)
        for cat_id, cat_name in categories.items():
            if cat_id != 0:
                self.category_combo.addItem(cat_name, cat_id)
    
    def start_quiz(self):
        try:
            num_questions = int(self.num_questions_input.text())
            if not 1 <= num_questions <= 50:
                raise ValueError("Number must be between 1 and 50")
            
            category = self.category_combo.currentData()
            if category == 0:
                category = None
            difficulty = self.difficulty_combo.currentText().lower()
            if difficulty == "any":
                difficulty = None
            
            self.questions = fetch_questions(amount=num_questions, category=category, difficulty=difficulty)
            if self.questions:
                # Clear the welcome screen
                self.welcome_widget.hide()
                self.build_quiz_ui()
                self.display_question()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"Invalid input: {e}")
    
    def build_quiz_ui(self):
        # Quiz Screen Widgets
        self.question_widget = QWidget()
        self.quiz_layout = QVBoxLayout()
        self.question_widget.setLayout(self.quiz_layout)

        self.question_label = QLabel("")
        self.question_label.setObjectName("question_label")  # Set objectName here
        self.question_label.setWordWrap(True)
        self.question_label.setFont(QFont("Arial", 20))
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setStyleSheet("padding: 20px;")
        self.options_group = QButtonGroup(self)
        self.options_layout = QVBoxLayout()
        self.options_layout.setSpacing(10)
        
        for i in range(4):
            radio_btn = QRadioButton()
            radio_btn.setFont(QFont("Arial", 16))
            self.options_group.addButton(radio_btn, id=i)
            self.options_layout.addWidget(radio_btn)
        
        self.submit_button = QPushButton("Submit Answer")
        self.submit_button.clicked.connect(self.check_answer)
        self.submit_button.setFixedWidth(200)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(20)
        
        self.timer_label = QLabel(f"Time Remaining: {self.time_limit} seconds")
        self.timer_label.setFont(QFont("Arial", 12))
        self.timer_label.setAlignment(Qt.AlignCenter)
        
        self.quiz_layout.addWidget(self.timer_label)
        self.quiz_layout.addWidget(self.question_label)
        self.quiz_layout.addLayout(self.options_layout)
        self.quiz_layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)
        self.quiz_layout.addWidget(self.progress_bar)
        
        self.main_layout.addWidget(self.question_widget)

        # Timer setup
        self.timer.timeout.connect(self.update_timer)
    
    def display_question(self):
        if self.question_index < len(self.questions):
            self.remaining_time = self.time_limit
            self.update_timer_label()
            self.timer.start(1000)
            
            question = self.questions[self.question_index]
            self.question_label.setText(f"Question {self.question_index + 1}:\n\n{question.prompt}")
            
            options = question.incorrect_answers + [question.correct_answer]
            random.shuffle(options)
            self.current_correct_index = options.index(question.correct_answer)
            
            for i, option in enumerate(options):
                radio_btn = self.options_group.button(i)
                radio_btn.setText(option)
                radio_btn.show()
                radio_btn.setChecked(False)
            
            # Hide unused radio buttons
            for i in range(len(options), 4):
                radio_btn = self.options_group.button(i)
                radio_btn.hide()
            
            self.progress_bar.setValue(self.question_index)
        else:
            self.show_result()
    
    def check_answer(self):
        selected_id = self.options_group.checkedId()
        self.timer.stop()
        if selected_id == -1:
            QMessageBox.warning(self, "No Selection", "Please select an answer before submitting.")
            self.timer.start(1000)
            return
        
        question = self.questions[self.question_index]
        question.user_answer = self.options_group.button(selected_id).text()
        
        if selected_id == self.current_correct_index:
            self.score += 1
            QMessageBox.information(self, "Correct", "✓ Correct!")
        else:
            self.incorrect_questions.append(question)
            QMessageBox.information(self, "Incorrect", f"✗ Wrong. The correct answer was: {question.correct_answer}")
        
        self.question_index += 1
        self.display_question()
    
    def update_timer(self):
        self.remaining_time -= 1
        self.update_timer_label()
        if self.remaining_time == 0:
            self.timer.stop()
            QMessageBox.information(self, "Time's Up", "Time's up for this question!")
            # Record that the user did not answer in time
            question = self.questions[self.question_index]
            question.user_answer = None
            self.incorrect_questions.append(question)
            self.question_index += 1
            self.display_question()
    
    def update_timer_label(self):
        self.timer_label.setText(f"Time Remaining: {self.remaining_time} seconds")
    
    def show_result(self):
        percentage = (self.score / len(self.questions)) * 100
        QMessageBox.information(
            self, "Quiz Completed",
            f"Your score: {self.score}/{len(self.questions)} ({percentage:.1f}%)"
        )
        self.review_incorrect_answers()
    
    def review_incorrect_answers(self):
        if not self.incorrect_questions:
            self.close()
            return
        review = QMessageBox.question(
            self, "Review Incorrect Answers",
            "Would you like to review the questions you answered incorrectly?",
            QMessageBox.Yes | QMessageBox.No
        )
        if review == QMessageBox.Yes:
            self.show_incorrect_answers()
        else:
            self.close()
    
    def show_incorrect_answers(self):
        self.review_widget = QDialog(self)
        self.review_widget.setWindowTitle("Review Incorrect Answers")
        self.review_widget.setGeometry(150, 150, 700, 500)
        
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Arial", 14))
        
        review_text = ""
        for idx, question in enumerate(self.incorrect_questions, 1):
            review_text += f"Question {idx}:\n{question.prompt}\n"
            if question.user_answer:
                review_text += f"Your Answer: {question.user_answer}\n"
            else:
                review_text += f"Your Answer: No Answer\n"
            review_text += f"Correct Answer: {question.correct_answer}\n\n"
        
        text_edit.setText(review_text)
        layout.addWidget(text_edit)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close_application)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.review_widget.setLayout(layout)
        self.review_widget.exec_()
    
    def close_application(self):
        self.review_widget.close()
        self.close()
    
    def set_style(self):
        # Apply stylesheets to enhance UI
        self.setStyleSheet("""
            QWidget {
                background-color: #f2f2f2;
            }
            QLabel#question_label {
                font-size: 20px;
                color: #333;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QRadioButton {
                font-size: 16px;
            }
            QProgressBar {
                border: 1px solid #bbb;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
            QLineEdit {
                padding: 5px;
                font-size: 14px;
            }
            QComboBox {
                padding: 5px;
                font-size: 14px;
            }
        """)
    
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

def main():
    app = QApplication(sys.argv)
    quiz_app = QuizApp()
    quiz_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()