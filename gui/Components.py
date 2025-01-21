import tkinter
from tkinter import *
from tkinter.ttk import *

'''
# UI组件
'''
# Style定义
def style_init():
    style = tkinter.ttk.Style()
    style.configure("TFrame", background="#FCF8EC")
    style.configure("TLabel", background="#FCF8EC",justify='left',font=("微软雅黑", 10, ""))
    style.configure("length_label.TLabel", background="#FCF8EC",justify='left',font=("微软雅黑", 10, ""), height=1)
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
    Label(parent, text=text, justify='left', wraplength=400).pack(padx=1,side="top",fill="x")

# 按钮
def a_button(parent,action_name: str,description: str, command):
    #btn =Button(parent, text=action_name+"。"+description, command=command, style="TButton").pack(pady=1,padx=2,side="top",fill="x")
    #Label(btn, text=text, justify='left', wraplength=420).pack(padx=1,side="top",fill="x")
    #relief="ridge",bg="#FCF8EC"
    #height = math.ceil((len(action_name)+len(description)) * 15 / 400.0) +0.2
    text = Text(parent,height=1.2, background="#FCF8EC",wrap="char",font=("微软雅黑", 11),cursor='hand2',relief="flat") 
    text.insert(INSERT, action_name+"。"+description) 
    text.pack(pady=1,padx=2,side="top",fill="x") 
    text.config(state="disabled")
    text.bindtags((str(text), str(parent), "all"))
    text.bind("<Button-1>",command)
    text.tag_add("Aname", "1.0", "1."+str(len(action_name))) 
    text.tag_config("Aname", font=("微软雅黑", 11, "bold","italic")) 