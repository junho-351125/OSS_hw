from __future__ import annotations

import random
import tkinter as tk

from tkinter import ttk, font

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        self.root = root
        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False

        self.score = 0
        self.total = 0
        ### 스피드런 전용 변수 추가
        self.speedrun_mode = False
        self.timer_started = False
        self.speedrun_score = 0
        self.time_left = 15

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x280")
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")

        ttk.Label(root, text="영단어").pack(pady=(16, 4))
        ###스피드런 전용 버튼 추가.
        self.speedrun_btn = tk.Button(
            root,
            text="스피드런",
            fg="white",
            bg="blue",
            highlightbackground="blue",
            relief="flat",
            font=("NanumGothic", 10),
            command=self.start_speedrun,
        )
        self.speedrun_btn.place(relx=1.0, x=-16, y=14, anchor="ne")

        self.timer_label = ttk.Label(
            root, 
            text="15s", 
            font=("NanumGothic", 12, "bold"), 
            foreground="red"
        )
            
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        self.answer_entry.bind("<KeyPress>", self.on_key_press)
        self.answer_entry.bind("<Return>", self.on_enter_press)

        buttons = ttk.Frame(root)
        buttons.pack(pady=6)
        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="다음", command=self.next_word).pack(
            side=tk.LEFT, padx=6
        )

        self.feedback_label = tk.Label(root, textvariable=self.feedback_var, font=("NanumGothic", 12))
        self.feedback_label.pack(pady=8)
        self.score_label = tk.Label(root, textvariable=self.score_var, font=("NanumGothic", 12))
        self.score_label.pack()

        self.next_word()

    def next_word(self) -> None:
        self.current = draw_word(self.words, self.rng)
        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)
        self.feedback_var.set("")
        self.checked = False
        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self) -> None:
        if self.current is None or self.checked:
            return
        self.checked = True
        self.total += 1
        user_input = self.answer_entry.get()
        if check_answer(self.current, user_input):
            self.score += 1
            self.feedback_var.set("정답입니다!")
        else:
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.check_button.state(["disabled"])

    def check_speedrun(self) -> None:
        if self.current is None or self.checked:
            return
        self.checked = True
        user_input = self.answer_entry.get()
    
        if check_answer(self.current, user_input):
            self.speedrun_score += 1
            self.feedback_var.set("정답!")
        else:
            self.feedback_var.set("오답!")
        self.score_var.set(f"speedrun score: {self.speedrun_score}")
        

    def start_speedrun(self) -> None:
        print("스피드런 동작")
        self.speedrun_mode = True
        self.timer_started = False
        self.speedrun_score = 0
        self.time_left = 15
        self.speedrun_btn.place_forget()
        self.timer_label.config(text="15s")
        self.timer_label.place(relx=1.0, x=-16, y=14, anchor="ne")
        self.score_label.config(foreground="red")

        self.score_var.set(f"speedrun score: {self.speedrun_score}")
        self.check_button.configure(command=self.check_speedrun)
        self.next_word()
        
    def on_key_press(self, event) -> None:
        if self.speedrun_mode and not self.timer_started:
            self.timer_started = True
            self.update_timer()
    def update_timer(self) -> None:
        if not self.speedrun_mode:
            return
        if self.time_left > 0:
            self.timer_label.config(text=f"{self.time_left}s")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="0s")
            self.feedback_label.config(font=("NanumGothic", 20, "bold"), foreground="red")
            self.feedback_var.set("시간 종료! 최종 점수를 확인하세요.")
            self.check_button.state(["disabled"])
            self.root.after(7000, self.reset_to_normal)


    def reset_to_normal(self) -> None:
        
        self.speedrun_mode = False
        self.timer_started = False
        
        self.timer_label.place_forget()
        self.speedrun_btn.place(relx=1.0, x=-16, y=14, anchor="ne")
        
        self.check_button.configure(command=self.check_current)
        
        self.feedback_label.config(font=("NanumGothic", 12), foreground="black")
        self.score_label.config(foreground="black")
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.feedback_var.set("일반 모드로 돌아왔습니다.")
        
        self.next_word()
    def on_enter_press(self, event) -> None:
        if self.speedrun_mode and self.time_left == 0:
            return
        
        if not self.checked:
            if self.speedrun_mode:
                self.check_speedrun()
                self.next_word()
                
        else:
            if not self.checked:
                self.check_current()
            else:
                self.next_word()  