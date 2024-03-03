import os
import re

from HTMLTagTraverse import htmltag, find_tag, find_tag_pair, find_tag_close_places

# 删除果园的垃圾格式
def clean_trash_format(trash_text: str,using: str) -> str:
    output: str = trash_text
    cursor: int = 0
    # 寻找垃圾格式处理集
    trash_style_list = []
    with open("trash_styles/"+using+".txt","r",encoding="UTF-8") as f:
        trash_style_list = [style.strip() for style in f.readlines()]
    # 处理前删除
    output = output.replace("\r"," ")
    output = output.replace("\n","")
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
                    print("找到非垃圾style："+style)
            # 寻找无效标签并删除
            if tag.tag_name in ["span","font"] and len(new_style) == 0:
                # 没有任何style的若干标签
                c_left, c_right = find_tag_close_places(output,right+1,tag.tag_name)
                if c_left != -1 and c_right != -1:
                    output = output[0:left] + output[right+1:c_left] + output[c_right+1:]
                    cursor = left
                    continue
                else:
                    print("未闭合，无法处理")
                    return ""
            elif tag.tag_name in ["span","font","p","b","strong","i","em","s","del"]:
                # 没有任何内容的若干标签
                c_left, c_right = find_tag_close_places(output,right+1,tag.tag_name)
                if c_left != -1 and c_right != -1:
                    content = ""
                    if right+1 != c_left:
                        content = output[right+1:c_left]
                        print(content)
                    #print(str([left,right,c_left,c_right]))
                    if right+1 == c_left or content.strip() == "" or content.strip() == "&nbsp;":
                        output = output[0:left] + content + output[c_right+1:]
                        cursor = left
                        continue
                else:
                    print("未闭合，无法处理")
                    return ""

            tag.tag_style = new_style
            tag_text = tag.output()
            output = output[0:left] + tag_text + output[right+1:]
            cursor = left + len(tag_text)
            continue
        else:
            print("处理完成")
            break;
    # 处理后删除
    output = output.replace("</b><b>","")
    output = output.replace("</strong><strong>","")
    output = output.replace("</i><i>","")
    output = output.replace("</em><em>","")
    return output
    
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


