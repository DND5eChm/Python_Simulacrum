import os
import re

from HTMLTagTraverse import htmltag, find_tag, find_tag_pair, find_tag_close_places

# 删除垃圾格式
def clean_trash_format(trash_text: str,using: str = "auto") -> str:
    output: str = trash_text
    cursor: int = 0
    # 寻找垃圾格式处理集
    trash_style_list = []
    if using == "auto":
        using = garbage_sorting(trash_text)
        if using == "":
            print("[提醒]未识别到垃圾格式，似乎没有垃圾格式？")
            return trash_text
    try:
        with open("trash_styles/"+using+".txt","r",encoding="UTF-8") as f:
            trash_style_list = [style.strip() for style in f.readlines()]
    except:
        print("[错误]无法加载垃圾格式处理集"+using+".txt")
        return trash_text
    # 处理前删除
    print("[提示]删除垃圾格式流程开始，使用处理集"+using)
    output = output.replace("\r"," ")
    output = output.replace("\n","")
    output = output.replace(": ",":")
    output = output.replace("<o:p>","")
    output = output.replace("</o:p>","")
    # 更聪明的处理方式
    while True:
        tag, left, right = find_tag(output,cursor)
        if left != -1 and right != -1:
            #print(tag.tag_name)
            tag.tag_class = ""
            new_style = []
            for style in tag.tag_style:
                if style not in trash_style_list:
                    new_style.append(style)
                    print("[提醒]找到非垃圾格式："+style)
            # 寻找无效标签并删除
            if tag.tag_name in ["span","font"] and len(new_style) == 0:
                # 没有任何style的若干标签
                c_left, c_right = find_tag_close_places(output,right+1,tag.tag_name)
                if c_left != -1 and c_right != -1:
                    output = output[0:left] + output[right+1:c_left] + output[c_right+1:]
                    cursor = left
                    continue
                else:
                    print("[错误]发现未闭合标签，垃圾格式无法处理")
                    return ""
            elif tag.tag_name in ["span","font","p","b","strong","i","em","s","del"]:
                # 没有任何内容的若干标签
                c_left, c_right = find_tag_close_places(output,right+1,tag.tag_name)
                if c_left != -1 and c_right != -1:
                    content = ""
                    if right+1 != c_left:
                        content = output[right+1:c_left]
                    if right+1 == c_left or content.strip() == "" or content.strip() == "&nbsp;":
                        output = output[0:left] + content + output[c_right+1:]
                        cursor = left
                        continue
                else:
                    print("[错误]发现未闭合标签，垃圾格式无法处理")
                    return ""

            tag.tag_style = new_style
            tag_text = tag.output()
            output = output[0:left] + tag_text + output[right+1:]
            cursor = left + len(tag_text)
            continue
        else:
            print("[提醒]垃圾格式处理完成")
            break;
    # 处理后删除
    output = re.compile(r'<(b|strong|i|em|u)></\1>', re.S|re.IGNORECASE).sub(r'\1', output)
    output = re.compile(r'\.*0+pt', re.S|re.IGNORECASE).sub('pt', output)
    # 添加一些便于观看的换行符
    output = re.compile(r'</(span|div|p|tr|table|quote)>', re.S|re.IGNORECASE).sub(r'</\1>\n', output)
    return output

# 识别垃圾格式类型
def garbage_sorting(trash_text:str) -> str:
    if "background-color: rgb(209, 234, 247)" in trash_text or "background-color: rgb(226, 244, 251)" in trash_text:
        print("[提醒]已发现垃圾格式特征：从纯美苹果园复制的内容")
        return "goddess"
    elif "mso-" in trash_text:
        print("[提醒]已发现垃圾格式特征：Word等文件")
        return "rtf"
    else:
        return ""
'''
# 删除无效span
def clean_useless_spans(span_text: str) -> str:
    def find_and_delete(output: str,length: int,start_index: int):
        j: int = start_index
        depth: int = 0
        while(j < length):
            if output[j] == "<":
                if depth == 0 and j+7 < length and output[j:j+7] == "</span>":
                    new_text: str = output[0:start_index-6] + output[start_index:j] + output[j+7:]
                    #print("已删除一项空白span")
                    return new_text
                elif j+1 < length and output[j+1] == "/":
                    depth -= 1
                elif j+2 < length and output[j+1:j+3] == "br":
                    depth += 0
                else:
                    depth += 1
            j += 1
        print("出错，遇到未闭合的span标签")
        return ""
    
    output: str = span_text
    length: int = len(output)
    i: int = 0
    while(i < length):
        if output[i] == "<":
            if i+6 < length and output[i:i+6] == "<span>":
                new_text: str = find_and_delete(output,length,i+6)
                if new_text != "":
                    output = new_text
                    length = len(output)
                    i -= 1
        i += 1
    return output
'''


