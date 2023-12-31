
from HTMLTagTraverse import htmltag, find_tag_pair, translate_html_entity

SAMEWORDS: dict[str, str] = {
    "strong" : "b",
    "em" : "i",
    "del" : "s",
    "div" : "quote",
    "blockquote" : "quote"
}

# 将html文本转换为bbcode文本
def morph_html_to_bbcode(html_text: str) -> str:
    output: str = html_text
    cursor: int = 0
    output = output.replace("\r","")
    output = output.replace("\n"," ")
    output = output.replace("<br>","\n")
    output = output.replace("!important","")
    while(True):
        tag, start_left, start_right, end_left, end_right = find_tag_pair(output,cursor)
        if start_left != -1 and start_right != -1 and end_left != -1 and end_right != -1:
            print("——"+output[start_left:start_right+1]+"  "+output[end_left:end_right+1])
            tag.tag_class = ""
            bbcode_start = ""
            bbcode_content = output[start_right+1:end_left]
            bbcode_end = ""
            if tag.tag_name == "img":
                bbcode_start = bbcode_start + "[img]"
                bbcode_content = tag.tag_src
                bbcode_end = "[/img]" + bbcode_end
            else:
                if tag.tag_name in SAMEWORDS.keys():
                    tag.tag_name = SAMEWORDS[tag.tag_name]
                if tag.tag_name in ["quote","b","i","s","table","tr","td","sup","sub","tt","list","li"]:
                    bbcode_start = bbcode_start + f"[{tag.tag_name}]"
                    bbcode_end = f"[/{tag.tag_name}]" + bbcode_end
                elif tag.tag_name == "p":
                    bbcode_end = bbcode_end + "\n"
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
                        style_name = style_name.strip()
                        style_config = style_config.strip()
                        if style_name == "color":
                            bbcode_start = bbcode_start + "[color="+style_config+"]"
                            bbcode_end = "[/color]" + bbcode_end
                        elif style_name in ["font-size","mso-bidi-font-size"]:
                            try:
                                if style_config.endswtih("pt"):
                                    style_config = str(int(float(style_config[:-2])))+"pt"
                                elif style_config.endswtih("px"):
                                    style_config = str(int(float(style_config[:-2])))+"px"
                                else:
                                    style_config = str(int(float(style_config)))
                            except:
                                style_config = style_config.replace(".0000","")
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
            #print(bbcode_start+bbcode_content+bbcode_end)
            cursor = start_left
        else:
            break
    return translate_html_entity(output)