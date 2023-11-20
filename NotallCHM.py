import os
import re

from AutoTabler import fix_table

# 将span改为不全书格式的font
def morph_span_to_chm_font(span_text: str) -> str:
    def morph_text(text: str):
        left = text.find("\"")
        right = text.find("\"",left+1)
        if left == -1 or right == -1:
            print(text)
            print("出错，遇到未闭合的style")
            return text
        forms = text[left+1:right].split(";")
        #print(text)
        #print(str(left)+"  "+str(right)+"  "+str(forms))
        new_texts = []
        for form in forms:
            form = form.strip()
            arg: str = ""
            if form.startswith("color:"):
                arg = form[6:].strip()
                if arg.startswith("#"):
                    new_texts.append("color=" + arg)
                elif arg.startswith("rgb("):
                    arg = arg[4:-1]
                    col = [int(c) for c in arg.split(",")]
                    new_texts.append("color=" + str(hex((col[0] << 16)+(col[1] << 8)+col[2])).replace("0x","#"))
                elif arg == "brown":
                    new_texts.append("color=#800000")
                else:
                    new_texts.append("color=" + arg)
            elif form.startswith("font-size:"):
                arg = form[10:].strip()
                if arg == "36pt":
                    new_texts.append("size=6")
                elif arg == "24pt":
                    new_texts.append("size=5")
                elif arg == "18pt" or arg == "16pt":
                    new_texts.append("size=4")
                elif arg.endswith("pt"):
                    size: int = round(int(arg[:-2]) / 4)
                    new_texts.append("size="+str(size)+"px")
                else:
                    new_texts.append("size="+arg)
        
        return "<font "+" ".join(new_texts)+">"
    
    output: str = span_text
    length: int = len(output)
    i: int = 0
    j: int = 0
    while(i < length):
        if output[i] == "<":
            if i+6 < length and output[i:i+5] == "<span":
                right = output.find(">",i)
                if right != -1:
                    sub_text = morph_text(output[i:right+1])
                    output = output[0:i] + sub_text + output[right+1:]
                    length = len(output)
        i += 1
    output = output.replace("</span>","</font>")
    return output

# 将双换行改为大换行，首尾加入p标签
def morph_brbr_to_p(br_text: str) -> str:
    output: str = br_text
    output = output.replace("<br><br>","</p><p>")
    output = output.replace("<br>","<br>\n")
    return "<p>" + output + "</p>"

# 不全书处理流程
def morph_notallbook_chm_html(old_text: str) -> str:
    output: str = old_text
    output = morph_span_to_chm_font(output)
    output = morph_brbr_to_p(output)
    output = fix_table(output)
    output = output.replace(u"\xa0","&nbsp;")
    output = output.replace(u"\u2014","...")
    output = output.replace("•","·")
    output = output.replace("<div","<div style=\"BORDER-TOP: black 1px solid; FONT-FAMILY: 仿宋; BORDER-RIGHT: black 1px solid; WIDTH: 600px; BORDER-BOTTOM: black 1px solid; PADDING-BOTTOM: 10px; PADDING-TOP: 10px; PADDING-LEFT: 50px; MARGIN-LEFT: 50px; BORDER-LEFT: black 1px solid; PADDING-RIGHT: 50px; BACKGROUND-COLOR: #cccccc\"")
    return output