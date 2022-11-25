from threading import Thread
import win32api
from PIL import ImageGrab
import pyocr
import ctypes
import time
import tkinter as tk
from requests import post
pyocr.tesseract.TESSERACT_CMD = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class ClipboardOCR:
    def __init__(self):
        self.tool = pyocr.get_available_tools()[0]
        self.builder = pyocr.builders.TextBuilder(tesseract_layout=6)
        self.text = ""

    def run(self, lang="jpn"):
        img = ImageGrab.grabclipboard()
        if img:
            self.text = self.tool.image_to_string(img, lang=lang, builder=self.builder)
        return self.text


def get_key_state(keycode):
    return win32api.GetAsyncKeyState(keycode) >> 15 < 0


def runClipboardOCR(lang="eng"):
    text = c.run(lang)
    return text


class Translator:
    def __init__(self, auth_key):
        self.data = {
            "source_lang": "EN",
            "target_lang": "JA",
            "split_sentences": "nonewlines",
            "auth_key": auth_key,
        }

    def translate(self, tk, text):
        task = Thread(
            target=self._translate,
            args=(
                tk,
                text,
            ),
            daemon=True,
        )
        task.start()

    def _translate(self, tk, text):
        tr_text = (
            post(
                "https://api-free.deepl.com/v2/translate",
                data=self.data | {"text": text},
            )
            .json()["translations"][0]
            .get("text")
        )
        print(tr_text)
        tk.label["text"] = tr_text
        x1, x2, y1, y2 = tk.coor
        tk.geometry(f"{x2-x1}x{max(tk.label.winfo_reqheight()+40, y2-y1)}+{x1}+{y1}")


class Application(tk.Tk):
    def __init__(self, x1, x2, y1, y2):
        super().__init__()
        self.coor = x1, x2, y1, y2
        self.title("Transparent window")
        self.attributes("-alpha", 0.95)
        self.attributes("-topmost", True)
        self.bind("<Configure>", self.sized)
        self.bind("<Shift-ButtonPress-1>", toggleOverrideRedirect)
        time.sleep(0.5)
        self.quit = tk.Button(self, text="x", command=self.destroy)
        self.quit.place(relx=1, rely=0, anchor="ne")
        self.text = runClipboardOCR()
        self.label = tk.Label(
            self,
            font=("游ゴシック", "12"),
            anchor="e",
            justify="left",
            text=self.text,
        )
        tr.translate(self, self.text)
        self.label.pack(expand=True)
        self.geometry(
            f"{x2-x1}x{max(self.label.winfo_reqheight()+40, y2-y1)}+{x1}+{y1}"
        )

    def sized(self, *args):
        self.label["wraplength"] = self.winfo_width() - 40


def toggleOverrideRedirect(ev):
    win = ev.widget.winfo_toplevel()
    win.overrideredirect(not win.overrideredirect())
    win.withdraw()
    win.deiconify()
    win.focus_force()
    return


def get_rectcoordinate():
    class _pointer(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_long),
            ("y", ctypes.c_long),
        ]

    point = _pointer()
    vk_leftbutton = 0x01
    while 1:
        if ctypes.windll.user32.GetAsyncKeyState(vk_leftbutton) == 0x8000:
            ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
            x1, y1 = point.x, point.y
            while ctypes.windll.user32.GetAsyncKeyState(vk_leftbutton) == 0x8000:
                pass
            break
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    x2, y2 = point.x, point.y
    return x1, x2, y1, y2


if __name__ == "__main__":
    AUTH_KEY =  "" # auth_keyを入力
    c = ClipboardOCR()
    tr = Translator(AUTH_KEY)

    while True:
        if get_key_state(91) and get_key_state(16) and get_key_state(83):
            app = Application(*get_rectcoordinate())
            app.overrideredirect(1)
            app.mainloop()
