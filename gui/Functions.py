import os
import re

from win32com.client import Dispatch
from pydocx import PyDocX

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

from gui.Editor import get_buffer, set_buffer,get_buffer_selected, set_buffer_selected, get_buffer_data_type, check_data_type, transform_data_type

'''
# 读取
'''
# 读取：获取剪贴板源数据（不处理）
def get_clipboard_raw() -> str:
    data = hcp.DumpHtml()
    if data != "" and data != "None":
        return data
    else:
        try:
            winclip.OpenClipboard()
            text = winclip.GetClipboardData(win32con.CF_UNICODETEXT)
            if text != "":
                return text
            else:
                print("[提醒]剪贴板内容为空")
                return ""
        except:
            print("[提醒]剪贴板内容无法识别。")
        finally:
            winclip.CloseClipboard()
    return ""

# 读取：获取剪贴板源数据（如果是HTML则进行预处理）
def get_clipboard() -> str:
    data = get_clipboard_raw()
    if check_data_type(data) == "html":
        data = preprocess(data)
    return data

# 功能：获取剪贴板内容，覆盖当前缓存区
def cmd_get_clipboard(event = None):
    set_buffer(get_clipboard())

# 功能：获取剪贴板内容并净化，覆盖当前缓存区
def cmd_get_clipboard_and_purge(event = None):
    data = get_clipboard()
    if check_data_type(data) == "html":
        data = purge_html(data)
    set_buffer(data)

# 功能：获取剪贴板内容，添加到当前缓存区的最后
def cmd_get_clipboard_addon(event = None):
    origin = get_buffer()
    data = get_clipboard()
    set_buffer(origin+data)

# 功能：将当前缓存区全部复制到剪贴板
def cmd_set_clipboard(event = None):
    data = get_buffer()
    if data != "":
        pyclip.copy(data)
        print("[提醒]已将选择文本复制到剪贴板")

# 功能：将当前缓存区全部复制到剪贴板，然后清空
def cmd_set_clipboard_and_delete(event = None):
    data = get_buffer()
    if data != "":
        pyclip.copy(data)
        set_buffer("")
        print("[提醒]已将选择文本剪切到剪贴板")

# 功能：清空当前缓存区
def cmd_clear(event = None):
    set_buffer("")

# 选区功能：获取剪贴板内容，覆盖当前选区
def selcmd_get_clipboard(event = None):
    set_buffer_selected(get_clipboard())

# 选区功能：获取剪贴板内容并净化，覆盖当前选区
def selcmd_get_clipboard_and_purge(event = None):
    data = get_buffer_selected()
    if check_data_type(data) == "html":
        data = purge_html(data)
    set_buffer_selected(data)

# 选区功能：将选区复制到剪贴板
def selcmd_set_clipboard(event = None):
    data = get_buffer_selected()
    if data != "":
        pyclip.copy(data)
        print("[提醒]已将选择文本复制到剪贴板")

# 选区功能：将选区复制到剪贴板，然后删除原选择区域
def selcmd_set_clipboard_and_delete(event = None):
    data = get_buffer_selected()
    if data != "":
        pyclip.copy(data)
        set_buffer_selected("")
        print("[提醒]已将选择文本剪切到剪贴板")

# 功能：将选区删除
def selcmd_delete(event = None):
    set_buffer_selected("")

# 处理：预处理
def preprocess(data: str):
    return clean_trash_format(data)

# 功能：预处理
def cmd_preprocess(event = None):
    origin = get_buffer()
    if origin != "":
        if get_buffer_data_type() == "html":
            print("[提醒]预处理开始")
            output = preprocess(origin)
            print("[提醒]预处理完成！")
            set_buffer(output,"html")
        else:
            print("[提醒]内容并非HTML，无需处理")
    else:
        print("[提醒]内容为空，无需处理")

# 读取：打开窗口，询问打开文件
def ask_open_file():
    filetype = [("拟像术材料成分",".htm .html .doc .docx .rtf .txt"),("不全书HTML文件", ".htm .html"),("RTF文件", ".doc .rtf"),("文本文件", ".txt")]
    user_path = filedialog.askopenfile(title="请选择要打开的文件",initialdir="./", filetypes=filetype)
        
    if user_path == None:
        print("[提醒]已取消读取。")
        return ""
    print("[提醒]正在读取", user_path.name)
    file_path = user_path.name
    #检查文件类型
    file_type = ""
    if file_path.endswith(".htm") or file_path.endswith(".html"):
                file_type = "html"
    elif file_path.endswith(".doc"):
                file_type = "doc"
    elif file_path.endswith(".docx"):
                file_type = "docx"
    else: #if file_path.endswith(".txt"):
                file_type = "txt"
    
    #根据类型读取
    output = ""
    
    #try:
    if file_type in ["doc","docx"]:
        if not os.path.exists("output"):
            os.makedirs("output")
        if file_type == "doc":
            word = Dispatch("WORD.Application")
            doc = word.Documents.Open(file_path)
            file_path = file_path + "x"
            doc.SaveAs(file_path,12,False,"",True,"",False,False,False,False)
            doc.Close()
            word.Quit()
        output = PyDocX.to_html(file_path)
        file_type = "html"
        
    #except:
    #    print("[警告]无法读取该RTF文件")'''
    else:
        try:
            with open(user_path.name,mode='r') as _f:
                output = _f.read()
        except:
            print("[警告]无法读取所选文件")
            return ""
        
    if file_type == "html":
        left = output.find("<body>")
        right = output.find("</body>")
        if left != -1 and right != -1:
            output = output[left+6:right]
        output = preprocess(output)
    if output != "":
        print("[提醒]读取完毕")
        return output
    else:
        print("[警告]未读取到内容")
        return ""

