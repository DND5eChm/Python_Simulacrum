
class Monster:
    def __init__(self, content):
        print("[提醒]开始处理怪物数据")
        #寻找数据
        content_lines = content.splitlines()
        self.title = self.find_first_line(content_lines)
        self.subtitle = self.find_second_line(content_lines)
        self.hp = self.find_data_line(content_lines,["生命值","hp"],"pattern")
        self.initiative = self.find_data_line(content_lines,["先攻","init","initiative"],"pattern")
        self.ac = self.find_data_line(content_lines,["护甲等级","ac"],"pattern")
        self.speed = self.find_data_line(content_lines,["速度","speed"])
        
        self.str = self.find_data_line(content_lines,["力量","str"],"attr").split("|")
        self.dex = self.find_data_line(content_lines,["敏捷","dex"],"attr").split("|")
        self.con = self.find_data_line(content_lines,["体质","con"],"attr").split("|")
        self.int = self.find_data_line(content_lines,["智力","int"],"attr").split("|")
        self.wis = self.find_data_line(content_lines,["感知","wis"],"attr").split("|")
        self.cha = self.find_data_line(content_lines,["魅力","cha"],"attr").split("|")
        
        self.skill = self.find_data_line(content_lines,["技能","skill"])
        self.save = self.find_data_line(content_lines,["豁免","save"])
        self.resistance = self.find_data_line(content_lines,["伤害抗性","抗性","damage resisitance","resistance"])
        self.damage_immune = self.find_data_line(content_lines,["伤害免疫","damage immune"])
        self.condition_immune = self.find_data_line(content_lines,["状态免疫","condition immune"])
        if self.damage_immune == "" and self.condition_immune == "":
            self.immune = self.find_data_line(content_lines,["免疫","immune"])
        elif self.damage_immune == "":
            self.immune = self.condition_immune
        elif self.condition_immune == "":
            self.immune = self.damage_immune
        else:
            self.immune = self.damage_immune+"；"+self.condition_immune
        self.gears = self.find_data_line(content_lines,["装备","gears"])
        self.sense = self.find_data_line(content_lines,["感官","sense"])
        self.lang = self.find_data_line(content_lines,["语言","language"])
        self.cr = self.find_data_line(content_lines,["挑战等级","cr","challenge"])
        self.contents = self.find_rest(content_lines)
        
        #处理旧版豁免
        if self.save != "":
            six_saves = self.save.replace("，","|").replace(",","|").replace("、","|").split("|")
            for six_save in six_saves:
                six_save = six_save.lower().strip()
                if six_save.startswith("力量") or six_save.startswith("str"):
                    self.str[2] = six_save[2:].strip()
                    print("[提醒]找到怪物数据 力量豁免=\""+self.str[2]+"\"")
                elif six_save.startswith("敏捷") or six_save.startswith("dex"):
                    self.dex[2] = six_save[2:].strip()
                    print("[提醒]找到怪物数据 敏捷豁免=\""+self.dex[2]+"\"")
                elif six_save.startswith("体质") or six_save.startswith("con"):
                    self.con[2] = six_save[2:].strip()
                    print("[提醒]找到怪物数据 体质豁免=\""+self.con[2]+"\"")
                elif six_save.startswith("智力") or six_save.startswith("int"):
                    self.int[2] = six_save[2:].strip()
                    print("[提醒]找到怪物数据 智力豁免=\""+self.int[2]+"\"")
                elif six_save.startswith("感知") or six_save.startswith("wis"):
                    self.wis[2] = six_save[2:].strip()
                    print("[提醒]找到怪物数据 感知豁免=\""+self.wis[2]+"\"")
                elif six_save.startswith("魅力") or six_save.startswith("cha"):
                    self.cha[2] = six_save[2:].strip()
                    print("[提醒]找到怪物数据 魅力豁免=\""+self.cha[2]+"\"")
        
        #优化一下一些空白位置的外观
        if self.str[2] == "":
            self.str[2] = self.str[1]
        if self.dex[2] == "":
            self.dex[2] = self.dex[1]
        if self.con[2] == "":
            self.con[2] = self.con[1]
        if self.int[2] == "":
            self.int[2] = self.int[1]
        if self.wis[2] == "":
            self.wis[2] = self.wis[1]
        if self.cha[2] == "":
            self.cha[2] = self.cha[1]
        
        if self.initiative == "":
            init_var = 10
            dex_mod = self.dex[1]
            if dex_mod.startswith("+") and dex_mod[1:].isdigit():
                init_var = init_var + int(dex_mod[1:])
            elif dex_mod.startswith("-") and dex_mod[1:].isdigit():
                init_var = init_var - int(dex_mod[1:])
            elif dex_mod.isdigit():
                init_var = init_var + int(dex_mod)
            self.initiative = self.dex[1]+"（"+str(init_var)+"）"
    
    def find_first_line(self,content_lines):
        for line in content_lines:
            if line.strip() != "":
                return line.strip()
                
    def find_second_line(self,content_lines):
        count = 0
        for line in content_lines:
            if line.strip() != "":
                if count == 0:
                    count = 1
                else:
                    return line.strip()
                    
    def find_data_line(self,content_lines:list[str],data_prefixs:list[str],data_type:str=""):
        #print("[提醒]开始寻找"+data_prefixs[0])
        mustbe = []
        possible = []
        possible_low = []
        fake_words = ["，","（","(","或","检","减","豁"] #后面出现这些字说明不是data_line
        for line in content_lines:
            for prefix in data_prefixs:
                if line.lower().startswith(prefix): #开头匹配，最优的情况
                    if line[len(prefix)] in [" ",":","："]: #完美匹配，加入肯定列表
                        mustbe.append(line[len(prefix)+1:].strip())
                    elif line[len(prefix)] not in fake_words: #不完美匹配，但不是行中文本，加入可能列表
                        possible.append(line[len(prefix):].strip())
                elif prefix in line.lower(): #行中匹配，不太妙的情况
                    left = line.find(prefix)
                    if line[left+len(prefix)] in [" ",":","："]: #但依旧完美匹配
                        if len(line) > left+len(prefix) and line[left+len(prefix)] not in fake_words: #确认不是行中文本，加入可能列表
                            possible.append(line[left+len(prefix)+1:].strip())
                    else: #不完美匹配
                        if len(line) > left+len(prefix) and line[left+len(prefix)] not in fake_words: #确认不是行中文本，加入不太可能列表
                            possible_low.append(line[left+len(prefix):].strip())
        
        #根据类型，循环尝试判断是否可能
        output = ""
        lists = [mustbe,possible,possible_low]
        depth = 0
        while(depth <= 2):
            if len(lists[depth]) > 0:
                need_second_check = False
                # 六维数据
                if data_type == "attr":
                    for thing in lists[depth]:
                        if "|" in thing: #老老实实用|分割了
                            if thing.count("|") == 2: #正好两次，那基本没问题了
                                output = thing
                                break
                            elif " " in thing:
                                right = thing.find(" ")
                                if thing[:right].count("|") == 2:
                                    output = thing[:right]
                                    break
                        elif "\t" in thing: #用tab分割...也行？
                            if thing.count("\t") == 2: #正好两次，那也基本没问题了
                                output = thing.replace("\t","|")
                                break
                            elif " " in thing:
                                right = thing.find(" ")
                                if thing[:right].count("\t") == 2:
                                    output = thing[:right].replace("\t","|")
                                    break
                        elif "(" in thing and ")" in thing or "（" in thing and "）" in thing:
                            need_second_check = True
                        elif " " in thing: #没有括号还用空格分割，很麻烦的情况
                            if thing.count(" ") == 2: #正好两次，没...没问题吗？
                                output = thing.replace(" ","|")
                                break
                            elif thing.count(" ") > 2: # 超过两次...这对么？
                                right = thing.find(" ")+1
                                right = thing.find(" ",right)+1
                                right = thing.find(" ",right)+1
                                output = thing[:right].replace(" ","|")
                                break

                # 有括号的一众
                if need_second_check or data_type == "pattern":
                    for thing in lists[depth]:
                        if "(" in thing and ")" in thing:
                            right = thing.find(")")+1
                            output = thing[:right]
                            break
                        elif "（" in thing and "）" in thing:
                            right = thing.find("）")+1
                            output = thing[:right]
                            break
                        elif " " in thing: #只写了数值没打括号？
                            right = thing.find(" ")
                            if thing[:right].isdigit(): 
                                output = thing
                        elif thing.isdigit(): #只写了数值没打括号？
                                output = thing
                
                # 其他常规栏
                if data_type == "":
                    output = lists[depth][0] # 选第一个
            
            # 输出不为空
            if output != "":
                # 六维括号版处理
                if data_type == "attr":
                    if "(" in output and ")" in output:
                        left = thing.find("(")
                        right = thing.find(")")
                        output = output[:left]+"|"+output[left+1:right]+"|"
                    elif "（" in thing and "）" in thing:
                        left = thing.find("（")
                        right = thing.find("）")
                        output = output[:left]+"|"+output[left+1:right]+"|"
                print("[提醒]找到怪物数据 "+data_prefixs[0]+"=\""+output+"\"")
                return output
            depth = depth + 1
        #没找到
        if data_type == "attr":
            return "10|+0|+0"
        return ""
    
    def find_rest(self,content_lines:list[str]):
        #print("[提醒]开始寻找剩余数据")
        top = 0
        found = False
        for line in content_lines:
            line_str = line.strip().lower()
            if line_str.startswith("挑战等级") or line_str.startswith("cr") or line_str.startswith("challenge"):
                top = top + 1
                break
            if line_str.startswith("特质") or line_str.startswith("动作") or line_str.startswith("附赠动作"):
                break
            top = top + 1
        if len(content_lines) > top:
            if content_lines[top].strip() == "": # 如果空了一大行那必定是了
                found = True
                if len(content_lines) > top+1:
                    top = top+1 #略过这行
            elif content_lines[top].startswith("特性") or content_lines[top+1].startswith("特质"): # 特性/特质打头？那你也是了
                found = True
            elif content_lines[top].startswith("动作") or content_lines[top+1].startswith("附赠动作"): # 动作/附赠动作打头？那你也是了
                found = True
        else:
            return []
        
        if found:
            outputs = []
            print("[提醒]找到怪物余下数据：")
            for line in content_lines[top:]:
                if line.strip() != "":
                    print("    "+line)
                    outputs.append(line.strip())
            return outputs
        return []

