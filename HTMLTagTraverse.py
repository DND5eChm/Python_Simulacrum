NOCONFIGTAG = ["br","hr"]
SELFCLOSEDTAG = ["img","br","hr"]


class htmltag:
    tag_name = ""
    tag_id = ""
    tag_class = ""
    tag_width = ""
    tag_height = ""
    tag_src = ""
    tag_href = ""
    tag_align = ""
    tag_bgcolor = ""
    tag_title = ""
    tag_style = []
    
    self_closed = False
    
    def __init__(self,tag_informations: str):
        if tag_informations.endswith("/"):
            self_closed = True
            tag_informations = tag_informations[0:-1]
        space = tag_informations.find(" ")
        if space != -1:
            self.tag_name = tag_informations[:space].lower()
            if self.tag_name not in NOCONFIGTAG:
                tag_informations = tag_informations[space+1:]
                self.tag_id = self.find_config("id",tag_informations)
                self.tag_class = self.find_config("class",tag_informations)
                self.tag_width = self.find_config("width",tag_informations)
                self.tag_height = self.find_config("height",tag_informations)
                if self.tag_name == "img":
                    self.tag_src = self.find_config("src",tag_informations)
                    self_closed = True
                elif self.tag_name == "a":
                    self.tag_href = self.find_config("href",tag_informations)
                elif self.tag_name == "p":
                    self.tag_align = self.find_config("align",tag_informations)
                elif self.tag_name == "td":
                    self.tag_bgcolor = self.find_config("bgColor",tag_informations)
                elif self.tag_name in ["abbr","acronym"]:
                    self.tag_title = self.find_config("title",tag_informations)
                self.tag_style = [style.strip() for style in translate_html_entity(self.find_config("style",tag_informations)).split(";") if style.strip() != ""]
            if self.tag_name in SELFCLOSEDTAG:
                self_closed = True
        else:
            self.tag_name = tag_informations

    def find_config(self,tag_name: str,tag_informations: str) -> tuple[str,str]:
        # 寻找tag的内部参数
        cursor_left = tag_informations.find(tag_name+"=")
        cursor_right = 0
        length = len(tag_name)
        if cursor_left != -1:
            if tag_informations[cursor_left+length+1] in ["'","\""]:
                cursor_right = tag_informations.find(tag_informations[cursor_left+length+1],cursor_left+length+2)
                if cursor_right != -1:
                    return tag_informations[cursor_left+length+2:cursor_right]
                else:
                    print("发现未闭合的标签")
                    return ""
            else:
                cursor_right = tag_informations.find(" ",cursor_left+length+1)
                if cursor_right == -1:
                    return tag_informations[cursor_left+length+1:cursor_right]
                else:
                    return tag_informations[cursor_left+length+1:]
        return ""
     
    def output(self) -> str:
        tag_text = self.tag_name
        if self.tag_id != "":
            tag_text += " id=\""+self.tag_id+"\""
        if self.tag_class != "":
            tag_text += " class=\""+self.tag_class+"\""
        if self.tag_width != "":
            tag_text += " width=\""+self.tag_width+"\""
        if self.tag_height != "":
            tag_text += " height=\""+self.tag_height+"\""
        if self.tag_src != "":
            tag_text += " src=\""+self.tag_src+"\""
        if self.tag_href != "":
            tag_text += " herf=\""+self.tag_href+"\""
        if self.tag_align != "":
            tag_text += " align=\""+self.tag_align+"\""
        if self.tag_bgcolor != "":
            tag_text += " bgColor=\""+self.tag_bgcolor+"\""
        if self.tag_title != "":
            tag_text += " title=\""+self.tag_title+"\""
        if len(self.tag_style) != 0:
            tag_text += " style=\""+";".join(self.tag_style).replace("\"","'")+"\""
        return "<"+tag_text+">"
     
    def output_close(self) -> str:
        return "</"+self.tag_name+">"


def find_tag_places(text: str,start_index: int):
    tag_information = ""
    cursor_left = text.find("<",start_index)
    cursor_right = text.find(">",start_index+1)
    if cursor_left != -1 and cursor_right != -1:
        return cursor_left, cursor_right
    else:
        return -1, -1

def find_tag_close_places(text: str,start_index: int,named: str):
    depth = 0
    cursor = start_index
    length = len(text) 
    while(True):
        left = text.find("<",cursor)
        right = text.find(">",cursor+1)
        if left != -1 and right != -1:
            if text[left+1] == "/":
                if depth <= 0 and text[left+2:right].lower() == named:
                    return left, right
                else:
                    depth -= 1
            else:
                if text[left+1:right].lower() not in ["br","img","img/"]:
                    depth += 1
            cursor = right+1
        else:
            return -1, -1

def find_tag(text: str,start_index: int, named: str = ""):
    cursor = start_index
    length = len(text)
    while True:
        cursor_left, cursor_right = find_tag_places(text,cursor)
        if cursor_left != -1 and cursor_right != -1 and cursor < length:
            if text[cursor_left+1] == "/":
                cursor = cursor_right + 1
                continue
            tag_information = text[cursor_left+1:cursor_right]
            if named == "" or tag_information.lower().startswith(named.lower()):
                return htmltag(tag_information), cursor_left, cursor_right
            else:
                cursor = cursor_right + 1
                continue
        else:
            return None, -1, -1

def find_tag_pair(text: str,start_index: int, named: str = ""):
    tag, cursor_left, cursor_right = find_tag(text,start_index,named)
    if cursor_left != -1 and cursor_right != -1:
        if tag.self_closed:
            close_cursor_left, close_cursor_right = cursor_right, cursor_right
        else:
            close_cursor_left, close_cursor_right = find_tag_close_places(text,cursor_right+1,tag.tag_name)
        return tag, cursor_left, cursor_right, close_cursor_left, close_cursor_right
    else:
        return None, -1, -1, -1, -1

def translate_html_entity(text: str):
    output = text.replace("&nbsp;"," ")
    output = output.replace("&lt;","<")
    output = output.replace("&gt;",">")
    output = output.replace("&amp;","&")
    output = output.replace("&quot;","\"")
    output = output.replace("&apos;","'")
    return output

UNABLEWORDS = " \\/:*?\"<>|"

def get_page_default_name(data: str):
    page_name = data
    tag_need = ""
    for tag_name in ["h1","h2","h3","h4","h5"]:
        if ("<" + tag_name) in data:
            tag_need = tag_name
            break
    while True:
        tag,left,right,c_left,c_right = find_tag_pair(page_name,0,tag_need)
        if left != -1 and right != -1 and c_left != -1 and c_right != -1:
            if tag.self_closed:
                page_name = page_name[right+1:]
            else:
                page_name = page_name[right+1:c_left]
                tag_need = ""
        else:
            break
    
    if "<" in page_name or ">" in page_name: # 说明解析失败了
        return "未命名页面"
    if len(page_name) > 30: # 太长了，说明没有标题
        return "未命名页面"
    
    page_name = page_name.replace("&nbsp;"," ")
    output = ""
    for word in page_name:
        if word in UNABLEWORDS:
            output = output + "_"
        else:
            output = output + word
    return output
    