# 功能：打开窗口，询问打开文件
def cmd_ask_open_file(event = None):
    data = ask_open_file()
    if data != "":
        set_buffer(data)

'''
# 转换功能
'''
# 功能：将缓存区的HTML代码转化为纯文本
def cmd_html_to_text(event = None):
    origin = get_buffer("html")
    if origin != "":
        output = purge_html(origin)
        print("[提醒]处理完成！")
        set_buffer(output,"text")
    
# 功能：将缓存区的HTML代码转化为不全书html
def cmd_html_to_notall(event = None):
    origin = get_buffer("html")
    if origin != "":
        output = morph_notallbook_chm_html(origin)
        print("[提醒]处理完成！")
        set_buffer(output,"html")

# 功能：将缓存区的HTML代码转化为BBcode
def cmd_html_to_bbcode(event = None):
    origin = get_buffer()
    if origin != "":
        output = morph_html_to_bbcode(origin)
        print("[提醒]转换完成！")
        set_buffer(output,"bbcode")

'''
# 文本生成器功能
'''
# 选区功能：将鼠标所选的文本转化为每单词首字母大写格式
def selcmd_word_capitalize(event = None):
    origin = get_buffer_selected()
    if origin != "":
        output = origin.title().replace(" Of "," of ").replace(" In "," in ").replace(" The "," the ").replace(" On "," on ").replace("'S","'s").replace("'Ll","'ll").replace("'Ve","'ve")
        print("[提醒]已将所选文本改为首字母大写！")
        set_buffer_selected(output)

# 功能：将文本生成为dnd样式(隔行染色，首行加粗)表格table
def cmd_make_table(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = atr.make_table(origin)
        print("[提醒]表格制作完成！")
        set_buffer(output,"html")

# 功能：将文本生成为果园bbcode表格table（临时写法）
def cmd_make_bbcode_table(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = transform_data_type(atr.make_table(origin),"html","bbcode")
        print("[提醒]表格制作完成！")
        set_buffer(output,"bbcode")

# 功能：将文本生成为东风版果园怪物模板BBCode
def cmd_make_monster_statblock_bbc(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"Goddess5EMonster")
        print("[提醒]东风版果园怪物数据卡制作完成！")
        set_buffer(output,"bbcode")

# 功能：将文本生成为不全书怪物模板html
def cmd_make_monster_statblock(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"Notall5EMonster")
        print("[提醒]不全书2024数据卡制作完成！")
        set_buffer(output,"html")
        
# 功能：将文本生成为刺猬版怪物模板html
def cmd_make_monster_statblock_hedgehog(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"HedgehogMonster")
        print("[提醒]刺猬版数据卡制作完成！")
        set_buffer(output,"html")
        
# 功能：将文本生成为咸喵版怪物模板html
def cmd_make_monster_statblock_saltmeow(event = None):
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"SaltymeowMonster",True) #Legacy模式
        print("[提醒]咸喵版数据卡制作完成！")
        set_buffer(output,"html")
'''
# 输出
'''
# 功能：将缓存区以HTML格式输出到剪贴板
def cmd_html_output_clipboard(event = None):
    origin = get_buffer("html")
    if origin != "":
        # 保留HTML标签，直接输出到剪贴板
        hcp.PutHtml(origin)
        print("[提醒]已将HTML代码输出到剪贴板")
    else:
        print("[提醒]缓存区为空，未能复制。")

# 功能：将缓存区以HTML格式（至不全书版）输出到剪贴板
def cmd_html_output_clipboard_test(event = None):
    origin = get_buffer("html")
    if origin != "":
        # 保留HTML标签，直接输出到剪贴板
        hcp.PutHtml(origin,True) #暂时测试
        print("[提醒]已将HTML代码（至不全书版）输出到剪贴板")
    else:
        print("[提醒]缓存区为空，未能复制。")

# 功能：将缓存区以文本输出到剪贴板
def cmd_text_output_clipboard(event = None):
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
        print("[提醒]缓存区为空，未能复制。")


'''
# 存储功能
'''
# 存储：打开窗口，询问保存路径
def ask_save_file(default_name: str,suffix: str):
    if not os.path.exists("output"):
        os.makedirs("output")
    filetype = []
    if suffix in [".htm",".html"]:
        filetypes= [("不全书HTML文件", ".htm .html")]
    elif suffix in [".doc",".rtf"]:
        filetypes= [("RTF文件", ".doc .docx .rtf")]
    elif suffix == ".txt":
        filetypes= [("文本文件", ".txt")]
    user_path = filedialog.asksaveasfile(title="请选择保存位置", initialdir="./output/", initialfile=default_name + suffix, filetypes=filetype, defaultextension=suffix)
    if user_path == None:
        print("[提醒]已取消保存。")
        return False, "", ""
    print("[提醒]正在保存至", user_path.name)
    file_name = os.path.splitext(os.path.basename(user_path.name))[0]
    return True, user_path.name, file_name

# 功能：保存为html文件（使用模板）
def cmd_save_as_htm(event = None):
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
        print("[警告]缓存区为空！")

# 功能：保存为文本文件
def cmd_save_as_txt(event = None):
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
        print("[警告]缓存区为空！")