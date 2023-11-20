import tkinter
import os
import re

import win32clipboard as winclip
import win32con
import HTMLClipboard as hcp
import AutoTabler as atr

from FormatTrashBinner import clean_trash_format
from BBCode import morph_html_to_bbcode
from NotallCHM import morph_notallbook_chm_html

#——————————————————————————————————————————

#显示剪贴板源数据
def clipboard_origin():
    # None
    abc = "abc"

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
        template: str = ""
        with open("template/Empty.htm","r",encoding="GBK") as f:
            template = f.read()
        with open("output.htm","w",encoding="GBK") as f:
            f.write(template.replace("{{内容}}",origin))
        print("已保存！")
    else:
        print("剪贴板为空/不是HTML！")
    
def save():
    # 保存
    origin = hcp.DumpHtml()
    if origin != "":
        with open("output.txt","w",encoding="UTF-8") as f:
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
            with open("output.txt","w",encoding="UTF-8") as f:
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

window = tkinter.Tk()
def a_button(text: str,command):
    tkinter.Button(window, text = text, command = command).pack()

a_button("显示当前剪贴板源数据",clipboard_origin)
#a_button("果园文本 -> rtf/doc(WIP)",goddess_to_rtf)
#a_button("rtf/doc -> 果园源数据(WIP)",goddess_to_rtf)
a_button("处理果园复制的富文本",goddess_process)
a_button("处理DOC/RTF复制的富文本",rtf_process)
a_button("html -> 果园BBcode",html_to_bbcode)
a_button("html -> 不全书格式",html_to_notall)
a_button("保存到output.htm",save_with_template_html)
a_button("保存到output.txt",save)
a_button("用已复制文本制作表格(用|分隔）",make_table)
#a_button("果园文本 -> 不全书html（文件）",goddess_to_html_file)
window.mainloop()