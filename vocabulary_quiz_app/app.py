from __future__ import annotations

import random
import tkinter as tk

from tkinter import ttk, font

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        # 타임아웃 및 카운트다운 기능 활용을 위해 root 저장
        self.root = root

        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False

        self.score = 0
        self.total = 0
        # 스피드런 전용 변수 초기화 
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
        # 스피드런 전용 버튼 추가. 영단어 글자랑 같은 행에, 오른쪽 끝 열에 배치
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

        # 스피드런의 타이머는 가독성을 위해 빨간색으로 설정. 최초 진입 시에는 숨김 상태
        self.timer_label = ttk.Label(
            root, 
            text="15s", 
            font=("NanumGothic", 12, "bold"), 
            foreground="red"
        )
        # 중앙 레이아웃 배치 (출제 단어 표시창 및 정답 입력창)    
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        self.answer_entry.bind("<KeyPress>", self.on_key_press) # 첫 타이핑 감지 시 스피드런 타이머 구동
        self.answer_entry.bind("<Return>", self.on_enter_press) # 엔터키 입력 시 채점 및 다음 단어 즉시 처리

        buttons = ttk.Frame(root)
        buttons.pack(pady=6)
        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)
        self.next_button = ttk.Button(buttons, text="다음", command=self.next_word)
        self.next_button.pack(side=tk.LEFT, padx=6)

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

        # 스피드런 전용 check함수 추가
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
        # 스피드런 버튼을 숨기고 남은 시간 표시
        self.speedrun_btn.place_forget()
        self.timer_label.config(text="15s")
        self.timer_label.place(relx=1.0, x=-16, y=14, anchor="ne")
        # 점수판 스타일을 빨간색으로 바꾼 후 점수 변수 초기화
        self.score_label.config(foreground="red")
        self.score_var.set(f"speedrun score: {self.speedrun_score}")
        self.check_button.configure(command=self.check_speedrun)
        self.next_word()

        
    def on_key_press(self, event) -> None:
        # 키입력 감지되면 타이머 가동
        if self.speedrun_mode and not self.timer_started:
            self.timer_started = True
            self.update_timer()
    def update_timer(self) -> None:
        if not self.speedrun_mode:
            return
        # 제한시간이 남아있다면 1초 차감 후 함수 다시 시작
        if self.time_left > 0:
            self.timer_label.config(text=f"{self.time_left}s")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        else:
        # 제한시간이 없다면 일반모드로 돌아감
            self.timer_label.config(text="0s")
            self.feedback_label.config(font=("NanumGothic", 20, "bold"), foreground="red")
            self.feedback_var.set("시간 종료! 최종 점수를 확인하세요.")
            self.check_button.state(["disabled"])
            self.next_button.state(["disabled"])
            self.root.after(5000, self.reset_to_normal)

    def reset_to_normal(self) -> None:
        self.speedrun_mode = False
        self.timer_started = False
        # 타이머 글자를 숨기고, 스피드런 버튼 복구
        self.timer_label.place_forget()
        self.speedrun_btn.place(relx=1.0, x=-16, y=14, anchor="ne")
        self.check_button.configure(command=self.check_current)
        # 점수판의 폰트와 색상을 일반 모드로 변경
        self.feedback_label.config(font=("NanumGothic", 12), foreground="black")
        self.score_label.config(foreground="black")
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.feedback_var.set("일반 모드로 돌아왔습니다.")
        self.next_word()

    def on_enter_press(self, event) -> None:
        if "disabled" in self.check_button.state():
            return  
        # 스피드런 모드라면 채점,다음문제를 enter키 한 번에 하도록 설정
        if self.speedrun_mode:
            self.check_speedrun()
            self.next_word()
        # 일반 모드라면 enter 두 번에 걸쳐서 하도록 로직 설정    
        else:
            if not self.checked:
                self.check_current()
            else:
                self.next_word()  