# 使用模板生成怪物数据块
def summon_monster(data: str,template_folder: str = "Goddess5EMonster") -> str:
    #获取模板内容
    base = ""
    contents = []
    template_subtitle = ""
    template_statlabel = ""
    template_actionlabel = ""
    template_italic = ""
    template_spell = ""
    with open(f"template/{template_folder}/Base.htm", "r") as f:
        base = f.read()
    with open(f"template/{template_folder}/SubTitle.htm", "r") as f:
        template_subtitle = f.read()
    with open(f"template/{template_folder}/StatLabel.htm", "r") as f:
        template_statlabel = f.read()
    with open(f"template/{template_folder}/ActionLabel.htm", "r") as f:
        template_actionlabel = f.read()
    with open(f"template/{template_folder}/Italic.htm", "r") as f:
        template_italic = f.read()
    with open(f"template/{template_folder}/Spell.htm", "r") as f:
        template_spell = f.read()
    
    # 识别内容
    #try:
    if 1 == 1:
        monster = Monster(data)
        
        #将内容塞入Base模板
        base = base.replace("{{名称}}",monster.title).replace("{{副栏}}",monster.subtitle).replace("{{护甲等级}}",monster.ac).replace("{{先攻}}",monster.initiative).replace("{{护甲等级}}",monster.ac).replace("{{生命值}}",monster.hp).replace("{{速度}}",monster.speed)
        base = base.replace("{{力量}}",monster.str[0]).replace("{{力量调整}}",monster.str[1]).replace("{{力量豁免}}",monster.str[2])
        base = base.replace("{{敏捷}}",monster.dex[0]).replace("{{敏捷调整}}",monster.dex[1]).replace("{{敏捷豁免}}",monster.dex[2])
        base = base.replace("{{体质}}",monster.con[0]).replace("{{体质调整}}",monster.con[1]).replace("{{体质豁免}}",monster.con[2])
        base = base.replace("{{智力}}",monster.int[0]).replace("{{智力调整}}",monster.int[1]).replace("{{智力豁免}}",monster.int[2])
        base = base.replace("{{感知}}",monster.wis[0]).replace("{{感知调整}}",monster.wis[1]).replace("{{感知豁免}}",monster.wis[2])
        base = base.replace("{{魅力}}",monster.cha[0]).replace("{{魅力调整}}",monster.cha[1]).replace("{{魅力豁免}}",monster.cha[2])
        
        #剩下的数据栏
        if monster.skill != "":
            line = template_statlabel.replace("{{名称}}","技能").replace("{{内容}}",monster.skill)
            contents.append(line)
        #if monster.save != "":
        #    line = template_statlabel.replace("{{名称}}","豁免").replace("{{内容}}",monster.save)
        #    contents.append(line)
        if monster.resistance != "":
            line = template_statlabel.replace("{{名称}}","抗性").replace("{{内容}}",monster.resistance)
            contents.append(line)
        if monster.immune != "":
            line = template_statlabel.replace("{{名称}}","免疫").replace("{{内容}}",monster.immune)
            contents.append(line)
        if monster.gears != "":
            line = template_statlabel.replace("{{名称}}","装备").replace("{{内容}}",monster.gears)
            contents.append(line)
        if monster.sense != "":
            line = template_statlabel.replace("{{名称}}","感官").replace("{{内容}}",monster.sense)
            contents.append(line)
        if monster.lang != "":
            line = template_statlabel.replace("{{名称}}","语言").replace("{{内容}}",monster.lang)
            contents.append(line)
        if monster.cr != "":
            line = template_statlabel.replace("{{名称}}","CR").replace("{{内容}}",monster.cr)
            contents.append(line)
        
        #空一行
        contents.append("")
        
        for content_line in monster.contents:
            result = ""
            for word in ["特质","动作","附赠动作","反应","传奇动作","神话动作"]:
                if content_line.startswith(word):
                    result = template_subtitle.replace("{{标题}}",content_line)
                    print("[提醒]发现小标题："+content_line.strip())
                    break
            for word in ["随意","任意","每项1/日","每项2/日","每项3/日","1/日","2/日","3/日"]:
                if content_line.startswith(word+":") or content_line.startswith(word+"："):
                    result = template_spell.replace("{{内容}}",content_line[len(word)+1:]).replace("{{条件}}",word)
                    print("[提醒]发现法术行："+content_line.strip())
                    break
            if result == "":
                if "。" in content_line:
                    right = content_line.find("。")
                    action_name = content_line[:right]
                    #逐字看看是不是标准的“动作Action”格式
                    enwords = 0
                    cnwords = 0
                    en_now = False
                    pattern_now = False
                    sus = False
                    for char in action_name:
                        if (not pattern_now) and (char.isdigit() or char == " " or char.encode().isalpha()):
                            en_now = True
                            enwords = enwords + 1
                        elif char in ["(","（"]:
                            pattern_now = True
                        elif char in [")","）"]:
                            pattern_now = False
                        else: #不符合上述特征，即为中文字符
                            cnwords = cnwords + 1
                            if not pattern_now and en_now:
                                sus = True #你小子先英文再中文，很可疑啊
                                en_now = False
                    if cnwords >= 1 and cnwords <= 8 and enwords >= 3:#动作英文里最短的Ram都有3个字,最短的中文是1个字,最长的中文都只有8个字
                        if sus: #你很可疑，我得再检查一下
                            for sus_word in ["可以","长休","短休","使用次数","目标","必须","否则","失败","成功","攻击","豁免"]:
                                if sus_word in action_name:
                                    result = content_line
                        if result == "": #诶你小子真的这个神经病结构啊
                            action_content = content_line[right+1:]
                            for words in [["近战或远程武器攻击","近战武器攻击","远程武器攻击"],["近战或远程法术攻击","近战法术攻击","远程法术攻击"],["近战或远程攻击检定","近战攻击检定","远程攻击检定"],["不论是否命中","命中或失手"],["命中"],["失手"],["力量豁免检定","敏捷豁免检定","体质豁免检定","智力豁免检定","感知豁免检定","魅力豁免检定","豁免检定"],["不论是否成功","成功或失败"],["失败"],["成功"]]:
                                for word in words: #每组仅匹配一次
                                    if (word+":") in action_content:
                                        action_content = action_content.replace(word+":",template_italic.replace("{{内容}}",word+"："),1)
                                        break
                                    elif (word+"：") in action_content:
                                        action_content = action_content.replace(word+"：",template_italic.replace("{{内容}}",word+"："),1)
                                        break
                            result = template_actionlabel.replace("{{名称}}",action_name).replace("{{内容}}",action_content)
                            print("[提醒]发现动作项："+action_name)
                    else:
                        result = content_line        
                else:
                    result = content_line
            # 加入内容列表
            if result != "":
                contents.append(result)
    #except:
    #    print("[警告]识别失败，请确认你使用了正确的数据")
    
    
    return base.replace("{{内容}}","\n".join(contents))