from tkinter import Tk, Frame, Text, Button, Label, Entry, Scrollbar, filedialog, font
from tkinter.ttk import Style, Separator
import os
import re
import pyclip

import win32clipboard as winclip
import win32con
import HTMLClipboard as hcp
import AutoTabler as atr

from FormatTrashBinner import clean_trash_format
from BBCode import morph_html_to_bbcode
from NotallCHM import morph_notallbook_chm_html
from HTMLTagTraverse import get_page_default_name

VERSION = "0.5β 不稳定版"

W: Tk #窗口本体
BUFFER: Entry #缓冲区框

'''
# 基础功能
'''
# 获取剪贴板源数据（不处理）
def get_clipboard():
    data = hcp.DumpHtml()
    if data != "":
        set_buffer(data)
    else:
        try:
            winclip.OpenClipboard()
            text = winclip.GetClipboardData(win32con.CF_UNICODETEXT)
        finally:
            winclip.CloseClipboard()
        if text != "":
            set_buffer(text)
        else:
            print("[提醒]剪贴板内容为空")

# 预处理
def preprocess():
    origin = get_buffer()
    print("[提醒]预处理开始")
    output = clean_trash_format(data)
    print("[提醒]预处理完成！")
    set_buffer(output)

# 获取缓冲区数据
def get_buffer() -> str:
    output = BUFFER.get('0.0','end').strip()
    return output

# 设置缓冲区数据
def set_buffer(data: str):
    BUFFER.delete('1.0','end')
    BUFFER.insert("1.0",str(data))

# 将果园文本转化为不全书html
def html_to_notall():
    origin = get_buffer()
    output = morph_notallbook_chm_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output)

'''
# 转换功能
'''
# 将果园文本转化为BBcode
def html_to_bbcode():
    origin = get_buffer()
    output = morph_html_to_bbcode(origin)
    print("[提醒]转换完成！")
    set_buffer(output)

'''
# 保存功能
'''
# 保存，但以读取模板并填写的格式保存
def save_with_template_html():
    origin = get_buffer()
    if origin != "":
        page_default_name = get_page_default_name(origin)
        template: str = ""
        with open("template/Empty.htm", "r", encoding="GBK") as f:
            template = f.read()
        if not os.path.exists("output"):
            os.makedirs("output")
        # 打开窗口让用户选择
        user_path = filedialog.asksaveasfile(title="请选择保存位置", initialdir="./output/", initialfile=page_default_name +
                                             ".htm", filetypes=[("不全书HTML文件", ".htm .html")], defaultextension=".htm")
        if user_path == None:
            print("已取消保存")
            return
        print("[提醒]已保存至：", user_path.name)
        output_name = os.path.splitext(os.path.basename(user_path.name))[0]
        with open(user_path.name, "w", encoding="GBK",errors="ignore") as f:
            f.write(template.replace("{{内容}}", origin).replace(
                "{{标题}}", output_name))
        print("[提醒]已保存！")
    else:
        print("[警告]剪贴板为空/不是HTML！")

# 保存
def save():
    origin = get_buffer()
    if origin != "":
        if not os.path.exists("output"):
            os.makedirs("output")
        with open("output/output.txt", "w", encoding="UTF-8") as f:
            f.write(origin)
        print("[提醒]已保存！")
    else:
        text = ""
        try:
            winclip.OpenClipboard()
            text = winclip.GetClipboardData(win32con.CF_UNICODETEXT)
        finally:
            winclip.CloseClipboard()
        if text != "":
            if not os.path.exists("output"):
                os.makedirs("output")
            with open("output/output.txt", "w", encoding="UTF-8") as f:
                f.write(text)
                print("[提醒]已保存！")
        else:
            print("[警告]剪贴板为空/无法解析！")

# 将文本转化为dnd样式的首行加粗间隔表格table
def make_table():
    origin = get_buffer()
    if origin != "":
        output = origin.replace("<br>", "\n")
        output = re.compile(r'<[^>]+>', re.S).sub("", output)
        output = atr.make_table(output)
        print("[提醒]表格制作完成！")
        set_buffer(output)

