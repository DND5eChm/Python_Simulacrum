import re

class Monster:
    def __init__(self, data):
        print("[提醒]开始处理怪物数据")
        #分割数据
        self.stats, self.contents = self.split_stat_and_content(data)
        #寻找数据
        self.title = self.find_first_line()
        self.subtitle = self.find_second_line()
        self.hp = self.find_stat_line(["生命值","hp"],"pattern")
        self.initiative = self.find_stat_line(["先攻","init","initiative"],"pattern")
        self.ac = self.find_stat_line(["护甲等级","ac"],"pattern")
        self.speed = self.find_stat_line(["速度","speed"])
        
        self.str = self.find_stat_line(["力量","str"],"attr").split("|")
        self.dex = self.find_stat_line(["敏捷","dex"],"attr").split("|")
        self.con = self.find_stat_line(["体质","con"],"attr").split("|")
        self.int = self.find_stat_line(["智力","int"],"attr").split("|")
        self.wis = self.find_stat_line(["感知","wis"],"attr").split("|")
        self.cha = self.find_stat_line(["魅力","cha"],"attr").split("|")
        
        self.skill = self.find_stat_line(["技能","skills"])
        self.save = self.find_stat_line(["豁免","saves"])
        self.vulner = self.find_stat_line(["易伤","vulnerabilities"])
        self.resistance = self.find_stat_line(["伤害抗性","抗性","damage resisitances","resistances"])
        self.damage_immune = self.find_stat_line(["伤害免疫","damage immunities"])
        self.condition_immune = self.find_stat_line(["状态免疫","condition immunities"])
        if self.damage_immune == "" and self.condition_immune == "":
            self.immune = self.find_stat_line(["免疫","immunities"])
        elif self.damage_immune == "":
            self.immune = self.condition_immune
        elif self.condition_immune == "":
            self.immune = self.damage_immune
        else:
            self.immune = self.damage_immune+"；"+self.condition_immune
        self.gears = self.find_stat_line(["装备","gears"])
        self.sense = self.find_stat_line(["感官","senses"])
        self.lang = self.find_stat_line(["语言","languages"])
        self.cr = self.find_stat_line(["挑战等级","cr","challenge"])
        
        
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
    
    #寻找第一行
    def find_first_line(self):
        for line in self.stats:
            if line.strip() != "":
                return line.strip()
    
    #寻找第二行
    def find_second_line(self):
        count = 0
        for line in self.stats:
            if line.strip() != "":
                if count == 0:
                    count = 1
                else:
                    return line.strip()
    
    #寻找数据
    def find_stat_line(self,data_prefixs:list[str],data_type:str=""):
        mustbe = []
        possible = []
        possible_low = []
        fake_words = ["，","。","（","检","减","豁"] #后面出现这些字说明不是data_line
        stack_mode = False #跨行堆叠模式
        stacks = 0
        stacked_text = ""
        
        for line in self.stats[1:]:
            if stack_mode: #属性表格的堆叠模式，多行组合来作为一行数据
                if stacks == 1 and line.isdigit(): #六维属性
                    stacks += 1
                    stacked_text += line
                    continue
                elif stacks < 4 and (line.startswith("+") or line.startswith("-")): #六维加值
                    stacks += 1
                    stacked_text += "|"+line
                    if stacks == 4: #堆叠获取完毕
                        stack_mode = False
                        possible.append(stacked_text.strip())
                    continue
                else:
                    stack_mode = False
            for prefix in data_prefixs:
                
                #处理本行是否匹配
                if len(line) < len(prefix): #长度不够，跳过
                    continue
                elif line.lower().startswith(prefix) and len(line) > len(prefix): #开头匹配，最优的情况
                    if line[len(prefix)] in [" ","："]: #完美匹配，加入肯定列表
                        mustbe.append(line[len(prefix)+1:].strip())
                        break
                    elif line[len(prefix)] not in fake_words: #不完美匹配，但不是行中文本，加入可能列表
                        possible.append(line[len(prefix):].strip())
                        break
                elif prefix in line.lower() and len(line) > len(prefix)+1: #行中匹配，不太妙的情况
                    left = line.find(prefix)
                    if left+len(prefix) < len(line):
                        if line[left+len(prefix)] in [" ","："]: #但依旧完美匹配
                            if len(line) > left+len(prefix) and line[left+len(prefix)] not in fake_words: #确认不是行中文本，加入可能列表
                                possible.append(line[left+len(prefix)+1:].strip())
                                break
                        else: #不完美匹配
                            if len(line) > left+len(prefix) and line[left+len(prefix)] not in fake_words: #确认不是行中文本，加入不太可能列表
                                possible_low.append(line[left+len(prefix):].strip())
                                break
                elif data_type == "attr": #跨行匹配，最最最最麻烦的情况
                    if prefix == line.lower():
                        stack_mode = True
                        stacks = 1
                        stacked_text = ""
                        break
        
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
                        elif "（" in thing and "）" in thing: #老版？二次检查吧
                            need_second_check = True
                        elif "+" in thing or "-" in thing: #不分割？你*没了我靠
                            if thing.count("+") + thing.count("-") == 2: #正好两次，那也基本没问题了
                                output = thing.replace("+","|+").replace("-","|-")
                                break
                            elif " " in thing:
                                right = thing.find(" ")
                                if thing[:right].count("+") + thing[:right].count("-") == 2:
                                    output = thing[:right].replace("+","|+").replace("-","|-")
                                    break
                        elif " " in thing: #用空格分割，很麻烦的情况
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
                        if "（" in thing and "）" in thing:
                            left = thing.find("（")
                            right = thing.find("）")+1
                            #检查这个括号是不是自己的
                            if thing[:left].strip().isdigit():
                                output = thing[:right]
                                break
                            elif " " in thing: #是不是把不需要的部分包裹进去了？
                                left = thing.find(" ")
                                if thing[:left].strip().isdigit():
                                    output = thing[:left].strip()
                            else: #不知道什么情况，以防万一先给过吧
                                output = thing[:right]
                        elif " " in thing: #只写了数值没打括号？
                            right = thing.find(" ")
                            if thing[:right].isdigit(): 
                                output = thing
                        elif thing.isdigit():
                                output = thing
                        elif len(thing) > 1 and (thing.startswith("+") or thing.startswith("-")) and thing[1:].isdigit():
                                output = thing
                
                # 其他常规栏
                if data_type == "":
                    output = lists[depth][0] # 选第一个
            
            # 输出不为空
            if output != "":
                # 六维括号版处理
                if data_type == "attr":
                    if "（" in thing and "）" in thing:
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
    
    # 分割数据区域与特质动作区域
    def split_stat_and_content(self,data:str):
        lines = []
        for raw_line in data.splitlines():
            line = raw_line.strip()
            if line != "":
                lines.append(line)
        #寻找分割位置
        p_split = 0
        found = False
        for line in lines:
            line_str = line.lower()
            #根据行开头判断是否是分割点
            if line_str.startswith("挑战等级") or line_str.startswith("cr") or line_str.startswith("challenge"):
                #下一行上方必是分割线
                p_split = p_split + 1
                found = True
                break
            elif line_str.startswith("特质") or line_str.startswith("动作") or line_str.startswith("附赠动作"):
                #这一行上方就是分割线
                found = True
                break
            p_split = p_split + 1
        # 没找到？怎么可能，换个方式再试一次
        if not found:
            p_split = 0
            for line in lines:
                line_str = line.lower()
                #根据特征判断是否是分割点
                if "xp" in line_str or "熟练加值" in line_str or "pb" in line_str:
                    #下一行上方可能分割线
                    p_split = p_split + 1
                    found = True
                    break
                elif "。" in line_str and len(line) >= 30: # 超过30字符，还不满足上述任何条件的情况下，只能当它是了
                    #这一行上方就是分割线
                    found = True
                    break
                p_split = p_split + 1
        
        #返回分割后的数据
        if found:
            print("                  "+lines[p_split-1])
            print("[提醒]分割位置：————————————")
            print("                  "+lines[p_split])
            return lines[:p_split],lines[p_split:]
        else:
            print("[警告]未能找到怪物数据。")
            return ["未知","未知"],[]

