import os
import re
import pyclip
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
#from tkinterweb import HtmlFrame

import win32clipboard as winclip
import win32con
import HTMLClipboard as hcp
import AutoTabler as atr

from Tools import purge_html, purge_bbcode

from FormatTrashBinner import clean_trash_format
from BBCode import morph_html_to_bbcode
from NotallCHM import morph_notallbook_chm_html
from HTMLTagTraverse import get_page_default_name
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
def get_buffer(as_data_type: str = "") -> str:
    output = BUFFER.get('0.0','end').strip()
    if chr(65279) in output:
        output = output.replace(chr(65279),"")
    
    # 如果有数据类型限制，尝试转换为该类数据
    if as_data_type != "" and BUFFER.data_type != as_data_type:
        return transform_data_type(output,BUFFER.data_type,as_data_type)
    return output

# 设置缓冲区数据
def set_buffer(data: str,data_type:str = "auto"):
    BUFFER.delete('1.0','end')
    BUFFER.insert("1.0",str(data))
    #不提供数据类型，则自动识别当前数据的类型
    if data_type == "auto":
        data_type = get_data_type(data)
    if BUFFER.data_type != data_type:
        BUFFER.data_type_change(data_type)
    # 如果可预览的话，更新预览
    #if "<" in data:
    #    PREVIEWER.load_html(str(data))

# 获取数据的格式类型
def get_data_type(data:str):
    if "</" in data and ">" in data:
        return "html"
    elif "[/" in data and "]" in data:
        return "bbcode"
    else:
        return "text"

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
def html_to_text():
    origin = get_buffer("html")
    output = purge_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output,"text")
    
# 将缓存区的HTML代码转化为不全书html
def html_to_notall():
    origin = get_buffer("html")
    output = morph_notallbook_chm_html(origin)
    print("[提醒]处理完成！")
    set_buffer(output,"html")

# 将缓存区的HTML代码转化为BBcode
def html_to_bbcode():
    origin = get_buffer()
    output = morph_html_to_bbcode(origin)
    print("[提醒]转换完成！")
    set_buffer(output,"bbcode")

'''
# 保存功能
'''
# 保存，但以读取模板并填写的格式保存
def save_as_html():
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
        print("[警告]缓冲区为空！")

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
        print("[警告]缓冲区为空！")

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
    origin = get_buffer("text")
    if origin != "":
        output = atr.make_table(origin)
        print("[提醒]表格制作完成！")
        set_buffer(output,"html")

# 将文本生成为果园bbcode表格table（临时写法）
def make_bbcode_table():
    origin = get_buffer("text")
    if origin != "":
        output = transform_data_type(atr.make_table(origin),"html","bbcode")
        print("[提醒]表格制作完成！")
        set_buffer(output,"bbcode")

# 将文本生成为果园怪物模板BBCode
def make_monster_statblock_bbc():
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"Goddess5EMonster")
        print("[提醒]生物数据制作完成！")
        set_buffer(output,"bbcode")

# 将文本生成为不全书怪物模板html
def make_monster_statblock():
    origin = get_buffer("text")
    if origin != "":
        output = summon_monster(origin,"Notall5EMonster")
        print("[提醒]生物数据制作完成！")
        set_buffer(output,"html")
