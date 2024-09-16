from tkinter import Tk, Button, filedialog
import os
import re

import win32clipboard as winclip
import win32con
import HTMLClipboard as hcp
import AutoTabler as atr

from FormatTrashBinner import clean_trash_format
from BBCode import morph_html_to_bbcode
from NotallCHM import morph_notallbook_chm_html
from HTMLTagTraverse import get_page_default_name

WINDOW: Tk

#——————————————————————————————————————————

#显示剪贴板源数据
def clipboard_origin():
    origin = hcp.DumpHtml()
    if origin != "":
        print(origin)
    else:
        try:
            winclip.OpenClipboard()
            text = winclip.GetClipboardData(win32con.CF_UNICODETEXT)
        finally:
            winclip.CloseClipboard()
        if text != "":
            print(text)
        else:
            print("剪贴板内容为空")

# 将果园文本转化为不全书html
def html_to_notall():
    origin = hcp.DumpHtml()
    output = morph_notallbook_chm_html(origin)
    print(output)
    print("完成！")
    hcp.PutHtml(output)

# 处理果园复制下来的文本
def goddess_process():
    origin = hcp.DumpHtml()
    output = clean_trash_format(origin,"goddess")
    print(output)
    print("完成！")
    hcp.PutHtml(output)

# 处理RTF复制下来的文本
def rtf_process():
    origin = hcp.DumpHtml().replace("\n","")
    output = clean_trash_format(origin,"rtf")
    print(output)
    print("完成！")
    hcp.PutHtml(output)


# 将果园文本转化为BBcode,然后存入剪贴板
def html_to_bbcode():
    origin = hcp.DumpHtml()
    output = morph_html_to_bbcode(origin)
    print(output)
    print("完成！")
    try:
        winclip.OpenClipboard()
        winclip.EmptyClipboard()
        winclip.SetClipboardData(win32con.CF_UNICODETEXT,output)
    finally:
        winclip.CloseClipboard()

#————————————————————
def save_with_template_html():
    # 保存，但以读取模板并填写的格式保存
    origin = hcp.DumpHtml()
    if origin != "":
        page_default_name = get_page_default_name(origin)
        template: str = ""
        with open("template/Empty.htm","r",encoding="GBK") as f:
            template = f.read()
        if not os.path.exists("output"):
            os.makedirs("output")
        #打开窗口让用户选择
        user_path = filedialog.asksaveasfile(title="请选择保存位置", initialdir="./output/", initialfile=page_default_name+".htm", filetypes=[("不全书HTML文件", ".htm .html")], defaultextension=".htm")
        if user_path == None:
            print("已取消保存")
            return
        print('已保存至：', user_path)
        output_name = os.path.splitext(os.path.basename(user_path.name))[0]
        with open(user_path.name,"w",encoding="GBK") as f:
            f.write(template.replace("{{内容}}",origin).replace("{{标题}}",output_name))
        print("已保存！")
    else:
        print("剪贴板为空/不是HTML！")
    
def save():
    # 保存
    origin = hcp.DumpHtml()
    if origin != "":
        if not os.path.exists("output"):
            os.makedirs("output")
        with open("output/output.txt","w",encoding="UTF-8") as f:
            f.write(origin)
        print("已保存！")
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
            with open("output/output.txt","w",encoding="UTF-8") as f:
                f.write(text)
                print("已保存！")
        else:
            print("剪贴板为空/无法解析！")

# 将文本转化为dnd样式的首行加粗间隔表格table
def make_table():
    origin = hcp.DumpHtml()
    if origin != "":
        output = origin.replace("<br>","\n")
        output = re.compile(r'<[^>]+>',re.S).sub("",output)
    else:
        winclip.OpenClipboard(0)
        src = winclip.GetClipboardData()
        output = src
        print(src)
        winclip.CloseClipboard()
    output = atr.make_table(output)
    print(output)
    print("完成！")
    hcp.PutHtml(output)


# UI
if __name__ == "__main__":
    WINDOW = Tk()
    def a_button(text: str,command):
        Button(WINDOW, text = text, command = command).pack()

    a_button("显示当前剪贴板源数据",clipboard_origin)
    a_button("处理果园复制的富文本",goddess_process)
    a_button("处理DOC/RTF复制的富文本",rtf_process)
    a_button("html -> 果园BBcode",html_to_bbcode)
    a_button("html -> 不全书格式",html_to_notall)
    a_button(f"保存为htm文件",save_with_template_html)
    a_button(f"保存为txt文件",save)
    a_button("用已复制文本制作表格(用|分隔）",make_table)
    WINDOW.mainloop()