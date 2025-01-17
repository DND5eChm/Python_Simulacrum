import re

# 清除html中的所有标签并保留“有效换行”
def purge_html(content: str) -> str:
    output = content.strip().replace("\r\n","").replace("\n","")
    output = re.compile(r'<(br|/tr|/p|/h[1234]).*?>', re.S|re.IGNORECASE).sub("\n", output)
    output = re.compile(r'</td><td.*?>', re.S|re.IGNORECASE).sub("\t", output)
    output = re.compile(r'<blockquote.*?>', re.S|re.IGNORECASE).sub("\n\n", output)
    output = re.compile(r'<li.*?>', re.S|re.IGNORECASE).sub("\n· ", output)
    output = re.compile(r'<[^>]+>', re.S|re.IGNORECASE).sub("", output)
    
    #去除前后神秘空格
    output = "\n".join([line.strip() for line in output.splitlines()])
    
    return output

# 清除bbcode中的所有标签并保留“有效换行”
def purge_bbcode(content: str) -> str:
    output = content.strip()
    output = re.compile(r'\[td\]\[td\]', re.S|re.IGNORECASE).sub("\t", output)
    output = re.compile(r'\[[^\]]+\]', re.S|re.IGNORECASE).sub("", output)
    
    return output

#颜色处理：将rgb(xx,xx,xx)转化为#XXXXXX
def rgb_to_hex(rgb_str: str) -> str:
    output = rgb_str
    if rgb_str.startswith("rgb(") and rgb_str.endswith(")"):
        try:
            r, g, b = rgb_str[4:-1].split(",")
            if r.isdigit() and g.isdigit() and b.isdigit():
                r = str(hex(int(r)))[2:].upper()
                g = str(hex(int(g)))[2:].upper()
                b = str(hex(int(b)))[2:].upper()
                if len(r) == 1:
                    r = "0"+r
                elif len(r) > 2:
                    r = "FF"
                if len(g) == 1:
                    g = "0"+g
                elif len(g) > 2:
                    g = "FF"
                if len(b) == 1:
                    b = "0"+b
                elif len(b) > 2:
                    b = "FF"
                output = "#"+r+g+b
        except:
            print("[警告]尝试将 "+rgb_str+" 转化为HEX失败。")
    return output