'''
# 输出
'''
# 将缓冲区以HTML格式输出到剪贴板
def html_output_clipboard():
    origin = get_buffer("html")
    if origin != "":
        # 保留HTML标签，直接输出到剪贴板
        pyclip.copy(origin)
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
# 缓存区类
'''
class BufferText(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.data_type = "text"
        self.data_type_str = "纯文本"
        self.data_length = 0
        self._orig = self._w+'_orig'
        self.tk.call('rename',self._w,self._orig)
        self.tk.createcommand(self._w,self._proxy)
    
    # 事件交接
    def _proxy(self, command, *args):
        if command in ['get','delete'] and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'):
            return
        cmd = (self._orig,command) + args
        result = self.tk.call(cmd)
        if command in ['insert','delete','replace']:
            self.event_generate('<<TextModified>>')
        return result
    
    # 类型更新
    def data_type_change(self, new_data_type:str):
        if new_data_type != self.data_type:
            self.data_type = new_data_type
            if new_data_type == "html": # html类型不自动换行
                self.config(wrap="none")
            else:
                self.config(wrap="char")
            
        
        if self.data_type == "html":
            self.data_type_str = "HTML代码"
        elif self.data_type == "bbcode":
            self.data_type_str = "果园BBCode"
        else: #self.data_type == "text":
            self.data_type_str = "纯文本"

'''
# UI事件
'''
# 每秒循环刷新
def on_refresh(event):
    #print("[事件]滴答")
    root.after(1000,on_refresh)

# 焦点进入
def on_focus_in(event):
    print("[事件]焦点进入")
    origin = get_buffer()
    if origin == "":
        print("[提醒]自动获取开始")
        get_clipboard()
        preprocess()

# 焦点离开
def on_focus_out(event):
    print("[事件]焦点离开")

# 手动更改缓存区事件
def on_buffer_changed(event):
    data = BUFFER.get("0.0","end")
    new_data_type = get_data_type(data)
    if new_data_type != BUFFER.data_type:
         BUFFER.data_type_change(new_data_type)
    BUFFER.data_length = len(data)
    length_label.config(text=str(BUFFER.data_length)+" 字符，数据类型："+BUFFER.data_type_str)
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
def a_big_title(parent,text: str):
    Label(parent, text=text, justify='left',style="BTitle.TLabel").pack(padx=1,side="top",fill="x")
    Separator(parent, orient="horizontal").pack(padx=1,side="top",fill="x")

# 小标题
def a_title(parent,text: str):
    Label(parent, text=text, justify='left',style="Title.TLabel").pack(padx=1,side="top",fill="x")
    Separator(parent, orient="horizontal").pack(padx=1,side="top",fill="x")

# 文本
def a_text(parent,text: str):
    Label(parent, text=text, justify='left', wraplength=420).pack(padx=1,side="top",fill="x")

# 按钮
def a_button(parent,text: str, command):
    Button(parent, text=text, command=command, style="TButton").pack(pady=1,padx=2,side="top",fill="x")
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
    tab = Frame(root,width=20)
    tab.pack(side="left",fill="y")
    Separator(root, orient="vertical").pack(side="left",fill="y")
    editor = Frame(root,width=30)
    editor.pack(side="right",fill="y")

    #功能列表
    a_big_title(tab,"功能 Traits")
    a_text(tab,"果园拟像术是用于处理html或rtf（doc文件之类的），靠暴力匹配去除其中无效的style等并格式化的工具。此版本并不稳定，请不要放心使用。")
    a_title(tab,"测试 Test")
    a_button(tab,"测试A。获取剪贴板源数据。",get_clipboard)
    a_button(tab,"测试B。预处理当前数据。",preprocess)
    a_title(tab,"处理 Process")
    a_button(tab,"净化。删除现有文本的所有html标签", html_to_text)
    a_button(tab,"处决不大写者。将现有文本全部转化为首字母大写的格式。", word_capitalize)
    a_button(tab,"制表符猛击。将现有文本转化为一张DND风格的果园表格（可识别|、tab、空格分隔）。", make_table)
    a_button(tab,"制表符猛击·二型。将现有文本转化为一张DND风格的html表格（可识别|、tab、空格分隔）。", make_table)
    a_button(tab,"怪物创成·升华。将现有文本转化为果园的东风5E2024怪物数据卡。", make_monster_statblock_bbc)
    a_button(tab,"怪物创成·沉降。将现有文本转化为不全书的5E2024怪物数据卡。", make_monster_statblock)
    a_button(tab,"果园侵袭。将现有html内容转换为果园BBcode。", html_to_bbcode)
    a_button(tab,"为何不全？将现有html内容转换为不全书的格式。", html_to_notall)
    a_title(tab,"输出 Output")
    a_button(tab,"带格式。将现有文本转化为带HTML格式的文本，复制到剪贴板。", html_output_clipboard)
    a_button(tab,"文本。将现有文本直接复制到剪贴板。", text_output_clipboard)
    a_title(tab,"存储 Save")
    #a_button(tab,"文档。将现有内容保存为一个由你指定的.doc文件。", save_as_doc)
    a_button(tab,"网页。将现有内容保存为一个由你指定的.html文件。", save_as_html)
    a_button(tab,"文本。将现有内容保存为output.txt。", save)
    
    #编辑区域
    a_big_title(editor,"编辑器 Editor")
    BUFFER = BufferText(editor,width=80,height=50,wrap="char")
    BUFFER.bind("<<TextModified>>", on_buffer_changed)
    BUFFER.data_type = "text"
    
    scrollbar = Scrollbar(editor, orient='vertical')
    BUFFER.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill='y')
    scrollbar.config(command=BUFFER.yview)
    length_label = Label(editor,text="0 字符")
    length_label.pack(side="bottom",fill="x", expand=True)
    
    BUFFER.pack(fill="both", expand=True)
    
    #PREVIEWER = HtmlFrame(root,width=20)
    #PREVIEWER.pack(side="right",fill='y')
    
    
    # 每秒循环刷新事件
    #root.after(1000,on_refresh)
    #UI循环开始，也即代码结束
    root.mainloop()
