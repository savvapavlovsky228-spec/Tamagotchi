import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
import threading
import time
import random



class Tamagotchi:
    def __init__(self, name: str = "Кукичи"):
        self.name = name[:16]
        self.hunger = 80
        self.thirst = 80
        self.energy = 80
        self.happiness = 80
        self.money = 120
        self.is_sick = False
        self.age_days = 0
        self.alive = True

    def _clamp(self, value: int) -> int:
        return max(0, min(100, value))

    def feed(self, amount=20, cost=10):
        if self.money < cost:
            return False
        self.hunger = self._clamp(self.hunger + amount)
        self.happiness = self._clamp(self.happiness + 2)
        self.money -= cost
        return True

    def give_water(self, amount=20, cost=5):
        if self.money < cost:
            return False
        self.thirst = self._clamp(self.thirst + amount)
        self.money -= cost
        return True

    def play(self):
        self.happiness = self._clamp(self.happiness + 10)
        self.energy = self._clamp(self.energy - 5)
        self.hunger = self._clamp(self.hunger - 5)
        return True

    def sleep(self):
        self.energy = self._clamp(self.energy + 50)
        self.age_days += 1
        self.hunger = self._clamp(self.hunger - 10)
        self.thirst = self._clamp(self.thirst - 10)
        return True

    def rest_day(self):
        if self.money < 20:
            return False
        self.hunger = self._clamp(self.hunger - 20)
        self.thirst = self._clamp(self.thirst - 20)
        self.happiness = self._clamp(self.happiness + 15)
        self.energy = self._clamp(self.energy + 50)
        self.age_days += 1
        self.money -= 20
        return True

    def work(self):
        self.money += 20
        self.hunger = self._clamp(self.hunger - 10)
        self.thirst = self._clamp(self.thirst - 10)
        self.happiness = self._clamp(self.happiness - 10)
        return True

    def heal(self):
        if self.money >= 50 and self.is_sick:
            self.money -= 50
            self.is_sick = False
            self.happiness = self._clamp(self.happiness + 30)
            return True
        return False

    def update(self):
        if not self.alive:
            return

        self.hunger = self._clamp(self.hunger - 1)
        self.thirst = self._clamp(self.thirst - 1)
        self.energy = self._clamp(self.energy - 1)

        if not self.is_sick and self.age_days > 0 and random.random() < 0.03:
            self.is_sick = True

        # Эффект болезни
        if self.is_sick:
            self.hunger = self._clamp(self.hunger - 2)
            self.thirst = self._clamp(self.thirst - 2)
            self.energy = self._clamp(self.energy - 3)
            self.happiness = self._clamp(self.happiness - 3)


        if (self.hunger <= 0 or self.thirst <= 0 or self.energy <= 0 or self.happiness <= 0):
            self.alive = False


    def get_mood_emoji(self) -> str:
        if self.is_sick:
            return "🤒"
        if self.happiness >= 80:
            return "😊"
        elif self.happiness >= 50:
            return "😐"
        elif self.happiness >= 20:
            return "😞"
        else:
            return "😨"


class TamagotchiApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Тамагочи — Кукичи")
        self.root.geometry("500x560")
        self.root.resizable(False, False)

        self.tamagotchi = Tamagotchi("Кукичи")
        self.running = True
        self.sick_window = None

        self.update_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.update_thread.start()

        self.setup_ui()

    def setup_ui(self):
        self.name_label = tk.Label(self.root, text=self.tamagotchi.name, font=("Arial", 20, "bold"))
        self.name_label.pack(pady=10)

        self.emoji_label = tk.Label(self.root, text=self.tamagotchi.get_mood_emoji(), font=("Arial", 48))
        self.emoji_label.pack()

        self.status_label = tk.Label(self.root, text="C00l!", font=("Arial", 12))
        self.status_label.pack()

        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)

        self.progress_bars = {}

        self.create_progress_row("Сытость:", "hunger")
        self.create_progress_row("Жажда:", "thirst")
        self.create_progress_row("Энергия:", "energy")
        self.create_progress_row("Счастье:", "happiness")

        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)

        self.money_label = tk.Label(self.root, text=f"Евро: {self.tamagotchi.money}", font=("Arial", 12))
        self.money_label.pack()

        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)

        self.message_label = tk.Label(self.root, text="Do you wanna play a little game?", fg="blue", font=("Arial", 10, "italic"))
        self.message_label.pack(pady=5)

        button_frame1 = tk.Frame(self.root)
        button_frame1.pack(pady=5)
        tk.Button(button_frame1, text="Покормить", command=self.on_feed, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame1, text="Напоить", command=self.on_water, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame1, text="Работать (+20€)", command=self.on_work, width=15, bg="#d0f0c0").pack(
            side=tk.LEFT, padx=5)

        button_frame2 = tk.Frame(self.root)
        button_frame2.pack(pady=5)
        tk.Button(button_frame2, text="Поиграть", command=self.on_play, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame2, text="Уложить спать", command=self.on_sleep, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame2, text="Отдохнуть (день)", command=self.on_rest, width=15).pack(side=tk.LEFT, padx=5)

    def create_progress_row(self, label_text: str, attr_name: str):
        frame = tk.Frame(self.root)

        frame.pack(fill='x', padx=20, pady=2)
        label = tk.Label(frame, text=label_text, width=10, anchor='w')
        label.pack(side=tk.LEFT)
        progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        progress.pack(side=tk.LEFT, fill='x', expand=True)
        self.progress_bars[attr_name] = progress

    def update_ui(self):
        self.emoji_label.config(text=self.tamagotchi.get_mood_emoji())
        avg = (self.tamagotchi.hunger + self.tamagotchi.thirst +
               self.tamagotchi.energy + self.tamagotchi.happiness) / 4
        status = "Inf aura ( Ronaldo suiiiiii )!" if avg > 75 else "Normal aura" if avg > 50 else "- 9999 aura" if avg > 25 else "Dead aura - inf social rating and cat waifu!"
        self.status_label.config(text=status)

        self.progress_bars["hunger"]["value"] = self.tamagotchi.hunger
        self.progress_bars["thirst"]["value"] = self.tamagotchi.thirst
        self.progress_bars["energy"]["value"] = self.tamagotchi.energy
        self.progress_bars["happiness"]["value"] = self.tamagotchi.happiness

        self.money_label.config(text=f"Евро: {self.tamagotchi.money}")

        if self.tamagotchi.is_sick and not self.sick_window:
            self.show_sick_window()
        elif not self.tamagotchi.is_sick and self.sick_window:
            self.close_sick_window()

        self.root.update_idletasks()

    def show_sick_window(self):
        if self.sick_window and self.sick_window.winfo_exists():
            return
        self.sick_window = Toplevel(self.root)
        self.sick_window.title("Болезнь")
        self.sick_window.geometry("500x500")
        self.sick_window.resizable(False, False)

        x = self.root.winfo_x() + self.root.winfo_width() + 10
        y = self.root.winfo_y()
        self.sick_window.geometry(f"+{x}+{y}")

        tk.Label(self.sick_window, text="У Кукичи рак Квена What! ", font=("Arial", 12, "bold"), fg="red").pack(pady=10)
        tk.Label(self.sick_window, text="Лечение стоит 5тр рублей ( ака 50€ с нашим то курсом -_-)", font=("Arial", 10)).pack()

        btn_heal = tk.Button(self.sick_window, text="Напичкать колёсами", command=self.on_heal, bg="#ffcccc")
        btn_heal.pack(pady=10)

        self.sick_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def close_sick_window(self):
        if self.sick_window and self.sick_window.winfo_exists():
            self.sick_window.destroy()
        self.sick_window = None

    def on_heal(self):
        if self.tamagotchi.heal():
            self.message_label.config(text="Thx i guess")
            self.close_sick_window()
        else:
            if self.tamagotchi.money < 50:
                self.message_label.config(text="Too poor")
            else:
                self.message_label.config(text="Not sick")
        self.update_ui()

    def on_feed(self):
        if self.tamagotchi.feed():
            self.message_label.config(text="Yammy")
        else:
            self.message_label.config(text="No shoes? NO SERVICE")
        self.update_ui()

    def on_water(self):
        if self.tamagotchi.give_water():
            self.message_label.config(text="Taste bad actually ")
        else:
            self.message_label.config(text="500 meters for town with water or 5 km for a little glass of water...? ")
        self.update_ui()

    def on_play(self):
        self.tamagotchi.play()
        self.message_label.config(text="Шнепе")
        self.update_ui()

    def on_sleep(self):
        self.tamagotchi.sleep()
        self.message_label.config(text="Go to sleeeep~ Go to sleeeep~")
        self.update_ui()

    def on_rest(self):
        if self.tamagotchi.rest_day():
            self.message_label.config(text="Just chillin'")
        else:
            self.message_label.config(text="why should i pay for rest bruh :/")
        self.update_ui()

    def on_work(self):
        self.tamagotchi.work()
        self.message_label.config(text="Good boy :P")
        self.update_ui()

    def _game_loop(self):
        while self.running:
            time.sleep(2)
            self.tamagotchi.update()

            if not self.tamagotchi.alive:
                self.message_label.config(text="Сосредоточься на всех параметрах, а не только на паре из них ")
                self.running = False
                self.root.after(0, lambda: messagebox.showinfo("Игра окончена", "Фиговый из тебя родитель :/"))
                root.quit()
                if self.sick_window:
                    self.close_sick_window()
            elif self.tamagotchi.age_days >= 30:
                self.message_label.config(text="Удивительно ! Ты не убил ребёнка за 30 дней")
                self.running = False
                self.root.after(0, lambda: messagebox.showinfo("УрААА!", "Только вот... зачем?"))

            self.root.after(0, self.update_ui)

    def show_game_over(self, title: str):
        self.root.after(0, lambda: messagebox.showinfo(title, self.message_label.cget("text")))


if __name__ == "__main__":
    root = tk.Tk()
    app = TamagotchiApp(root)
    root.mainloop()