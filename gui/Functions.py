import os
import re

from tkinter import filedialog
import win32clipboard as winclip
import pyclip
import win32con

import module.HTMLClipboard as hcp
import module.AutoTabler as atr
from module.Tools import purge_html, purge_bbcode
from module.FormatTrashBinner import clean_trash_format
from module.BBCode import morph_html_to_bbcode
from module.NotallCHM import morph_notallbook_chm_html
from module.HTMLTagTraverse import get_page_default_name
from module.SummonMonster import summon_monster

from gui.Editor import get_buffer, set_buffer, get_buffer_data_type

'''
# 基础功能
'''
# 获取剪贴板源数据（不处理）
def get_clipboard(event = None):
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
def preprocess(event = None):
    origin = get_buffer()
    if origin != "":
        if get_buffer_data_type() == "html":
            print("[提醒]预处理开始")
            output = clean_trash_format(origin)
            print("[提醒]预处理完成！")
            set_buffer(output,"html")
        else:
            print("[提醒]内容并非HTML，无需处理")
    else:
        print("[提醒]内容为空，无需处理")

# 获取剪贴板源数据并预处理
def get_clipboard_and_preprocess(event = None):
    get_clipboard()
    preprocess()

'''
# 转换功能
'''
# 数据类型转换
def transform_data_type(data:str,old_data_type:str,new_data_type:str):
    if old_data_type == "text":
        return data # 文本无法再修改
    trans = old_data_type+"→"+new_data_type
    if trans == "html→text":
        return purge_html(data) # 清除html格式
    elif trans == "bbcode→text":
        return purge_bbcode(data) # 清除bbcode格式
    elif trans == "html→bbcode":
        return morph_html_to_bbcode(data) # 转换html至bbcode
    elif trans == "bbcode→html":
        return "暂不支持由bbcode转html" #转换bbcode至html
    
    #不符合上述的，直接原封不动返回
    return data
    
# 将缓存区的HTML代码转化为纯文本
def html_to_text(event = None):
    origin = get_buffer("html")
    output = purge_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output,"text")
    
# 将缓存区的HTML代码转化为不全书html
def html_to_notall(event = None):
    origin = get_buffer("html")
    output = morph_notallbook_chm_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output,"html")

# 将缓存区的HTML代码转化为BBcode
def html_to_bbcode(event = None):
    origin = get_buffer()
    output = morph_html_to_bbcode(origin)
    print("[提醒]转换完成！")
    set_buffer(output,"bbcode")

'''
# 保存功能
'''
# 打开窗口，询问保存路径
def ask_save_file(default_name: str,suffix: str):
    if not os.path.exists("output"):
        os.makedirs("output")
    filetype = []
    if suffix in [".htm",".html"]:
        filetypes= [("不全书HTML文件", ".htm .html")]
    elif suffix in [".doc",".rtf"]:
        filetypes= [("RTF文件", ".doc .rtf")]
    elif suffix == ".txt":
        filetypes= [("文本文件", ".txt")]
    user_path = filedialog.asksaveasfile(title="请选择保存位置", initialdir="./output/", initialfile=default_name + suffix, filetypes=filetype, defaultextension=suffix)
    if user_path == None:
        print("[提醒]已取消保存。")
        return False, "", ""
    print("[提醒]正在保存至", user_path.name)
    file_name = os.path.splitext(os.path.basename(user_path.name))[0]
    return True, user_path.name, file_name

# 保存为html文件（使用模板）
def save_as_htm(event = None):
    origin = get_buffer()
    if origin != "":
        page_default_name = get_page_default_name(origin)
        template: str = ""
        with open("template/Empty.htm", "r", encoding="GBK") as f:
            template = f.read()
        # 打开窗口让用户选择
        decide, file_path, output_name = ask_save_file(page_default_name,".htm")
        if decide:
            with open(file_path, "w", encoding="GBK",errors="ignore") as f:
                f.write(template.replace("{{内容}}", origin).replace(
                    "{{标题}}", output_name))
            print("[提醒]保存完毕！")
    else:
        print("[警告]缓冲区为空！")

# 保存为文本文件
def save_as_txt(event = None):
    origin = get_buffer()
    if origin != "":
        if not os.path.exists("output"):
            os.makedirs("output")
        # 打开窗口让用户选择
        decide, file_path, output_name = ask_save_file("output",".txt")
        if decide:
            with open(file_path, "w", encoding="UTF-8",errors="ignore") as f:
                f.write(origin)
            print("[提醒]保存完毕！")
    else:
        print("[警告]缓冲区为空！")

'''
# 文本生成器功能
'''
# 将文本转化为每单词首字母大写格式
def word_capitalize(event = None):
    origin = get_buffer()
    output = origin.title().replace(" Of "," of ").replace(" In "," in ").replace(" The "," the ").replace(" On "," on ").replace("'S","'s").replace("'Ll","'ll").replace("'Ve","'ve")
    print("[提醒]已全部改为首字母大写！")
    set_buffer(output)

# 将文本生成为dnd样式(隔行染色，首行加粗)表格table
def make_table(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = atr.make_table(origin)
        print("[提醒]表格制作完成！")
        set_buffer(output,"html")

# 将文本生成为果园bbcode表格table（临时写法）
def make_bbcode_table(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = transform_data_type(atr.make_table(origin),"html","bbcode")
        print("[提醒]表格制作完成！")
        set_buffer(output,"bbcode")

# 将文本生成为果园怪物模板BBCode
def make_monster_statblock_bbc(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"Goddess5EMonster")
        print("[提醒]生物数据制作完成！")
        set_buffer(output,"bbcode")

# 将文本生成为不全书怪物模板html
def make_monster_statblock(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"Notall5EMonster")
        print("[提醒]生物数据制作完成！")
        set_buffer(output,"html")
'''
# 输出
'''
# 将缓冲区以HTML格式输出到剪贴板
def html_output_clipboard(event = None):
    origin = get_buffer("html")
    if origin != "":
        # 保留HTML标签，直接输出到剪贴板
        hcp.PutHtml(origin)
        print("[提醒]已将HTML代码输出到剪贴板")
    else:
        print("[提醒]缓冲区为空，未能复制。")

# 将缓冲区以HTML格式（至不全书版）输出到剪贴板
def html_output_clipboard_test(event = None):
    origin = get_buffer("html")
    if origin != "":
        # 保留HTML标签，直接输出到剪贴板
        hcp.PutHtml(origin,True) #暂时测试
        print("[提醒]已将HTML代码（至不全书版）输出到剪贴板")
    else:
        print("[提醒]缓冲区为空，未能复制。")

# 将缓冲区以文本输出到剪贴板
def text_output_clipboard(event = None):
    origin = get_buffer()
    if origin != "":
        #try:
        #    winclip.OpenClipboard()
        #    winclip.EmptyClipboard()
        #    winclip.SetClipboardData(win32con.CF_UNICODETEXT, origin)
        #    print("[提醒]已将文本输出到剪贴板")
        #finally:
        #    winclip.CloseClipboard()
        pyclip.copy(origin)
        print("[提醒]已将文本输出到剪贴板")
    else:
        print("[提醒]缓冲区为空，未能复制。")