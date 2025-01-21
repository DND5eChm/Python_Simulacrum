from module.HTMLTagTraverse import htmltag, find_tag_pair, translate_html_entity
from module.Tools import rgb_to_hex
import re

SAMEWORDS: dict[str, str] = {
    "strong" : "b",
    "em" : "i",
    "del" : "s",
    "div" : "quote",
    "blockquote" : "quote"
}

DEFAULTFONTSIZE = {
        "px" : 13,
        "pt" : 10
}

# 将html文本转换为bbcode文本
def morph_html_to_bbcode(html_text: str) -> str:
    output: str = html_text
    cursor: int = 0
    output = output.replace("\r","")
    output = output.replace("\n","")
    output = output.replace("<br>","\n")
    output = output.replace("!important","")
    
    font_sizes_in_page = {}
    base_font_size = {} #单位为px或1/2pt
    #获取基准字体大小
    matcher = re.compile(r"(?<=font-size:)[0-9\.]*(px|pt)", re.S|re.IGNORECASE)
    for match in matcher.finditer(output):
        text = match.group()
        text = str(float(text[:-2]))+text[-2:]
        if text not in font_sizes_in_page.keys():
            font_sizes_in_page[text] = 1
        else:
            font_sizes_in_page[text] = font_sizes_in_page[text] + 1
    if len(font_sizes_in_page) > 0:
        max_appears = max(font_sizes_in_page.values())
        for font_size,appears in font_sizes_in_page.items():
            if appears == max_appears:
                if font_size.endswith("pt"):
                    base_font_size["pt"] = float(font_size[:-2])
                    base_font_size["px"] = base_font_size["pt"] * 0.75
                else: #if font_size.endswith("px"):
                    base_font_size["px"] = float(font_size[:-2])
                    base_font_size["pt"] = base_font_size["px"] * 1.3333
                break
    else:
        base_font_size["px"] = DEFAULTFONTSIZE["px"]
        base_font_size["pt"] = DEFAULTFONTSIZE["pt"]
        
    #开始处理
    while(True):
        tag, start_left, start_right, end_left, end_right = find_tag_pair(output,cursor)
        if start_left != -1 and start_right != -1 and end_left != -1 and end_right != -1:
            #print("——"+output[start_left:start_right+1]+"  "+output[end_left:end_right+1])
            tag.tag_class = ""
            bbcode_start = ""
            bbcode_content = output[start_right+1:end_left].strip()
            bbcode_end = ""
            if tag.tag_name == "img":
                bbcode_start = bbcode_start + "[img]"
                bbcode_content = tag.tag_src
                bbcode_end = "[/img]" + bbcode_end
            else:
                if tag.tag_name in SAMEWORDS.keys():
                    tag.tag_name = SAMEWORDS[tag.tag_name]
                if tag.tag_name in ["b","i","s","sup","sub","tt"]: #无内容则删除
                    if bbcode_content.strip() == "": #空白内容则不做code
                        bbcode_start = ""
                        bbcode_content = bbcode_content
                        bbcode_end = ""
                    else:
                        bbcode_start = bbcode_start + f"[{tag.tag_name}]"
                        bbcode_end = f"[/{tag.tag_name}]" + bbcode_end
                elif tag.tag_name in ["td"]: #去换行
                    bbcode_start = bbcode_start + f"[{tag.tag_name}]"
                    bbcode_end = f"[/{tag.tag_name}]" + bbcode_end
                    bbcode_content = bbcode_content.strip()
                elif tag.tag_name in ["quote","table","list"]: #首尾换行
                    bbcode_start = bbcode_start + f"[{tag.tag_name}]\n"
                    bbcode_end = f"[/{tag.tag_name}]\n" + bbcode_end
                elif tag.tag_name in ["tr","li"]: #末尾换行
                    bbcode_start = bbcode_start + f"[{tag.tag_name}]"
                    bbcode_end = f"[/{tag.tag_name}]\n" + bbcode_end
                elif tag.tag_name in ["h1","h2","h3","h4","h5","h6"]:
                    bbcode_end = "\n" + bbcode_end
                elif tag.tag_name == "p":
                    bbcode_end = "\n" + bbcode_end
                elif tag.tag_align != "":
                    bbcode_start = bbcode_start + f"[{tag.tag_align}]"
                    bbcode_end = f"[/{tag.tag_align}]" + bbcode_end
                elif tag.tag_href != "":
                    bbcode_start = bbcode_start + f"[url={tag.tag_href}]"
                    bbcode_end = "[/url]" + bbcode_end
                elif tag.tag_name in ["abbr","acronym"] and tag.tag_title != "":
                    bbcode_start = bbcode_start + f"[{tag.tag_name}={tag.tag_title}]"
                    bbcode_end = f"[/{tag.tag_name}]" + bbcode_end
                
                for style in tag.tag_style:
                    if ":" in style:
                        style_name, style_config = style.split(":")
                        style_name = style_name.strip().lower()
                        style_config = style_config.strip().lower()
                        if style_name == "color":
                            if style_config.startswith("rgb("):
                                style_config = rgb_to_hex(style_config)
                                if style_config != "#000000": # 黑色忽略
                                    bbcode_start = bbcode_start + "[color="+style_config+"]"
                                    bbcode_end = "[/color]" + bbcode_end
                            else:
                                bbcode_start = bbcode_start + "[color="+style_config+"]"
                                bbcode_end = "[/color]" + bbcode_end
                        elif style_name in ["font-size","mso-bidi-font-size"]:
                            for unit in ["pt","px"]:
                                if style_config.endswith(unit):
                                    size_str = style_config[:-len(unit)]
                                    size = float(size_str) / base_font_size[unit] * DEFAULTFONTSIZE[unit]
                                    if int(size) != DEFAULTFONTSIZE[unit]:
                                        style_config = str(int(size))+unit
                                        bbcode_start = bbcode_start + f"[size={style_config}]"
                                        bbcode_end = "[/size]" + bbcode_end
                        elif style_name == "text-decoration":
                            if style_config == "underline":
                                bbcode_start = bbcode_start + "[u]"
                                bbcode_end = "[/u]" + bbcode_end
                        elif style_name == "list-style-type":
                            if style_config == "disc":
                                bbcode_start.replace("[li]","[*]")
                                bbcode_end.replace("[/li]","[*]")
                            elif style_config == "circle":
                                bbcode_start.replace("[li]","[o]")
                                bbcode_end.replace("[/li]","[o]")
                            elif style_config == "square":
                                bbcode_start.replace("[li]","[x]")
                                bbcode_end.replace("[/li]","[x]")
                            
            
            output = output[0:start_left]+bbcode_start+bbcode_content+bbcode_end+output[end_right+1:]
            print("[Start]"+bbcode_start)
            print("[Content]"+bbcode_content)
            print("[End]"+bbcode_end)
            cursor = start_left
        else:
            print("[提醒]全部html标签已处理完毕")
            break
        
        #特殊处理，防止表格乱换行现象
        output = output.replace("\n[/td]","[/td]")
    return translate_html_entity(output)