# -*- coding: utf-8 -*-
"""
BABBDI 简体中文汉化词典（人工翻译）

左侧为游戏内英文原文的"规范化键"：全部大写、内部连续空白折叠为单个空格。
生成脚本会在游戏文件中查找匹配的原始字符串，并输出精确键，因此
此处无需精确复现原文的空格数量与大小写。

右边为简体中文译文。译文风格：贴合本作冷峻、忧郁、极简的调性。
专有名词（人名、地名）保留原文：NPC 说话人名称游戏内保持拉丁原文，
与官方社区汉化的处理方式一致。
"""

TRANSLATIONS = [

    # ============ 主菜单 ============
    ("PLAY", "开始游戏"),
    ("OIPPTION", "设置"),                 # 原文为艺术化乱序的 OPTIONS
    ("OPTECNS", "设置"),                  # 同上，另一处乱序写法
    ("PLAY", "开始游戏"),
    ("OPTIONS", "设置"),
    ("PLAME", "开始游戏"),                # 艺术化乱序的 PLAY
    ("QUUTI", "退出游戏"),                # 艺术化乱序的 QUIT
    ("BACK", "返回"),
    ("CONTROLS", "操作设置"),
    ("SOUND EFFECT", "音效"),
    ("MASTER VOLUME", "主音量"),
    ("AMBIENT SOUNDS", "环境音"),
    ("MUSIC", "音乐"),
    ("ULTRA", "极高"),
    ("LOW", "低"),
    ("MEDIUM", "中"),
    ("HIGH", "高"),
    ("LO A D G I N", "载入中"),            # 原文为乱序的 LOADING
    ("SPEEDRUN MODE", "速通模式"),
    ("SPEEDRUN MOde".upper(), "速通模式"),
    ("VERSION 1.2.4", "版本 1.2.4"),

    # ============ 主菜单提示语 ============
    ("TIP - PRESS [TAB] INGAME TO ENTER THE LIBRARY",
     "提示：游戏中按 [tab] 进入资料库"),
    ("UNPLUG GAMEPAD TO SEE KEYBOARD CONTROLS",
     "拔掉手柄即可查看键盘操作"),
    ("UNPLUG CONTROLLER TO PLAY WITH KEYBOARD",
     "拔掉手柄即可改用键盘游玩"),
    ('YOU CAN RESTART THE GAME IN THE INGAME MENU WITH "RESET SAVE" BUTTON',
     "你可以用游戏内菜单里的“重置存档”按钮重新开始游戏"),

    # ============ 游戏内 UI / 菜单 ============
    ("LIBRARY", "资料库"),
    ("LIBBARY", "资料库"),                # 原文为艺术化乱序写法
    ("RESUME", "继续游戏"),
    ("RETURN", "返回"),
    ("TO MENU", "返回主菜单"),
    ("EXIT TO MAIN MENU", "退出到主菜单"),
    ("BACK", "返回"),
    ("MAP", "地图"),
    ("CONFIRM", "确定"),
    ("CANCEL", "取消"),
    ("SAVE", "保存"),
    ("SAVE GAME", "保存游戏"),
    ("RESET RUN", "重置本轮"),
    ("RESET SAVE", "重置存档"),
    ("RETURN HOME", "返回家中"),
    ("NOT AVAILABLE", "不可用"),
    ("GAME SAVED", "游戏已保存"),
    ("YOUR PROGRESS WILL BE SAVED", "你的进度将会被保存"),
    ("YOUR LIBRARY WILL BE SAVED", "你的资料库将会被保存"),
    ("ACHIEVEMENTS", "成就"),
    ("ACHIEVEMENT UNLOCKED", "成就已解锁"),
    ("SECRET COLLECTION", "秘密收藏"),
    ("MOUSE SENSITIVITY", "鼠标灵敏度"),
    ("SMOOTH HEAD MOVEMENT", "平滑头部动作"),
    ("INVERT MOUSE X", "反转鼠标 X 轴"),
    ("INVERT MOUSE Y", "反转鼠标 Y 轴"),
    ("HEADBOD AND CAMERA TILT", "头部晃动与镜头倾斜"),   # 原文 HEADBOD 系开发者笔误
    ("DELETE ALL YOUR PROGRESS (INCLUDING ACHIEVEMENTS && SECRETS)",
     "删除你的全部进度（包括成就与秘密）"),
    ("DOING THIS WILL BRING YOU BACK TO YOUR HOME (KEEPING YOUR PROGRESS)",
     "这样做会把你送回家里（进度保留）"),

    # ============ 交互提示 ============
    ("ASK FOR TRAIN [E]", "询问火车 [e]"),
    ("OPEN DOOR [E]", "开门 [e]"),
    ("OPEN DOOR [X]", "开门 [x]"),
    ("USE ELEVATOR [E]", "使用电梯 [e]"),
    ("USE ELEVATOR [X]", "使用电梯 [x]"),
    ("GRAB [E]", "拾取 [e]"),
    ("GRAB [X]", "拾取 [x]"),
    ("TALK [E]", "交谈 [e]"),
    ("TALK [X]", "交谈 [x]"),
    ("ON/OFF [E]", "开/关 [e]"),
    ("ON/OFF [X]", "开/关 [x]"),
    ("OK", "确定"),
    ("SAVING...", "保存中…"),
    ("PRESS [TAB] TO OPEN LIBRARY", "按 [tab] 打开资料库"),
    ("PRESS 'TAB' TO OPEN LIBRARY", "按 'tab' 打开资料库"),
    ("PRESS [M] TO SEE MAP", "按 [m] 查看地图"),
    ("YOU HAVE NO TICKET", "你没有车票"),
    ("GO BACK TO SUBWAY INFORMATION CENTRE", "回到地铁信息中心"),

    # ============ 弹窗 / 提示 ============
    ("YOU FOUND A SECRET OBJECT", "你发现了一件秘密物品"),
    ("YOU FOUND THE MAP", "你找到了地图"),
    ("YOU LEFT BABBDI", "你离开了巴布迪"),

    # ============ 制作名单 ============
    ("A GAME MADE BY", "游戏制作"),
    ("ACKNOWLEDGMENTS", "鸣谢"),
    ("SPECIAL THANKS TO :", "特别鸣谢："),

    # ============ 任务 / 成就名称 ============
    ("BABBDI QUEST :", "巴布迪任务："),
    ("DOGGO FRIENDLY :", "狗狗之友："),
    ("FLAT FACE :", "平躺脸："),
    ("SOCIAL QUEST :", "社交任务："),
    ("WAY OF THE BIKER :", "摩托之路："),
    ("WAY OF THE CLIMBER :", "攀爬之路："),
    ("WAY OF THE RUSHER :", "速通之路："),
    ("WAY OF THE SEDUCER :", "撩人之道："),
    ("MELANCHOLIC DEPARTURE :", "忧郁的离别："),
    ("SECRETS MASTER :", "秘密大师："),
    ("WAY OF THE CLIMBER", "攀爬之路"),

    # ============ 任务 / 成就描述 ============
    ("CLIMB YOUR WAY THROUGH BABBDI AND REACH THE HIGHEST PEAK",
     "一路攀爬穿越巴布迪，登上最高峰"),
    ("LEAVE THE TOWN OF BABBDI.", "离开巴布迪城。"),
    ("FINISH THE GAME UNDER 4 MINUTES", "在 4 分钟内通关"),
    ("INTERACT WITH EVERYONE IN THE TOWN OF BABBDI",
     "与巴布迪城里的每一个人交谈"),
    ("IMPRESS THE GIRL NEXT TO THE CHURCH WITH THE BIKE",
     "骑摩托车让教堂旁的女孩刮目相看"),
    ("FIND A TICKET IN ORDER TO LEAVE THE TOWN OF BABBDI",
     "找到一张车票，才能离开巴布迪城"),
    ("GET ALL SECRET OBJECTS IN THE TOWN OF BABBDI",
     "集齐巴布迪城里的所有秘密物品"),
    ("GET HIT BY A TRAIN", "被火车撞到"),
    ("PLAY BALL WITH THE DOG", "和狗玩球"),

    # ============ 道具名称 ============
    ("TICKET", "车票"),
    ("MAP", "地图"),
    ("CLUB", "球棒"),
    ("MOTO", "摩托车"),
    ("STICK", "木棍"),
    ("PROPELLER", "螺旋桨"),
    ("BLOWER", "吹叶机"),
    ("SECRETFINDER", "寻尸器"),
    ("BIGBALL", "大球"),
    ("TRUMPET", "小号"),
    ("FLASHLIGHT", "手电筒"),
    ("GRABBER", "抓取爪"),

    # ============ NPC 对话（含西班牙语台词） ============
    ("YOU WANT TO LEAVE ?", "你想离开吗？"),
    ("TAKE THE TRAIN, THE STATION ISN'T FAR", "坐火车吧，车站不远"),
    ("MY DOCTOR SAID TO STAY IN THAT POSITION",
     "医生说我要一直保持这个姿势"),
    ("INTESTINAL ISSUES", "肠道有毛病"),
    ("UP THERE...", "在上面……"),
    ("I THINK HIS WIFE PASSED AWAY", "我想他妻子已经过世了"),
    ("IT WAS TOO MUCH FOR HER", "她承受不住了"),
    ("UNLESS YOU'VE GOT A TICKET.", "除非你有车票。"),
    ("TRAINS DON'T STOP", "火车不会停"),
    ("NOT EVEN IF YOU STEP ON THE TRACKS", "就算你站到铁轨上也不会"),
    ("TRY JUMPING", "试试跳下去吧"),
    ("JUMPING WON'T HURT YOU", "跳下去不会受伤的"),
    ("LEAVING BABBDI ?", "要离开巴布迪了？"),
    ("MAYBE TRAVEL AGENTS STILL SELL TICKETS", "也许旅行社还在卖票"),
    ("THE INFORMATION CENTRE IS AT THE END OF THE CANAL",
     "信息中心在运河的尽头"),
    ("SWEET SWEET SUNSHINE", "甜美的阳光"),
    ("I'M LYING FLAT", "我正平躺着"),
    ("NO SÉ CUANDO PODRÉ VOLVER A MI CASA PERO POR EL MOMENTO ME GUSTA BABBDI.",
     "我不知道什么时候才能回家，不过眼下我喜欢巴布迪。"),
    ("ES MUY ESPECIAL.", "它很特别。"),
    ("ERES LOCO ?", "你疯了吗？"),
    ("ME GUSTA LA MUSICA.", "我喜欢音乐。"),
    ("MI PADRE MURIÓ...", "我父亲去世了……"),
    ("JOSÉ PADILLAS...", "何塞·帕迪利亚斯……"),
    ("GAMBA Y LA PEQUEÑA DE MI CASA ESTAMOS EN VACACIONES AQUI EN BABBDI.",
     "甘巴和我家小丫头，我们正在巴布迪这里度假。"),
    ("HER BODY DECAYED SO QUICKLY", "她的身体腐烂得太快了"),
    ("NO NEED FOR THIS ANYMORE, TAKE IT", "这个我已经用不上了，拿去吧"),
    ("WE WILL GET OUT OF BABBDI", "我们会离开巴布迪的"),
    ("I HAVE TRAIN TICKETS", "我有火车票"),
    ("SEWERS OIL", "下水道的油"),
    ("GET OUT OF MY SIGHT.", "滚出我的视线。"),
    ("HE HAS TICKETS TO LEAVE BABBDI", "他有离开巴布迪的车票"),
    ("LUCKY HIM", "他可真走运"),
    ("THEY DON'T SELL TICKETS ANYMORE", "他们不再卖票了"),
    ("REMEMBER THAT SICK WOMAN'", "还记得那个生病的女人吧"),
    ("SHE DIED, MAYBE YOU CAN HAVE HER TICKET",
     "她死了，也许你可以拿她的票"),
    ("TAKE THIS DEVICE AND RIGHT CLICK TO FIND HER CORPSE",
     "拿上这个装置，右键点击就能找到她的尸体"),
    ("HIS WIFE IS SICK", "他妻子病了"),
    ("HE NEEDS TO REACH THE CITY", "他得进城去"),
    ("BY TRAIN", "坐火车"),
    ("YOU CAN BUY THOSE AT THE END OF THE CANAL, IN THE INFORMATION CENTRE",
     "你可以在运河尽头的信息中心买到"),
    ("THIS IS A GREAT FOOD PLACE", "这里的饭菜很不错"),
    ("THE ONLY WAY OF LEAVING BABBDI...", "离开巴布迪的唯一办法……"),
    ("REQUIRES A TRAIN TICKET", "需要一张火车票"),
    ("THAT WAS IMPRESSIVE", "真厉害"),
    ("I'M SO BORED", "我好无聊"),
    ("MAKE MY HEAD SPIN", "让我头晕目眩"),
    ("TAKE MY CLUB", "拿走我的球棒吧"),
    ("JUST GRAB IT AND HIT SURFACES WITH IT", "捡起来敲打各种东西就行"),
    ("MAYBE WE SEE EACH OTHER AGAIN", "也许我们还会再见"),
    ("BYE", "再见"),
    ("ONE STEP AT A TIME", "一步一步来"),
    ("I CAN MAKE IT HOME", "我能回到家"),
    ("THIS WAS MY FAVORITE MUSIC WHEN I WAS A CHILD.",
     "这是我小时候最喜欢的音乐。"),
    ("WE HAD SUCH A GREAT TIME WITH YOUR MOTHER",
     "我们和你母亲度过了一段非常美好的时光"),
    ("I REMEMBER WHEN YOU WERE JUST A CHILD", "我还记得你小时候的样子"),
    ("WE DON'T ISSUE THESE ANYMORE.", "我们已经不发这种票了。"),
    ("NO MORE TICKETS.", "没有票了。"),
]

# 需要额外补充的、无法通过规范化匹配得到的短文本（纯符号）
EXTRA = [
    ("...", "……"),
]

# ---------------------------------------------------------------------------
# 以"正则"形式给出的条目
#
# 背景：XUnity 的 GeneratePartialTranslations（用于支持对话的逐字打字机效果）
# 会为精确键的每一个前缀生成"部分译文"。因此若某条精确键是另一段游戏文本的
# 延长，那段短文本就会被误伤。
#
# 实例：精确键 "BABBDI QUEST    :" 会让主菜单背景上的大标题 "BABBDI"
# 被当作它的前缀，翻译成"巴布"。改成正则后即可避免。
# 正则条目只在精确匹配失败后才生效。
# ---------------------------------------------------------------------------
REGEX_ENTRIES = [
    (r'^BABBDI QUEST\s*:$', '巴布迪任务：'),
]

# 上面那些改用正则表达的条目，不再生成精确键（按规范化形式匹配排除）
EXCLUDE_EXACT = [
    'BABBDI QUEST    :',
]