# 使用模板生成怪物数据块
def summon_monster(data: str,template_folder: str = "Goddess5EMonster") -> str:
    #获取模板内容
    base = ""
    contents = []
    stat_contents = []
    template_subtitle = ""
    template_statlabel = ""
    template_actionlabel = ""
    template_normallabel = ""
    template_spelllabel = ""
    template_italic = ""
    template_fixedword = ""
    template_term = ""
    template_spell = ""
    with open(f"template/{template_folder}/Base.htm", "r") as f:
        base = f.read()
    with open(f"template/{template_folder}/SubTitle.htm", "r") as f:
        template_subtitle = f.read()
    with open(f"template/{template_folder}/StatLabel.htm", "r") as f:
        template_statlabel = f.read()
    with open(f"template/{template_folder}/ActionLabel.htm", "r") as f:
        template_actionlabel = f.read()
    with open(f"template/{template_folder}/SpellLabel.htm", "r") as f:
        template_spelllabel = f.read()
    with open(f"template/{template_folder}/NormalLabel.htm", "r") as f:
        template_normallabel = f.read()
    with open(f"template/{template_folder}/Italic.htm", "r") as f:
        template_italic = f.read()
    with open(f"template/{template_folder}/FixedWord.htm", "r") as f:
        template_fixedword = f.read()
    with open(f"template/{template_folder}/Term.htm", "r") as f:
        template_term = f.read()
    with open(f"template/{template_folder}/Spell.htm", "r") as f:
        template_spell = f.read()
    
    # 识别内容
    #try:
    if 1 == 1:
        data = data.replace(" "," ").replace("&nbsp;"," ") #防止神秘小空格炸格式
        data = data.replace("(","（").replace(")","）").replace(";","；").replace(":","：").replace("5-6","5~6").replace("4-6","4~6") #半角符号转全角符号
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
            stat_contents.append(line)
        #if monster.save != "":
        #    line = template_statlabel.replace("{{名称}}","豁免").replace("{{内容}}",monster.save)
        #    stat_contents.append(line)
        if monster.vulner != "":
            line = template_statlabel.replace("{{名称}}","易伤").replace("{{内容}}",monster.vulner)
            stat_contents.append(line)
        if monster.resistance != "":
            line = template_statlabel.replace("{{名称}}","抗性").replace("{{内容}}",monster.resistance)
            stat_contents.append(line)
        if monster.immune != "":
            line = template_statlabel.replace("{{名称}}","免疫").replace("{{内容}}",monster.immune)
            stat_contents.append(line)
        if monster.gears != "":
            line = template_statlabel.replace("{{名称}}","装备").replace("{{内容}}",monster.gears)
            stat_contents.append(line)
        if monster.sense != "":
            line = template_statlabel.replace("{{名称}}","感官").replace("{{内容}}",monster.sense)
            stat_contents.append(line)
        if monster.lang != "":
            line = template_statlabel.replace("{{名称}}","语言").replace("{{内容}}",monster.lang)
            stat_contents.append(line)
        if monster.cr != "":
            line = template_statlabel.replace("{{名称}}","CR").replace("{{内容}}",monster.cr)
            stat_contents.append(line)
        
        #核心内容
        for content_line in monster.contents:
            action_name = ""
            result = ""
            
            #定型文
            if content_line.startswith("传奇动作次数") and content_line.endswith("。"):
                result = template_fixedword.replace("{{定型文}}",content_line)
                print("[提醒]发现定型文："+content_line.strip())
            else:
                #小标题
                for word in ["特质","动作","附赠动作","反应","传奇动作","神话动作"]:
                    if content_line.startswith(word):
                        result = template_subtitle.replace("{{标题}}",content_line)
                        print("[提醒]发现小标题："+content_line.strip())
                        break
                #法术上色
                for word in ["随意","任意","每项1/日","每项2/日","每项3/日","1/日","2/日","3/日"]:
                    if content_line.startswith(word+"："):
                        result = template_spelllabel.replace("{{内容}}",content_line[len(word)+1:]).replace("{{条件}}",word)
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
                        elif char == "（":
                            pattern_now = True
                        elif char  == "）":
                            pattern_now = False
                        elif not pattern_now: #不符合上述特征，即为中文字符
                            cnwords = cnwords + 1
                            if en_now:
                                sus = True #你小子先英文再中文，很可疑啊
                                en_now = False
                    
                    #动作英文里最短的Ram都有3个字,最短的中文是1个字,最长的中文都只有8个字
                    if cnwords >= 1 and cnwords <= 8 and enwords >= 3:
                        if sus: #你很可疑，我得再检查一下
                            for sus_word in ["可以","长休","短休","使用次数","目标","必须","否则","失败","成功","攻击","豁免"]:
                                if sus_word in action_name:
                                    action_name = ""
                                    result = content_line
                        #如果到现在还没处理出文本，说明完美符合动作项的结构
                        if result == "": 
                            result = content_line[right+1:]
                            print("[提醒]发现动作项："+action_name)
                    else:
                        action_name = ""
                        result = content_line
                else:
                    action_name = ""
                    result = content_line
                
                #给动作项的特殊文本词汇加斜体
                for words in [["近战或远程武器攻击","近战武器攻击","远程武器攻击"],["近战或远程法术攻击","近战法术攻击","远程法术攻击"],["近战或远程攻击检定","近战攻击检定","远程攻击检定"],["不论是否命中","命中或失手"],["命中"],["失手"],["力量豁免检定","敏捷豁免检定","体质豁免检定","智力豁免检定","感知豁免检定","魅力豁免检定","豁免检定"],["不论是否成功","失败或成功","成功或失败"],["首次失败"],["再次失败"],["失败"],["成功"],["触发"],["回应","响应"],["效果"]]:
                    for word in words: #每组仅匹配一次
                        if (word+"：") in result:
                            result = result.replace(word+"：",template_italic.replace("{{内容}}",word+"："),1)
                            break
                
                #给术语词汇变绿
                term_left,term_right = template_term.split("{{内容}}",1)
                for word in ["目盲","受擒","中毒","魅惑","失能","倒地","耳聋","束缚","力竭","麻痹","震慑","恐慌","石化","昏迷","半身掩护","四分之三掩护","全身掩护","锥状","柱状","线状","立方","光环","球状","明亮光照","微光光照","轻度遮蔽","重度遮蔽","借机攻击","撤离","躲藏","疾走","回避","D20检定"]:
                    if word in result:
                        result = result.replace(word,term_left+word+term_right)
                #几个有常见混淆的用正则表达式去匹吧
                result = re.sub(r'(?<!破)隐形(?!术)',term_left+"隐形"+term_right, result)
                result = re.sub(r'黑暗(?!(术|视))',term_left+"黑暗"+term_right, result)
                #手动法术上色
                if result.count("#") >= 2:
                    spell_left,spell_right = template_spell.split("{{内容}}",1)
                    result = re.sub(r'\#(.*?)\#',spell_left+r'\1'+spell_right, result)
            # 加入内容列表
            if action_name != "":
                contents.append(template_actionlabel.replace("{{名称}}",action_name).replace("{{内容}}",result))
            elif result != "":
                contents.append(template_normallabel.replace("{{内容}}",result))
    #except:
    #    print("[警告]识别失败，请确认你使用了正确的数据")
    
    
    return base.replace("{{可选数据}}","\n".join(stat_contents)).replace("{{内容}}","\n".join(contents))