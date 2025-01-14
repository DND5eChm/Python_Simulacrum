import os
import re
import pyclip
import tkinter
from tkinter import *
from tkinter.ttk import *
#from tkinterweb import HtmlFrame

import win32clipboard as winclip
import win32con
import HTMLClipboard as hcp
import AutoTabler as atr

from FormatTrashBinner import clean_trash_format
from BBCode import morph_html_to_bbcode
from NotallCHM import morph_notallbook_chm_html
from HTMLTagTraverse import get_page_default_name
from HTMLPurger import purge_html
from SummonMonster import summon_monster

VERSION = "0.6β 不稳定版"

root: Tk #窗口本体
BUFFER: Entry #缓冲区框
#PREVIEWER: HtmlFrame #预览区域

'''
# 基础功能
'''
# 获取剪贴板源数据（不处理）
def get_clipboard():
    data = hcp.DumpHtml()
    if data != "" and data != "None":
        set_buffer(data)
    else:
        try:
            winclip.OpenClipboard()
            text = winclip.GetClipboardData(win32con.CF_UNICODETEXT)
            if text != "":
                set_buffer(text)
            else:
                print("[提醒]剪贴板内容为空")
        except:
            print("[提醒]剪贴板内容无法识别。")
        finally:
            winclip.CloseClipboard()

# 预处理
def preprocess():
    origin = get_buffer()
    print("[提醒]预处理开始")
    output = clean_trash_format(origin)
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
    # 如果可预览的话，更新预览
    #if "<" in data:
    #    PREVIEWER.load_html(str(data))

'''
# 转换功能
'''
# 将html转化为纯文本
def html_to_text():
    origin = get_buffer()
    output = purge_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output)
    
# 将果园文本转化为不全书html
def html_to_notall():
    origin = get_buffer()
    output = morph_notallbook_chm_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output)

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

'''
# 文本生成器功能
'''
# 将文本转化为每单词首字母大写格式
def word_capitalize():
    origin = get_buffer()
    output = origin.title().replace(" Of "," of ").replace(" In "," in ").replace(" The "," the ").replace(" On "," on ").replace("'S","'s").replace("'Ll","'ll").replace("'Ve","'ve")
    print("[提醒]已全部改为首字母大写！")
    set_buffer(output)

# 将文本生成为dnd样式(隔行染色，首行加粗)表格table
def make_table():
    origin = get_buffer()
    if origin != "":
        output = origin.replace("<br>", "\n")
        output = re.compile(r'<[^>]+>', re.S).sub("", output)
        output = atr.make_table(output)
        print("[提醒]表格制作完成！")
        set_buffer(output)

# 将文本生成为果园怪物模板BBCode
def make_monster_statblock():
    origin = get_buffer()
    if origin != "":
        output = summon_monster(origin)
        print("[提醒]生物数据制作完成！")
        set_buffer(output)

'''
# 输出
'''
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
# UI事件
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

'''
# UI组件
'''
# Style定义
def style_init():
    style = tkinter.ttk.Style()
    style.configure("TFrame", background="#FCF8EC")
    style.configure("TLabel", background="#FCF8EC",justify='left',font=("微软雅黑", 10, ""))
    style.configure("TSeparator", background="#B79C61", height=1)
    style.configure("TButton",background="#FCF8EC",justify='left', anchor='w',relief="flat",font=("微软雅黑", 10, ""))
    style.configure("BTitle.TLabel", foreground="#800000", background="#FCF8EC",justify='left',font=("微软雅黑", 18, "bold"))
    style.configure("Title.TLabel", foreground="#800000", background="#FCF8EC",justify='left',font=("微软雅黑", 11, "bold"))
    style.configure("Buffer.TText", background="#FFFAEF",font=("", 8, ""))
    '''
    暂时看不懂，先放弃了
    style.map("TButton",
        foreground=[('!disabled','red'),('pressed', 'red'), ('active', 'blue')],
        background=[('!disabled','red'),('pressed', '!disabled', 'black'), ('active', 'red')]
    )
    '''

# 大标题
def a_big_title(text: str):
    Label(TABFRAME, text=text, justify='left',style="BTitle.TLabel").pack(padx=1,side="top",fill="x")
    Separator(TABFRAME, orient="horizontal").pack(padx=1,side="top",fill="x")

# 小标题
def a_title(text: str):
    Label(TABFRAME, text=text, justify='left',style="Title.TLabel").pack(padx=1,side="top",fill="x")
    Separator(TABFRAME, orient="horizontal").pack(padx=1,side="top",fill="x")

# 文本
def a_text(text: str):
    Label(TABFRAME, text=text, justify='left', wraplength=420).pack(padx=1,side="top",fill="x")

# 按钮
def a_button(text: str, command):
    Button(TABFRAME, text=text, command=command, style="TButton").pack(pady=1,padx=2,side="top",fill="x")
    #relief="ridge",bg="#FCF8EC"

# UI
if __name__ == "__main__":
    root = tkinter.Tk()
    style_init()
    root.bind("<FocusIn>", on_focus_in)
    root.bind("<FocusOut>", on_focus_out)
    root.title("果园格式拟像术 v"+VERSION)
    root.config(bg="#FCF8EC")
    #W.attributes("-toolwindow", 2)
    TABFRAME = Frame(root,width=30)
    TABFRAME.pack(side="left",fill="y")

    #显示界面
    a_big_title("功能 Traits")
    a_text("果园拟像术是用于处理html或rtf（doc文件之类的），靠暴力匹配去除其中无效的style等并格式化的工具。此版本并不稳定，请不要放心使用。")
    a_title("测试 Test")
    a_button("测试A。获取剪贴板源数据。",get_clipboard)
    a_button("测试B。预处理当前数据。",preprocess)
    a_title("处理 Process")
    a_button("净化。删除现有文本的所有html标签", html_to_text)
    a_button("处决不大写者。将现有文本转化为首字母大写的格式。", word_capitalize)
    a_button("制表符猛击。将现有文本转化为一张DND风格的html格式的表格(用|或TAB分隔)。", make_table)
    a_button("怪物创成。将现有文本转化为果园的东风5E怪物数据卡。", make_monster_statblock)
    a_button("果园侵袭。将现有html内容转换为果园BBcode。", html_to_bbcode)
    a_button("残缺·不全。将现有html内容转换为不全书或残缺大典的格式。", html_to_notall)
    a_title("输出 Output")
    a_button("HTML。将现有文本转化为HTML代码，输出到剪贴板。", html_output_clipboard)
    a_button("文本。将文本输出到剪贴板。", text_output_clipboard)
    a_title("存储 Save")
    a_button("HTML文件。将现有内容保存为一个由你指定的.htm或.html文件。", save_with_template_html)
    a_button("文本文件。将现有内容保存为output.txt。", save)
    
    #缓冲区
    Separator(TABFRAME, orient="vertical").pack(fill="y")
    scrollbar = Scrollbar(root, orient='vertical')
    scrollbar.pack(side="right", fill='y')
    BUFFER = Text(root,width=80,height=50,wrap="char", yscrollcommand=scrollbar.set)
    BUFFER.pack(side="right",fill="both", expand=True)
    scrollbar.config(command=BUFFER.yview)
    
    #PREVIEWER = HtmlFrame(root,width=20)
    #PREVIEWER.pack(side="right",fill='y')
    root.mainloop()
