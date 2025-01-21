
import math
import tkinter
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
#from tkinterweb import HtmlFrame
from gui.Components import *
from gui.Functions import *
from gui.Editor import Editor

window: Tk #窗口本体
#PREVIEWER: HtmlFrame #预览区域

class Simulacrum(tkinter.Tk):
    def __init__(self, version, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        window = self
        style_init()
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.title("果园格式拟像术 v"+version)
        self.iconbitmap('./icon/icon.ico')
        self.config(bg="#FCF8EC")
        #W.attributes("-toolwindow", 2)
        tabarea = Frame(self,width=400,height=500)
        tabarea.pack(side="left",fill="y")
        tabarea.pack_propagate(0)
        Separator(self, orient="vertical").pack(side="left",fill="y")
        editorarea = Frame(self,width=500,height=500)
        editorarea.pack(side="left",fill="both",expand=True)

        #功能列表
        a_big_title(tabarea,"功能 Traits")
        a_text(tabarea,"果园拟像术是用于处理html或rtf（doc文件之类的），靠暴力匹配去除其中无效的style等并格式化的工具。此版本并不稳定，请不要放心使用。\n"\
        "制表器识别|、(tabarea)、空格分隔单元格，识别换行为分行。"
        )
        a_title(tabarea,"测试 Test")
        a_button(tabarea,"测试A","获取剪贴板源数据（不处理）。",get_clipboard)
        a_button(tabarea,"测试B","预处理现有文本。",preprocess)
        a_title(tabarea,"获取 Input")
        a_button(tabarea,"粘贴","将剪贴板内数据粘贴到编辑器内。",get_clipboard_and_preprocess)
        #a_button(tabarea,"打开文件。打开本地的一个文件，将其读取到编辑器内。",load_file)
        a_title(tabarea,"HTML处理 HTML Process")
        a_button(tabarea,"净化之力","删除其所有html标签", html_to_text)
        a_button(tabarea,"果园侵袭","将其转换为果园BBcode。", html_to_bbcode)
        a_button(tabarea,"为何不全","将其转换为不全书的格式。", html_to_notall)
        a_title(tabarea,"文本处理 Text Process")
        a_button(tabarea,"处决不大写者","将其全部转化为首字母大写的格式。", word_capitalize)
        a_button(tabarea,"制表器猛击","将其转化为一张果园表格。", make_table)
        a_button(tabarea,"制表器能爆","将其转化为一张DND风格的html表格。", make_table)
        a_button(tabarea,"怪物创成α","将其转化为果园的东风5E2024怪物数据卡。", make_monster_statblock_bbc)
        a_button(tabarea,"怪物创成β","将其转化为不全书的5E2024怪物数据卡。", make_monster_statblock)
        a_title(tabarea,"输出 Output")
        a_button(tabarea,"复制·带格式","将其转化为带格式的文本并复制到剪贴板。", html_output_clipboard)
        a_button(tabarea,"复制·CHM","将其转化为CHM用文本并复制到剪贴板。", html_output_clipboard_test)
        a_button(tabarea,"复制·文本","将其直接复制到剪贴板。", text_output_clipboard)
        a_title(tabarea,"存储 Save")
        #a_button(tabarea,"文档。将现有内容保存为一个由你指定的.doc文件。", save_as_doc)
        a_button(tabarea,"网页文件","将其保存为一个由你指定的.htm文件。", save_as_htm)
        a_button(tabarea,"文本文件","将其保存为一个由你指定的.txt文件。", save_as_txt)
        
        #编辑区域
        a_big_title(editorarea,"编辑器 Editor")
        editor = Editor(editorarea,width=80,height=50,wrap="char",font=("微软雅黑", 11))
        editor.pack(fill="both", expand=True)
        
        #PREVIEWER = HtmlFrame(self,width=20)
        #PREVIEWER.pack(side="right",fill='y')
        
        
        # 每秒循环刷新事件
        #self.after(1000,on_refresh)
    
    # 每秒循环刷新
    def on_refresh(self,event):
        #print("[事件]滴答")
        root.after(1000,on_refresh)

    # 焦点进入
    def on_focus_in(self,event):
        print("[事件]焦点进入")
        origin = get_buffer()
        if origin == "":
            print("[提醒]自动获取开始")
            get_clipboard()
            preprocess()

    # 焦点离开
    def on_focus_out(self,event):
        print("[事件]焦点离开")

