import os

from HTMLTagTraverse import find_tag, find_tag_pair

BGCOLOR = "#eeeeee"
TAB = "	"
NBSP = "&nbsp;"
SPLITER = "|"

def betterize_table(table: list[list[str]],first_line_bold: bool = True) -> str:
    table_height = len(table)
    table_width = 0
    # 查找行宽
    for row in table:
        table_width = max(len(row),table_width)
    # 补足行宽
    for i in range(table_height):
        while(len(table[i]) < table_width):
            table[i] += [""]
    # 防止空表幽灵
    if len(table) == 0 or len(table[0]) == 0:
        return""
    # 检测掷骰表，是的话等下给第一列加上居中和宽度
    left_top = table[0][0]
    roll_table = False
    first_row_width = 0
    if left_top.lower().startswith("d") and left_top[1:].isdigit():
        roll_table = True
        for i in range(table_height):
            if len(table[i][0]) > first_row_width:
                first_row_width = len(table[i][0])
    # 首行加粗
    if first_line_bold and table_height > 0:
        table[0] = [f"<strong>{block}</strong>" for block in table[0]]
    # 掷骰表居中
    if roll_table:
        for i in range(table_height):
            table[i][0] = "<p align=center>"+table[i][0]+"</p>"
    # 加上td，且偶数行上色
    for i in range(table_height):
        if i % 2 == 1: # 事实上从程序的角度来看是单数行上色
            table[i] = [f"<td bgColor={BGCOLOR}>{block}</td>" for block in table[i]]
        else:
            table[i] = [f"<td>{block}</td>" for block in table[i]]
    # 掷骰表首列宽度
    if roll_table:
        for i in range(table_height):
            table[i][0] = "<td width=" + str(first_row_width*20) + table[i][0][3:]
    # 读取模板
    template: str = ""
    with open("template/Table.htm","r",encoding="UTF-8") as f:
        template = f.read()
    # 加上tr，输出
    outputs = []
    for table_line in table:
        outputs.append("<tr>"+"\n".join(table_line)+"\n</tr>")
    print("\n".join(outputs))
    return template.replace("{{内容}}","\n".join(outputs))
    

def make_table(data: str,first_line_bold: bool = True) -> str:
    # 制作新的表格
    data_lines = data.splitlines()
    table: list[list[str]] = []
    table_width: int = 0
    table_height: int = 0
    # 拆分
    for data_line in data_lines:
        table_line = []
        if TAB in data_line:
            table_line = [block.strip() for block in data_line.split(TAB)]
        elif NBSP in data_line:
            table_line = [block.strip() for block in data_line.split(NBSP) if block.strip() != ""]
        elif SPLITER in data_line:
            table_line = [block.strip() for block in data_line.split(SPLITER) if block.strip() != ""]
        else:
            table_line = [block.strip() for block in data_line.split("  ") if block.strip() != ""]
        if len(table_line) > table_width:
            table_width = len(table_line)
        if len(table_line) > 0:
            table.append(table_line)
    if len(table) == 0 or table_width == 0:
        print("内容为空")
        return data
    else:
        return betterize_table(table,first_line_bold)
    

def fix_table(data: str,first_line_bold: bool = True) -> str:
    # 给已有表格润色
    table_cursor = 0
    output = data
    while True:
        tag, left, right, c_left, c_right = find_tag_pair(output,table_cursor,"table")
        if left != -1 and right != -1:
            table_content = output[right+1:c_left]
            tag.tag_width = "600px"
            new_table: list[list[str]] = []
            roll_table = False
            first_row_width = 5 # 先这样
            tr_count = 0
            cursor = 0
            # 遍历行
            while True:
                tr_tag, tr_left, tr_right, tr_c_left, tr_c_right = find_tag_pair(table_content,cursor,"tr")
                if tr_left != -1 and tr_right != -1 and tr_c_left != -1 and tr_c_right != -1:
                    tr_content = table_content[tr_right+1:tr_c_left].replace("\n","")
                    sub_cursor = 0
                    new_tr = []
                    # 遍历格
                    while True:
                        td_tag, td_left, td_right, td_c_left, td_c_right = find_tag_pair(tr_content,sub_cursor,"td")
                        if td_left != -1 and td_right != -1:
                            td_content = tr_content[td_right+1:td_c_left].replace("\n","")
                            new_tr.append(td_content)
                            sub_cursor = td_c_right + 1
                        else:
                            break
                    new_table.append(new_tr)
                    tr_count += 1
                    cursor = tr_c_right + 1
                else:
                    break
            
            new_table_str = "\n"+betterize_table(new_table,first_line_bold)+"\n"
            output = output[0:left]+new_table_str+output[c_right+1:]
            table_cursor = left + len(new_table_str) + 1
        else:
            break
    return output