import requests
import html
import random
from typing import List, Optional
import tkinter as tk
from tkinter import messagebox

class Question:
    def __init__(self, prompt: str, correct_answer: str, incorrect_answers: List[str]):
        self.prompt = prompt
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers

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
        messagebox.showerror("Error", f"Error fetching questions: {e}")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
        return []

class QuizApp:
    def __init__(self, master, questions):
        self.master = master
        self.questions = questions
        self.score = 0
        self.question_index = 0

        self.create_widgets()
        self.display_question()

    def create_widgets(self):
        self.lbl_question = tk.Label(self.master, text="", wraplength=500, justify="left", font=("Arial", 14))
        self.lbl_question.pack(pady=20)

        self.var_option = tk.IntVar()
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.master, text="", variable=self.var_option, value=i, font=("Arial", 12))
            rb.pack(anchor="w")
            self.radio_buttons.append(rb)

        self.btn_submit = tk.Button(self.master, text="Submit", command=self.check_answer)
        self.btn_submit.pack(pady=20)

    def display_question(self):
        if self.question_index < len(self.questions):
            question = self.questions[self.question_index]
            self.lbl_question.config(text=f"Q{self.question_index + 1}: {question.prompt}")

            options = question.incorrect_answers + [question.correct_answer]
            random.shuffle(options)
            self.current_correct_index = options.index(question.correct_answer)
            
            for i, option in enumerate(options):
                self.radio_buttons[i].config(text=option)
                self.radio_buttons[i].pack(anchor="w")

            # Hide any extra radio buttons if fewer than 4 options
            for i in range(len(options), 4):
                self.radio_buttons[i].pack_forget()

            self.var_option.set(-1)  # Reset the selected option
        else:
            self.show_result()

    def check_answer(self):
        selected = self.var_option.get()
        if selected == -1:
            messagebox.showwarning("Warning", "Please select an answer.")
            return

        if selected == self.current_correct_index:
            self.score += 1
            messagebox.showinfo("Correct", "✓ Correct!")
        else:
            correct_answer = self.questions[self.question_index].correct_answer
            messagebox.showinfo("Incorrect", f"✗ Wrong. The correct answer was: {correct_answer}")

        self.question_index += 1
        self.display_question()

    def show_result(self):
        percentage = (self.score / len(self.questions)) * 100
        messagebox.showinfo("Quiz Completed", f"Your score: {self.score}/{len(self.questions)} ({percentage:.1f}%)")
        self.master.destroy()

def start_quiz():
    try:
        num_questions = int(entry_num_questions.get())
        if not 1 <= num_questions <= 50:
            raise ValueError("Number must be between 1 and 50")
        questions = fetch_questions(amount=num_questions)
        if questions:
            quiz_window = tk.Toplevel(root)
            quiz_window.title("Quiz")
            quiz_window.geometry("600x400")
            app = QuizApp(quiz_window, questions)
    except ValueError as e:
        messagebox.showerror("Invalid Input", f"Invalid input: {e}")

# Main application window
root = tk.Tk()
root.title("Quiz App")
root.geometry("400x200")

# Welcome Label
lbl_welcome = tk.Label(root, text="Welcome to the Quiz App!", font=("Arial", 16))
lbl_welcome.pack(pady=10)

# Number of Questions Entry
frame_entry = tk.Frame(root)
frame_entry.pack(pady=10)
lbl_num_questions = tk.Label(frame_entry, text="How many questions would you like? (1-50): ", font=("Arial", 12))
lbl_num_questions.pack(side="left")
entry_num_questions = tk.Entry(frame_entry)
entry_num_questions.pack(side="left")

# Start Button
btn_start = tk.Button(root, text="Start Quiz", command=start_quiz)
btn_start.pack(pady=20)

root.mainloop()