# 将缓冲区以HTML格式输出到剪贴板
def html_output_clipboard():
    origin = get_buffer()
    if origin != "":
        # 保留HTML标签，直接输出到剪贴板
        pyperclip.copy(origin)
        print("[提醒]已将HTML代码输出到剪贴板")
    else:
        print("[提醒]缓冲区为空，未能复制。")

# 将缓冲区以文本输出到剪贴板
def text_output_clipboard():
    origin = get_buffer()
    if origin != "":
        try:
            winclip.OpenClipboard()
            winclip.EmptyClipboard()
            winclip.SetClipboardData(win32con.CF_UNICODETEXT, origin)
            print("[提醒]已将文本输出到剪贴板")
        finally:
            winclip.CloseClipboard()
    else:
        print("[提醒]缓冲区为空，未能复制。")

'''
# UI系统
'''
# 焦点进入
def on_focus_in(event):
    print("[提醒]焦点进入")
    origin = get_buffer()
    if origin == "":
        print("[提醒]自动获取开始")
        get_clipboard()
        preprocess()

# 焦点离开
def on_focus_out(event):
    print("[提醒]焦点离开")

# UI
if __name__ == "__main__":
    W = Tk()
    W.bind("<FocusIn>", on_focus_in)
    W.bind("<FocusOut>", on_focus_out)
    W.title("果园格式拟像术 v"+VERSION)
    W.config(bg="#FCF8EC")
    #W.attributes("-toolwindow", 2)
    TABFRAME = Frame(W,width=30,bg="#FCF8EC")
    TABFRAME.pack(side="left",fill="y")
    TITLEFONT = font.Font(weight="bold")
    BIGTITLEFONT = font.Font(weight="bold",size="16")

    def a_big_title(text: str):
        Label(TABFRAME, text=text, justify='left',bg="#FCF8EC", anchor='w', fg="#800000", font=BIGTITLEFONT).pack(side="top",fill="x")
        Separator(TABFRAME, orient="horizontal").pack(side="top",fill="x")
        
    def a_title(text: str):
        Label(TABFRAME, text=text, justify='left',bg="#FCF8EC", anchor='w', fg="#800000", font=TITLEFONT).pack(side="top",fill="x")
        Separator(TABFRAME, orient="horizontal").pack(side="top",fill="x")
    
    def a_text(text: str):
        Label(TABFRAME, text=text, justify='left',bg="#FCF8EC", anchor='w', wraplength=420).pack(side="top",fill="x")
    
    def a_button(text: str, command):
        Button(TABFRAME, text=text, command=command,relief="ridge", justify='left', anchor='w',bg="#FCF8EC").pack(pady=1,padx=2,side="top",fill="x")

    #显示界面
    a_big_title("功能 Traits")
    a_text("果园拟像术是用于处理html或rtf（doc文件之类的），靠暴力匹配去除其中无效的style等并格式化的工具。此版本并不稳定，请不要放心使用。")
    a_title("测试 Test")
    a_button("测试A。获取剪贴板源数据。",get_clipboard)
    a_button("测试B。预处理当前数据。",preprocess)
    a_title("处理 Process")
    a_button("制表符猛击。拟像术将现有文本转化为一张html格式的表格(用|或TAB分隔)。", make_table)
    a_button("果园侵袭。拟像术将现有html内容转换为果园BBcode。", html_to_bbcode)
    a_button("残缺·不全。拟像术将现有html内容转换为不全书或残缺大典的格式。", html_to_notall)
    a_title("输出 Output")
    a_button("HTML。将数据转化为HTML代码，输出到剪贴板。", html_output_clipboard)
    a_button("文本。将文本输出到剪贴板。", text_output_clipboard)
    a_title("存储 Save")
    a_button("HTML文件。拟像术将现有内容保存为一个由你指定的htm文件。", save_with_template_html)
    a_button("TXT文件。拟像术将现有内容保存为一个由你指定的txt文件。", save)
    
    #缓冲区
    Separator(TABFRAME, orient="vertical").pack(fill="y")
    scrollbar = Scrollbar(W, orient='vertical')
    scrollbar.pack(side="right", fill='y')
    BUFFER = Text(W,width=60,height=50,bg="#FFFAEF",wrap="char", yscrollcommand=scrollbar.set)
    BUFFER.pack(side="right",fill="both", expand=True)
    scrollbar.config(command=BUFFER.yview)
    W.mainloop()
