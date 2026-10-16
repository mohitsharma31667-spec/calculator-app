import ast
import math
import os

os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, RoundedRectangle
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.image import Image

from main import calculate, format_answer


# ---------------- FONT ----------------

FONT_NAME = "Roboto"

if os.name == "nt":
    hindi_font = r"C:\Windows\Fonts\Nirmala.ttf"
    if os.path.exists(hindi_font):
        LabelBase.register(
            name="AppHindiFont",
            fn_regular=hindi_font
        )
        FONT_NAME = "AppHindiFont"


# ---------------- COLORS ----------------

BG = (0.025, 0.035, 0.055, 1)
PANEL = (0.065, 0.080, 0.115, 1)
KEY = (0.10, 0.12, 0.17, 1)
OPERATOR = (0.08, 0.20, 0.36, 1)
BLUE = (0.10, 0.38, 0.95, 1)
PRESSED = (0.20, 0.55, 1.0, 1)
WHITE = (0.94, 0.97, 1, 1)
MUTED = (0.55, 0.64, 0.77, 1)
RED = (0.45, 0.10, 0.15, 1)

Window.clearcolor = BG


# ---------------- BUTTON ----------------

class CalcButton(Button):
    def __init__(self, fill=KEY, **kwargs):
        super().__init__(**kwargs)

        self.fill = fill
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = WHITE
        self.font_name = FONT_NAME
        self.font_size = sp(19)
        self.bold = True

        with self.canvas.before:
            self.bg_color = Color(*self.fill)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )

        self.bind(pos=self.update_shape, size=self.update_shape)
        self.bind(on_press=self.press_effect)
        self.bind(on_release=self.release_effect)

    def update_shape(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def press_effect(self, *_):
        self.bg_color.rgba = PRESSED

    def release_effect(self, *_):
        Clock.schedule_once(self.restore_color, 0.12)

    def restore_color(self, _dt):
        self.bg_color.rgba = self.fill


# ---------------- APP ----------------

class MyCalculator(App):

    def build(self):
        self.title = "My Calculator"
        self.history = []
        self.fullscreen_enabled = False

        self.root_layout = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(9)
        )

        self.make_header()
        self.make_tabs()

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(9)
        )
        self.root_layout.add_widget(self.content)

        self.show_calculator()
        return self.root_layout

    # ---------------- HEADER ----------------

    def make_header(self):
        header = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(8)
        )

        full_btn = CalcButton(
            text="FS",
            size_hint_x=None,
            width=dp(48)
        )
        full_btn.bind(on_release=self.toggle_fullscreen)

        title = Label(
            text="MY CALCULATOR",
            font_name=FONT_NAME,
            color=WHITE,
            font_size=sp(20),
            bold=True,
            halign="left",
            valign="middle"
        )
        title.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        menu_btn = CalcButton(
            text="...",
            size_hint_x=None,
            width=dp(48)
        )
        menu_btn.bind(on_release=self.show_menu)

        header.add_widget(full_btn)
        header.add_widget(title)
        header.add_widget(menu_btn)
        self.root_layout.add_widget(header)

    def make_tabs(self):
        tabs = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8)
        )

        self.calc_tab = CalcButton(
            text="Calculator",
            fill=BLUE
        )
        self.calc_tab.bind(
            on_release=lambda *_: self.show_calculator()
        )

        self.converter_tab = CalcButton(
            text="Converter",
            fill=KEY
        )
        self.converter_tab.bind(
            on_release=lambda *_: self.show_converter()
        )

        tabs.add_widget(self.calc_tab)
        tabs.add_widget(self.converter_tab)
        self.root_layout.add_widget(tabs)

    def toggle_fullscreen(self, *_):
        self.fullscreen_enabled = not self.fullscreen_enabled
        Window.fullscreen = self.fullscreen_enabled

    # ---------------- MENU AND HISTORY ----------------

    def show_menu(self, *_):
        layout = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        history_btn = CalcButton(
            text="Calculation History",
            fill=OPERATOR,
            size_hint_y=None,
            height=dp(48)
        )
        close_btn = CalcButton(
            text="Close",
            size_hint_y=None,
            height=dp(44)
        )

        layout.add_widget(history_btn)
        layout.add_widget(close_btn)

        popup = Popup(
            title="Menu",
            content=layout,
            size_hint=(0.85, 0.35)
        )

        history_btn.bind(
            on_release=lambda *_: (
                popup.dismiss(),
                self.show_history()
            )
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_history(self, *_):
        text = "\n".join(self.history[-12:])
        if not text:
            text = "No history yet."

        label = Label(
            text=text,
            font_name=FONT_NAME,
            color=WHITE,
            halign="left",
            valign="top"
        )
        label.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )

        Popup(
            title="Calculation History",
            content=label,
            size_hint=(0.9, 0.7)
        ).open()

    # ---------------- CALCULATOR SCREEN ----------------

    def show_calculator(self, *_):
        self.calc_tab.fill = BLUE
        self.converter_tab.fill = KEY
        self.content.clear_widgets()

        display = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(5),
            size_hint_y=None,
            height=dp(145)
        )

        with display.canvas.before:
            Color(*PANEL)
            display.rect = RoundedRectangle(
                pos=display.pos,
                size=display.size,
                radius=[dp(20)]
            )

        display.bind(
            pos=lambda obj, *_:
            setattr(obj.rect, "pos", obj.pos),
            size=lambda obj, *_:
            setattr(obj.rect, "size", obj.size)
        )

        self.expression_input = TextInput(
            text="",
            hint_text="0",
            multiline=False,
            font_name=FONT_NAME,
            font_size=sp(30),
            foreground_color=WHITE,
            hint_text_color=MUTED,
            cursor_color=BLUE,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            padding=dp(8),
            size_hint_y=None,
            height=dp(58)
        )
        display.add_widget(self.expression_input)

        self.answer_label = Label(
            text="Answer appears here",
            font_name=FONT_NAME,
            color=BLUE,
            font_size=sp(19),
            halign="right",
            valign="middle",
            size_hint_y=None,
            height=dp(35)
        )
        self.answer_label.bind(
            size=lambda obj, val:
            setattr(obj, "text_size", val)
        )
        display.add_widget(self.answer_label)
        self.content.add_widget(display)

        photo_btn = CalcButton(
            text="CAMERA / CHOOSE PHOTO",
            fill=OPERATOR,
            size_hint_y=None,
            height=dp(46),
            font_size=sp(15)
        )
        photo_btn.bind(on_release=self.camera_message)
        self.content.add_widget(photo_btn)

        keys = GridLayout(
            cols=4,
            spacing=dp(7)
        )

        key_rows = [
            ("AC", RED), ("DEL", OPERATOR),
            ("(", OPERATOR), (")", OPERATOR),
            ("7", KEY), ("8", KEY), ("9", KEY), ("÷", OPERATOR),
            ("4", KEY), ("5", KEY), ("6", KEY), ("×", OPERATOR),
            ("1", KEY), ("2", KEY), ("3", KEY), ("-", OPERATOR),
            ("0", KEY), (".", KEY), ("=", BLUE), ("+", OPERATOR)
        ]

        for text, color in key_rows:
            button = CalcButton(text=text, fill=color)
            button.bind(on_release=self.press_key)
            keys.add_widget(button)

        self.content.add_widget(keys)

        footer = Label(
            text="SMART  •  SIMPLE  •  FAST",
            font_name=FONT_NAME,
            color=MUTED,
            font_size=sp(10),
            size_hint_y=None,
            height=dp(18)
        )
        self.content.add_widget(footer)

    # ---------------- MATH BUTTONS ----------------

    def press_key(self, button):
        key = button.text
        current = self.expression_input.text

        if key == "AC":
            self.expression_input.text = ""
            self.answer_label.text = "Answer appears here"
            return

        if key == "DEL":
            self.expression_input.text = current[:-1]
            return

        if key == "=":
            self.solve_question()
            return

        self.expression_input.text = current + key
        self.expression_input.cursor = (
            len(self.expression_input.text), 0
        )

    def solve_question(self, *_):
        original = self.expression_input.text.strip()

        if not original:
            self.answer_label.text = "Enter a question first"
            return

        text = original

        while text and text[-1] in "+-×÷*/^":
            text = text[:-1].rstrip()

        if not text:
            self.answer_label.text = "Invalid expression"
            return

        text = (
            text.replace("×", "*")
                .replace("÷", "/")
                .replace("^", "**")
        )

        if len(text) > 250:
            self.answer_label.text = "Expression too long"
            return

        allowed = set("0123456789+-*/(). %")
        if not all(char in allowed for char in text):
            self.answer_label.text = "Use a math expression"
            return

        try:
            tree = ast.parse(text, mode="eval")
            result = calculate(tree.body)

            if isinstance(result, complex):
                self.answer_label.text = "Unsupported calculation"
                return

            if isinstance(result, float) and not math.isfinite(result):
                self.answer_label.text = "Invalid result"
                return

            answer = str(format_answer(result))
            self.answer_label.text = "= " + answer
            self.history.append(original + " = " + answer)

        except ZeroDivisionError:
            self.answer_label.text = "Cannot divide by zero"
        except Exception:
            self.answer_label.text = "Invalid expression"

    # ---------------- PHOTO PICKER ----------------

    def camera_message(self, *_):
        chooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"],
            path=os.path.expanduser("~")
        )

        select_btn = CalcButton(
            text="SELECT PHOTO",
            fill=BLUE,
            size_hint_y=None,
            height=dp(46)
        )
        cancel_btn = CalcButton(
            text="CANCEL",
            fill=KEY,
            size_hint_y=None,
            height=dp(42)
        )

        layout = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8)
        )
        layout.add_widget(chooser)
        layout.add_widget(select_btn)
        layout.add_widget(cancel_btn)

        popup = Popup(
            title="Choose Question Photo",
            content=layout,
            size_hint=(0.92, 0.88)
        )

        def select_photo(*_):
            if not chooser.selection:
                self.answer_label.text = "Select a photo first"
                return

            path = chooser.selection[0]
            popup.dismiss()

            preview_layout = BoxLayout(
                orientation="vertical",
                spacing=dp(8),
                padding=dp(8)
            )

            preview_layout.add_widget(
                Image(source=path, allow_stretch=True, keep_ratio=True)
            )

            preview_layout.add_widget(
                Label(
                    text="Photo selected. OCR is not connected yet.",
                    font_name=FONT_NAME,
                    color=WHITE,
                    size_hint_y=None,
                    height=dp(48)
                )
            )

            close_btn = CalcButton(
                text="CLOSE",
                fill=BLUE,
                size_hint_y=None,
                height=dp(42)
            )
            preview_layout.add_widget(close_btn)

            preview_popup = Popup(
                title="Question Photo",
                content=preview_layout,
                size_hint=(0.9, 0.85)
            )
            close_btn.bind(on_release=preview_popup.dismiss)
            preview_popup.open()

        select_btn.bind(on_release=select_photo)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    # ---------------- UNIT CONVERTER ----------------

    def show_converter(self, *_):
        self.calc_tab.fill = KEY
        self.converter_tab.fill = BLUE
        self.content.clear_widgets()

        title = Label(
            text="UNIT CONVERTER",
            font_name=FONT_NAME,
            color=WHITE,
            font_size=sp(22),
            size_hint_y=None,
            height=dp(48)
        )
        self.content.add_widget(title)

        self.convert_input = TextInput(
            hint_text="Enter a number, e.g. 100",
            multiline=False,
            input_filter="float",
            font_name=FONT_NAME,
            font_size=sp(22),
            foreground_color=WHITE,
            cursor_color=BLUE,
            background_normal="",
            background_active="",
            background_color=PANEL,
            padding=dp(12),
            size_hint_y=None,
            height=dp(52)
        )
        self.content.add_widget(self.convert_input)

        units = [
            "Meter", "Kilometer", "Centimeter",
            "Millimeter", "Foot", "Inch"
        ]

        self.from_unit = Spinner(
            text="Meter",
            values=units,
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(48),
            background_color=OPERATOR,
            color=WHITE
        )
        self.to_unit = Spinner(
            text="Centimeter",
            values=units,
            font_name=FONT_NAME,
            size_hint_y=None,
            height=dp(48),
            background_color=OPERATOR,
            color=WHITE
        )

        self.content.add_widget(
            Label(text="From", font_name=FONT_NAME, color=MUTED,
                  size_hint_y=None, height=dp(24))
        )
        self.content.add_widget(self.from_unit)

        self.content.add_widget(
            Label(text="To", font_name=FONT_NAME, color=MUTED,
                  size_hint_y=None, height=dp(24))
        )
        self.content.add_widget(self.to_unit)

        convert_btn = CalcButton(
            text="CONVERT",
            fill=BLUE,
            size_hint_y=None,
            height=dp(50)
        )
        convert_btn.bind(on_release=self.convert_units)
        self.content.add_widget(convert_btn)

        self.convert_result = Label(
            text="Result appears here",
            font_name=FONT_NAME,
            color=BLUE,
            font_size=sp(20)
        )
        self.content.add_widget(self.convert_result)

    def convert_units(self, *_):
        try:
            value = float(self.convert_input.text)

            factors = {
                "Meter": 1.0,
                "Kilometer": 1000.0,
                "Centimeter": 0.01,
                "Millimeter": 0.001,
                "Foot": 0.3048,
                "Inch": 0.0254
            }

            meters = value * factors[self.from_unit.text]
            result = meters / factors[self.to_unit.text]

            self.convert_result.text = (
                f"{value:g} {self.from_unit.text}\n"
                f"= {result:.8g} {self.to_unit.text}"
            )

        except (ValueError, KeyError):
            self.convert_result.text = "Enter a valid number"


if __name__ == "__main__":
    MyCalculator().run()