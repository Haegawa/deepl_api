import os
from PIL import Image
from PIL import ImageGrab
import pyocr
import pyocr.builders
import requests
import tkinter
from tkinter import font
import os
pyocr.tesseract.TESSERACT_CMD = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

class ClipboardOCR():
    def __init__(self):
        # OCRエンジンの取得
        self.tool = pyocr.get_available_tools()[0]
        self.builder = pyocr.builders.TextBuilder()
        self.text = ""

    def preproseccing(self, img_org):
        img_rgb = img_org.convert("RGB")
        pixels = img_rgb.load()
        # 原稿画像加工（黒っぽい色以外は白=255,255,255にする）
        c_max = 169
        for j in range(img_rgb.size[1]):
            for i in range(img_rgb.size[0]):
                if (pixels[i, j][0] > c_max or pixels[i, j][1] > c_max or
                        pixels[i, j][0] > c_max):
                    pixels[i, j] = (255, 255, 255)
            
        return img_rgb
            
    def extract_text(self, lang="jpn"):
        img = ImageGrab.grabclipboard()
        #img = self.preproseccing(img)
        # ocr実行
        if img:
            self.text = self.tool.image_to_string(img, lang=lang, builder=self.builder)
        
        return self.text

class Translate():
    def __init__(self, API_KEY):
        c = ClipboardOCR()
        self.text = c.extract_text()

        source_lang = 'EN'
        target_lang = 'JA'
        # パラメータの指定
        self.params = {
                    'auth_key' : API_KEY,
                    'text' : self.text,
                    'source_lang' : source_lang, # 翻訳対象の言語
                    "target_lang": target_lang  # 翻訳後の言語
                }

    def translate(self):
        # リクエストを投げる
        request = requests.post("https://api-free.deepl.com/v2/translate", data=self.params) # URIは有償版, 無償版で異なるため要注意
        result = request.json()
        text = result["translations"][0]["text"]

        print(text)

        return text

class GUI():
    def __init__(self):
        # t = Translate()
        # self.text = t.translate()

        self.root = tkinter.Tk()

    def show_gui(self, text):
        self.root.title("deepl 翻訳結果")
        font1 = font.Font(family="メイリオ")
        label = tkinter.Label(self.root, text=text, font=font1)
        label.pack(side="top")

        self.root.mainloop()


if __name__ == "__main__":
    AUTH_KEY =  os.getenv("DEEPL_AUTH_KEY") # auth_keyを入力
    AUTH_KEY = ""
    #c = ClipboardOCR()
    #t = Translate(AUTH_KEY, text)
    g = GUI()

    while True:
        t = Translate(AUTH_KEY)
        text = t.translate()
        g.show_gui(text)


        