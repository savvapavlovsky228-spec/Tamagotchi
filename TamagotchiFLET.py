import flet as ft
import time
import threading
from enum import Enum


class IllnessLevel(Enum):
    NONE = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3


class Tamagotchi:
    def __init__(self, name: str = "Кукичи"):
        self.name = name[:16]
        self.hunger = 80
        self.thirst = 80
        self.energy = 80
        self.happiness = 80
        self.hygiene = 80
        self.money = 100
        self.illness = IllnessLevel.NONE
        self.age_days = 0
        self.alive = True

    def _clamp(self, value: int) -> int:
        return max(0, min(100, value))

    def feed(self, amount: int = 20, cost: int = 10):
        if self.money < cost:
            return False
        self.hunger = self._clamp(self.hunger + amount)
        self.happiness = self._clamp(self.happiness + 2)
        self.money -= cost
        return True

    def give_water(self, amount: int = 20, cost: int = 5):
        if self.money < cost:
            return False
        self.thirst = self._clamp(self.thirst + amount)
        self.money -= cost
        return True

    def play(self, time_min: int = 10):
        self.happiness = self._clamp(self.happiness + 10)
        self.energy = self._clamp(self.energy - 5)
        self.hunger = self._clamp(self.hunger - 5)
        return True

    def sleep(self, hours: int = 8):
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

    def update(self):
        if not self.alive:
            return

        self.hunger = self._clamp(self.hunger - 1)
        self.thirst = self._clamp(self.thirst - 1)
        self.energy = self._clamp(self.energy - 1)

        if self.illness != IllnessLevel.NONE:
            self.hunger = self._clamp(self.hunger - 2)
            self.thirst = self._clamp(self.thirst - 2)
            self.energy = self._clamp(self.energy - 3)
            self.happiness = self._clamp(self.happiness - 3)

        if (self.hunger <= 0 or self.thirst <= 0 or self.energy <= 0 or
            self.happiness <= 0):
            self.alive = False

    def get_status_text(self) -> str:
        avg = (self.hunger + self.thirst + self.energy + self.happiness) / 4
        if avg > 75:
            return "Отлично!"
        elif avg > 50:
            return "Нормально"
        elif avg > 25:
            return "Плохо"
        else:
            return "Критично!"

    def get_mood_emoji(self) -> str:
        if self.happiness >= 80:
            return "😊"
        elif self.happiness >= 50:
            return "😐"
        elif self.happiness >= 20:
            return "😞"
        else:
            return "😢"


class FletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.tamagotchi = Tamagotchi("Кукичи")
        self.running = True

        self.timer_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.timer_thread.start()

        self.build_ui()

    def build_ui(self):
        self.page.title = "Тамагочи — Кукичи"
        self.page.padding = 20
        self.page.bgcolor = ft.Colors.GREEN_100

        self.pet_name = ft.Text(f"{self.tamagotchi.name}", size=24, weight="bold")
        self.mood_emoji = ft.Text(self.tamagotchi.get_mood_emoji(), size=60)
        self.status_label = ft.Text(self.tamagotchi.get_status_text(), size=18)

        self.hunger_bar = ft.ProgressBar(value=self.tamagotchi.hunger / 100, width=300)
        self.thirst_bar = ft.ProgressBar(value=self.tamagotchi.thirst / 100, width=300)
        self.energy_bar = ft.ProgressBar(value=self.tamagotchi.energy / 100, width=300)
        self.happiness_bar = ft.ProgressBar(value=self.tamagotchi.happiness / 100, width=300)

        self.money_label = ft.Text(f"Евро: {self.tamagotchi.money}", size=16)
        self.message_box = ft.Text("Привет! Я хочу играть!", italic=True, color=ft.Colors.BLUE_800)

        # Кнопки
        btn_feed = ft.ElevatedButton("Покормить", on_click=self.on_feed)
        btn_water = ft.ElevatedButton("Напоить", on_click=self.on_water)
        btn_play = ft.ElevatedButton("Поиграть", on_click=self.on_play)
        btn_sleep = ft.ElevatedButton("Уложить спать", on_click=self.on_sleep)
        btn_rest = ft.ElevatedButton("Отдохнуть (день)", on_click=self.on_rest)
        btn_work = ft.ElevatedButton("Работать (+20€)", on_click=self.on_work)

        self.page.add(
            ft.Column([
                self.pet_name,
                self.mood_emoji,
                self.status_label,
                ft.Divider(),
                ft.Row([ft.Text("Сытость:"), self.hunger_bar]),
                ft.Row([ft.Text("Жажда:"), self.thirst_bar]),
                ft.Row([ft.Text("Энергия:"), self.energy_bar]),
                ft.Row([ft.Text("Счастье:"), self.happiness_bar]),
                ft.Divider(),
                self.money_label,
                ft.Divider(),
                self.message_box,
                ft.Row([btn_feed, btn_water, btn_work]),
                ft.Row([btn_play, btn_sleep, btn_rest]),
            ])
        )

    def update_ui(self):
        self.mood_emoji.value = self.tamagotchi.get_mood_emoji()
        self.status_label.value = self.tamagotchi.get_status_text()
        self.hunger_bar.value = self.tamagotchi.hunger / 100
        self.thirst_bar.value = self.tamagotchi.thirst / 100
        self.energy_bar.value = self.tamagotchi.energy / 100
        self.happiness_bar.value = self.tamagotchi.happiness / 100
        self.money_label.value = f"Евро: {self.tamagotchi.money}"
        self.page.update()

    def on_feed(self, e):
        if self.tamagotchi.feed():
            self.message_box.value = "Спасибо за еду! 😋"
        else:
            self.message_box.value = "Не хватает денег на еду!"
        self.update_ui()

    def on_water(self, e):
        if self.tamagotchi.give_water():
            self.message_box.value = "Вода вкусная! 💧"
        else:
            self.message_box.value = "Не хватает денег на воду!"
        self.update_ui()

    def on_play(self, e):
        self.tamagotchi.play()
        self.message_box.value = "Ура! Поиграли! 🎮"
        self.update_ui()

    def on_sleep(self, e):
        self.tamagotchi.sleep()
        self.message_box.value = "Сладких снов! 😴"
        self.update_ui()

    def on_rest(self, e):
        if self.tamagotchi.rest_day():
            self.message_box.value = "Хорошо отдохнули! ☀️"
        else:
            self.message_box.value = "Не хватает денег на отдых!"
        self.update_ui()

    def on_work(self, e):
        self.tamagotchi.work()
        self.message_box.value = "Поработал! Заработал 20€ 💼"
        self.update_ui()

    def _game_loop(self):
        while self.running:
            time.sleep(2)
            self.tamagotchi.update()
            if not self.tamagotchi.alive:
                self.message_box.value = "💔 Тамагочи умер... Все параметры важны!"
                self.running = False
            elif self.tamagotchi.age_days >= 30:
                self.message_box.value = "🎉 Поздравляем! Вы вырастили тамагочи 30 дней!"
                self.running = False

    def update_ui_from_thread(self):
        self.update_ui()


def main(page: ft.Page):
    app = FletApp(page)


if __name__ == "__main__":
    ft.app(target=main)