from tkinter import *
from tkinter.ttk import *

import module.HTMLClipboard as hcp
from module.Tools import purge_html, purge_bbcode
from module.BBCode import morph_html_to_bbcode

'''
# 编辑器·缓存区类
'''
class Editor(Text):
    Buffer = None

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        Editor.Buffer = self
        self.data_type = "text"
        self.data_type_str = "纯文本"
        self.data_length = 0
        self.length_label = None
        self._orig = self._w+'_orig'
        self.tk.call('rename',self._w,self._orig)
        self.tk.createcommand(self._w,self._proxy)
        self.bind("<<TextModified>>", self.on_editor_changed)
    
    # 事件交接
    def _proxy(self, command, *args):
        if command in ['get','delete'] and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'):
            return
        cmd = (self._orig,command) + args
        result = self.tk.call(cmd)
        if command in ['insert','delete','replace']:
            self.event_generate('<<TextModified>>')
        return result
    
    # 打包
    def pack(self, *args, **kwargs):
        self.scrollbar_y = Scrollbar(self.master, orient='vertical')
        self.scrollbar_x = Scrollbar(self.master, orient='horizontal')
        self.config(yscrollcommand=self.scrollbar_y.set,xscrollcommand=self.scrollbar_x.set)
        self.length_label = Label(self.master,text=str(self.data_length)+" 字符，数据类型："+self.data_type_str,style="length_label.TLabel")
        self.scrollbar_x.config(command=self.xview)
        self.scrollbar_y.config(command=self.yview)
        # 打包各部件
        self.length_label.pack(side="bottom",fill="x", expand=True)
        #self.scrollbar_x.pack(side="bottom", fill='x')
        self.scrollbar_y.pack(side="right", fill='y')
        Text.pack(self, *args, **kwargs)
    
    # 手动更改缓存区事件
    def on_editor_changed(self,event):
        data = self.get("0.0","end")
        new_data_type = get_data_type(data)
        if new_data_type != self.data_type:
             self.data_type_change(new_data_type)
        self.data_length = len(data)
        # 更新提示栏
        if self.length_label:
            self.length_label.config(text=str(self.data_length)+" 字符，数据类型："+self.data_type_str)
    
    # 类型更新
    def data_type_change(self, new_data_type:str):
        self.data_type = new_data_type
        if new_data_type == "html": # html类型不自动换行
            self.config(wrap="none")
            self.scrollbar_x.pack(side="bottom", fill='x')
        else:
            self.config(wrap="char")
            self.scrollbar_x.pack_forget()
            
        if self.data_type == "html":
            self.data_type_str = "HTML代码"
        elif self.data_type == "bbcode":
            self.data_type_str = "果园BBCode"
        else: #self.data_type == "text":
            self.data_type_str = "纯文本"
        # 更新提示栏
        if self.length_label:
            self.length_label.config(text=str(self.data_length)+" 字符，数据类型："+self.data_type_str)

"""
编辑Editor内数据
"""
# 获取缓冲区数据
def get_buffer(as_data_type: str = "") -> str:
    output = Editor.Buffer.get('0.0','end').strip()
    if chr(65279) in output:
        output = output.replace(chr(65279),"")
    
    # 如果有数据类型限制，尝试转换为该类数据
    if as_data_type != "" and Editor.Buffer.data_type != as_data_type:
        return transform_data_type(output,Editor.Buffer.data_type,as_data_type)
    return output

# 设置缓冲区数据
def set_buffer(data: str,data_type:str = "auto"):
    Editor.Buffer.delete('1.0','end')
    Editor.Buffer.insert("1.0",str(data))
    #不提供数据类型，则自动识别当前数据的类型
    if data_type == "auto":
        data_type = get_data_type(data)
    if Editor.Buffer.data_type != data_type:
        Editor.Buffer.data_type_change(data_type)
    # 如果可预览的话，更新预览
    #if "<" in data:
    #    PREVIEWER.load_html(str(data))

# 获取缓冲区数据类型
def get_buffer_data_type():
    return Editor.Buffer.data_type

# 获取数据的格式类型
def get_data_type(data:str):
    if "</" in data and ">" in data:
        return "html"
    elif "[/" in data and "]" in data:
        return "bbcode"
    else:
        return "text"

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