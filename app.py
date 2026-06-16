#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Web Application - 个人信息管理平台
功能模块: 资讯管理、项目库、成长记录、求职导航、学习资料
"""

# ==============================================================================
# 【1】导入依赖
# ==============================================================================
from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import uuid

# ==============================================================================
# 【2】应用初始化配置
# ==============================================================================
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==============================================================================
# 【3】资讯管理模块 (news)
# ==============================================================================
NEWS_FILE = 'news_data.json'

def load_news():
    """加载资讯数据"""
    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "sports_nba": [],
        "sports_football": [],
        "tech_ai": [],
        "tech_products": [],
        "world_news": [],
        "last_updated": None
    }

def save_news(data):
    """保存资讯数据"""
    data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(NEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_default_news():
    """初始化默认资讯数据（2026年6月12日）"""
    news = load_news()
    if not news.get('last_updated'):
        news = {
            "sports_nba": [
                {"title": "库里砍下35分，勇士险胜湖人总分2-1", "source": "虎扑", "time": "2026-06-12", "hot": True},
                {"title": "2025-26赛季NBA总决赛：勇士vs凯尔特人G3", "source": "腾讯体育", "time": "2026-06-12", "hot": True},
                {"title": "库里职业生涯三分球命中数突破3700个", "source": "NBA中文官网", "time": "2026-06-11", "hot": False},
                {"title": "勇士队成功晋级总决赛，库里剑指第五冠", "source": "虎扑", "time": "2026-06-10", "hot": False},
                {"title": "NBA Finals MVP榜单：库里领跑", "source": "腾讯体育", "time": "2026-06-09", "hot": False},
            ],
            "sports_football": [
                {"title": "2026世界杯小组赛A组：德国7-0大胜开门红", "source": "FIFA官网", "time": "2026-06-12", "hot": True},
                {"title": "日本2-1逆转德国，亚洲球队再创奇迹", "source": "懂球帝", "time": "2026-06-12", "hot": True},
                {"title": "阿根廷3-0轻取对手，梅西首战破门", "source": "虎扑足球", "time": "2026-06-11", "hot": False},
                {"title": "法国4-0横扫对手，姆巴佩梅开二度", "source": "懂球帝", "time": "2026-06-11", "hot": False},
                {"title": "巴西2-0战胜克罗地亚，内马尔建功", "source": "FIFA官网", "time": "2026-06-10", "hot": False},
                {"title": "韩国1-0小胜乌拉圭，孙兴慜点球破门", "source": "虎扑足球", "time": "2026-06-10", "hot": False},
            ],
            "tech_ai": [
                {"title": "OpenAI发布GPT-5 Turbo，AI能力再创新高", "source": "OpenAI官网", "time": "2026-06-12", "hot": True},
                {"title": "谷歌发布Gemini 2.5 Ultra，全面超越GPT-5", "source": "Google AI", "time": "2026-06-11", "hot": True},
                {"title": "Anthropic发布Claude 4.0，推理能力大幅提升", "source": "Anthropic官网", "time": "2026-06-10", "hot": False},
                {"title": "百度文心一言4.0发布，中文能力全球第一", "source": "机器之心", "time": "2026-06-09", "hot": False},
                {"title": "阿里通义千问Qwen3发布，开源模型登顶榜首", "source": "阿里云", "time": "2026-06-08", "hot": False},
            ],
            "tech_products": [
                {"title": "Apple WWDC 2026：iOS 20发布，AI全面赋能", "source": "Apple官网", "time": "2026-06-12", "hot": True, "category": "Apple"},
                {"title": "NVIDIA RTX 5090 Ti正式发布，光追性能翻倍", "source": "NVIDIA官网", "time": "2026-06-11", "hot": True, "category": "NVIDIA"},
                {"title": "Tesla FSD V15全球推送，完全自动驾驶临近", "source": "Tesla官网", "time": "2026-06-10", "hot": False, "category": "Tesla"},
                {"title": "小米15 Ultra正式发布，影像系统全球第一", "source": "小米官网", "time": "2026-06-09", "hot": False, "category": "小米"},
                {"title": "华为Mate 70 Pro发布，麒麟9020芯片性能爆表", "source": "华为官网", "time": "2026-06-08", "hot": False, "category": "华为"},
            ],
            "world_news": [
                {"title": "中美贸易谈判取得重大进展", "source": "参考消息", "time": "2026-06-12", "hot": True, "region": "美国"},
                {"title": "俄乌冲突迎来停火曙光，各方谈判重启", "source": "环球时报", "time": "2026-06-11", "hot": True, "region": "欧洲"},
                {"title": "台海局势稳定，和平发展成主旋律", "source": "观察者网", "time": "2026-06-10", "hot": False, "region": "亚洲"},
                {"title": "全球军费开支创新高，AI武器成焦点", "source": "参考消息", "time": "2026-06-09", "hot": False, "region": "军事"},
                {"title": "美军在亚太地区举行大规模军演", "source": "环球时报", "time": "2026-06-08", "hot": False, "region": "美国"},
            ],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_news(news)
    return news

# ==============================================================================
# 【4】项目库模块 (projects)
# ==============================================================================
PROJECTS_FILE = 'projects_data.json'

def load_projects():
    """加载项目数据"""
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_projects(projects):
    """保存项目数据"""
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

# ==============================================================================
# 【5】成长记录模块 (growth)
# ==============================================================================
GROWTH_FILE = 'growth_data.json'

def load_growth():
    """加载成长记录"""
    if os.path.exists(GROWTH_FILE):
        with open(GROWTH_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"years": {}}

def save_growth(data):
    """保存成长记录"""
    with open(GROWTH_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==============================================================================
# 【6】静态数据定义
# ==============================================================================
# 杭州活动数据
ACTIVITY_DATA = [
    {"id": 1, "title": "中国美术学院毕业展2026", "date": "2026-05-18 至 06-18", "location": "中国美术学院象山校区", "category": "艺术", "source": "中国美院官网", "url": "http://www.caa.edu.cn"},
    {"id": 2, "title": "杭州西湖音乐节2026", "date": "2026-06-15 至 06-16", "location": "西湖景区太子湾公园", "category": "音乐", "source": "大麦网", "url": "https://www.damai.cn"},
    {"id": 3, "title": "杭州国际动漫节2026", "date": "2026-04-30 至 05-05", "location": "杭州白马湖国际会展中心", "category": "动漫", "source": "杭州动漫节官网", "url": "http://www.cicaf.com"},
    {"id": 4, "title": "杭州马拉松2026", "date": "2026-11-24", "location": "杭州奥体中心", "category": "体育", "source": "杭州马拉松官网", "url": "http://www.hzim.org"},
    {"id": 5, "title": "杭州文博会2026", "date": "2026-10-17 至 10-20", "location": "杭州国际博览中心", "category": "文化", "source": "杭州文博会官网", "url": "http://www.hzccie.com"},
    {"id": 6, "title": "浙江美术馆年度特展", "date": "2026-03-01 至 08-31", "location": "浙江美术馆", "category": "艺术", "source": "浙江美术馆官网", "url": "http://www.zjam.org.cn"},
]

# 求职数据
JOB_DATA = [
    {"id": 1, "title": "测试开发工程师", "company": "阿里巴巴", "location": "杭州", "salary": "22-38K", "experience": "3-5年", "url": "https://talent.alibaba.com"},
    {"id": 2, "title": "自动化测试工程师", "company": "网易", "location": "杭州", "salary": "20-32K", "experience": "2-4年", "url": "https://campus.163.com"},
    {"id": 3, "title": "测试开发工程师", "company": "字节跳动", "location": "杭州", "salary": "25-42K", "experience": "3-5年", "url": "https://jobs.bytedance.com"},
    {"id": 4, "title": "软件测试工程师", "company": "华为", "location": "杭州", "salary": "20-35K", "experience": "2-4年", "url": "https://career.huawei.com"},
    {"id": 5, "title": "测试开发工程师", "company": "海康威视", "location": "杭州", "salary": "18-30K", "experience": "2-4年", "url": "https://www.hikvision.com/cn/careers/"},
    {"id": 6, "title": "测试工程师", "company": "小米", "location": "杭州", "salary": "20-33K", "experience": "2-4年", "url": "https://hr.xiaomi.com"},
]

# 企业链接
COMPANY_LINKS = [
    {"name": "阿里巴巴", "logo": "🏢", "url": "https://talent.alibaba.com", "category": "互联网"},
    {"name": "网易", "logo": "🎮", "url": "https://campus.163.com", "category": "互联网"},
    {"name": "字节跳动", "logo": "📱", "url": "https://jobs.bytedance.com", "category": "互联网"},
    {"name": "华为", "logo": "📡", "url": "https://career.huawei.com", "category": "通信"},
    {"name": "海康威视", "logo": "📷", "url": "https://www.hikvision.com/cn/careers/", "category": "安防"},
    {"name": "大华", "logo": "🔒", "url": "https://www.dahuatech.com/careers/", "category": "安防"},
    {"name": "同花顺", "logo": "📈", "url": "https://www.10jqka.com.cn/about/careers/", "category": "金融"},
    {"name": "菜鸟网络", "logo": "📦", "url": "https://cainiao.tmall.com/careers/", "category": "物流"},
]

# 测开学习数据
STUDY_DATA = {
    "exam_structure": {
        "title": "海康测开校招笔试题型",
        "structure": "单选 + 多选 + 简答 + 编程（共约90–120分钟）",
        "sections": [
            {"name": "单选题", "count": "15–20道", "score": "约40分", "content": "计算机基础、网络、OS、Python、测试理论、SQL"},
            {"name": "多选题", "count": "5–10道", "score": "约20分", "content": "网络协议、Linux命令、测试分类、Python特性、数据库索引/事务"},
            {"name": "简答题", "count": "2–3道", "score": "约20分", "content": "测试用例设计、接口测试流程、偶现bug排查、TCP三次握手"},
            {"name": "编程题", "count": "1–2道", "score": "约20分", "content": "难度：LeetCode 简单，语言优先Python"},
        ]
    },
    "content_directions": [
        {"name": "测试基础", "importance": "必考，占比高", "topics": ["测试流程、测试分类（黑/白/灰盒；功能/接口/自动化/性能）", "用例设计：等价类、边界值、场景法（简答高频）", "缺陷生命周期、bug报告要素", "自动化测试适用场景、优缺点"]},
        {"name": "Python", "importance": "主力语言", "topics": ["基础：数据类型、列表/字典/元组、循环、函数、类、继承", "高频：字符串处理、正则、文件读写、异常处理", "编程题：字符串反转、去重、合并数组、简单逻辑模拟"]},
        {"name": "计算机网络", "importance": "海康最爱", "topics": ["TCP/UDP 区别、三次握手/四次挥手", "HTTP 状态码（200/301/404/500/502）", "HTTPS、Socket、IP、端口、DNS"]},
        {"name": "Linux", "importance": "必考命令", "topics": ["文件：ls、cd、pwd、mkdir、rm、cp、mv、cat、tail、grep", "进程：ps、top、kill、netstat", "日志：tail -f、grep -i error"]},
        {"name": "数据库", "importance": "MySQL", "topics": ["增删改查、 where、group by、order by、limit", "多表查询（join）、索引作用、事务ACID"]},
    ],
    "practice_channels": [
        {"name": "牛客网", "description": "海康真题最多，必刷", "tips": ["搜：海康威视 测试开发 笔试题", "重点刷：2024–2026年测开真题、Python专项、SQL专项、Linux专项"], "url": "https://www.nowcoder.com"},
        {"name": "LeetCode", "description": "只刷简单", "tips": ["数组：两数之和、合并两个有序数组、移除元素", "字符串：反转字符串、字符串中的单词、最长公共前缀", "每天3–5道，1周足够"], "url": "https://leetcode.cn"},
        {"name": "SQL刷题", "description": "牛客网SQL入门到进阶", "tips": ["简单查询、多表查询"], "url": "https://www.nowcoder.com"},
        {"name": "Linux命令", "description": "牛客网Linux常用命令专项", "tips": ["自己装个虚拟机/用在线终端敲一遍"], "url": "https://www.nowcoder.com"},
    ],
    "review_priority": [
        {"day": "第1天", "goal": "必拿分，70%分数", "tasks": ["测试理论：用例设计方法、测试分类、缺陷流程（背熟）", "Python基础：列表/字典操作、字符串、循环、函数", "Linux高频命令：ls、cd、tail、grep、ps、netstat", "网络：TCP三次握手、HTTP状态码（背熟）"]},
        {"day": "第2天", "goal": "稳过线，20%分数", "tasks": ["SQL：单表查询、where、group by、order by、简单join", "编程题：字符串+数组各练5题", "简答题模板：用例设计、偶现bug排查、接口测试流程"]},
        {"day": "第3天", "goal": "冲高分，10%分数", "tasks": ["多刷海康真题（牛客），熟悉出题风格", "补充：进程线程区别、死锁、索引、事务ACID"]},
    ],
    "answer_strategy": [
        "单选多选：快速过，不会先标记，别纠结",
        "简答：分点写（1/2/3），字少但要点全",
        "编程：先写能跑的简单版本，再优化；注释写清楚",
    ]
}

# 体育数据
SPORTS_DATA = {
    "nba": {
        "title": "NBA篮球资讯",
        "favorite_player": "库里 (Stephen Curry)",
        "favorite_team": "金州勇士",
        "links": [
            {"name": "虎扑NBA", "url": "https://nba.hupu.com"},
            {"name": "腾讯体育", "url": "https://sports.qq.com/nba/"},
            {"name": "NBA中文官网", "url": "https://china.nba.com"},
        ]
    },
    "football": {
        "title": "2026世界杯",
        "info": "2026年世界杯将由美国、加拿大、墨西哥联合举办，扩军至48支球队",
        "highlights": [
            {"team": "德国", "group": "A组", "note": "传统强队，2014年冠军", "flag": "🇩🇪"},
            {"team": "法国", "group": "D组", "note": "2018年冠军，阵容豪华", "flag": "🇫🇷"},
            {"team": "巴西", "group": "G组", "note": "五冠王，足球王国", "flag": "🇧🇷"},
            {"team": "日本", "group": "E组", "note": "亚洲之光，连续晋级", "flag": "🇯🇵"},
            {"team": "韩国", "group": "H组", "note": "孙兴慜领衔", "flag": "🇰🇷"},
            {"team": "英格兰", "group": "C组", "note": "欧洲强队", "flag": "🏴"},
            {"team": "西班牙", "group": "B组", "note": "2010年冠军", "flag": "🇪🇸"},
            {"team": "阿根廷", "group": "C组", "note": "2022年冠军，梅西", "flag": "🇦🇷"},
        ],
        "links": [
            {"name": "FIFA世界杯官网", "url": "https://www.fifa.com/worldcup"},
            {"name": "懂球帝", "url": "https://www.dongqiudi.com"},
            {"name": "虎扑足球", "url": "https://soccer.hupu.com"},
        ]
    }
}

# 科技数据
TECH_DATA = {
    "ai": {
        "title": "AI人工智能",
        "links": [
            {"name": "OpenAI", "url": "https://openai.com"},
            {"name": "Anthropic", "url": "https://anthropic.com"},
            {"name": "机器之心", "url": "https://jiqizhixin.com"},
        ]
    },
    "tech_news": {
        "title": "科技新品",
        "categories": [
            {"name": "Apple苹果", "icon": "🍎"},
            {"name": "英伟达NVIDIA", "icon": "🎮"},
            {"name": "Tesla特斯拉", "icon": "🚗"},
            {"name": "小米", "icon": "📱"},
        ],
        "links": [
            {"name": "36氪", "url": "https://36kr.com"},
            {"name": "极客公园", "url": "https://geekpark.net"},
            {"name": "爱范儿", "url": "https://ifanr.com"},
        ]
    }
}

# 世界局势数据
WORLD_DATA = {
    "title": "世界局势与国际动态",
    "regions": [
        {"name": "美国", "icon": "🇺🇸", "topics": [
            {"title": "中美关系最新动态", "summary": "贸易谈判与科技领域合作进展"},
            {"title": "美联储利率政策", "summary": "2026年货币政策走向分析"},
            {"title": "美国大选", "summary": "2026年中期选举备受关注"},
        ]},
        {"name": "欧洲", "icon": "🇪🇺", "topics": [
            {"title": "俄乌冲突", "summary": "和平谈判重启，局势缓和"},
            {"title": "欧盟经济", "summary": "能源转型与经济复苏并进"},
        ]},
        {"name": "亚洲", "icon": "🌏", "topics": [
            {"title": "中日韩关系", "summary": "经贸合作持续深化"},
            {"title": "台海局势", "summary": "和平发展是主旋律"},
        ]},
    ],
    "military": {
        "title": "军事动态",
        "updates": [
            {"title": "全球军费开支增长", "summary": "各国国防预算持续攀升"},
            {"title": "新型武器装备", "summary": "海陆空天多领域更新迭代"},
            {"title": "AI军事应用", "summary": "无人系统与智能武器成焦点"},
        ]
    },
    "links": [
        {"name": "参考消息", "url": "https://www.cankaoxiaoxi.com"},
        {"name": "环球时报", "url": "https://www.huanqiu.com"},
        {"name": "观察者网", "url": "https://www.guancha.cn"},
    ]
}

# 小说影视数据
NOVEL_DATA = {
    "title": "小说影视推荐",
    "novels": [
        {
            "title": "大奉打更人",
            "author": "卖报小郎君",
            "type": "古典仙侠探案",
            "status": "已完结",
            "chapters": 1000,
            "description": "警校毕业的许七安穿越到异世界成为小捕快，凭借现代刑侦知识破解税银大案，入职打更人后一路成长为国士。他周旋于朝堂、江湖、佛道之间，见证了皇室的腐朽，拥立新帝，最终以凡人之躯逆伐神魔，成为绝世武神。",
            "characters": [
                {"name": "许七安", "role": "主角", "desc": "现代穿越者，刑侦高手，从囚徒到打更人，最终成为武神"},
                {"name": "魏渊", "role": "打更人首领", "desc": "亦师亦父，心怀天下，战死沙场"},
                {"name": "怀庆长公主", "role": "女帝", "desc": "聪慧果决，大奉女帝，许七安的坚定支持者"},
                {"name": "许平志", "role": "二叔", "desc": "刻板正直的武官，许七安的养父"},
                {"name": "褚采薇", "role": "司天监弟子", "desc": "活泼可爱的术士，厨艺精湛"},
                {"name": "李妙真", "role": "天宗圣女", "desc": "行侠仗义，天地会核心成员"},
                {"name": "神殊", "role": "佛门大能", "desc": "寄宿在许七安体内的残魂，半步武神级战力"},
                {"name": "洛玉衡", "role": "国师", "desc": "人宗道首，渡劫成就一品"},
            ],
            "highlights": [
                "第一卷·京察风云：税银案初露锋芒，桑泊案揭示国运密码",
                "第二卷·国士无双：佛门赌赛辩法，斩杀镇北王血屠三千里",
                "第三卷·江湖路远：身世揭秘，纵横九州积蓄力量",
                "第四卷·逐鹿中原：拥立怀庆登基，平定云州叛乱",
                "第五卷·绝世武神：四大超品灭世浩劫，武神一刀斩神魔",
                "经典战役：云州独断后、楚州斩亲王、京城扶女帝、海外战诸神"
            ]
        },
        {
            "title": "庆余年",
            "author": "猫腻",
            "type": "历史玄幻",
            "status": "已完结",
            "chapters": 783,
            "description": "范闲，庆国数十年风雨的见证者。他偷渡到这个世界，凭借过人的智慧和手腕，在复杂的朝堂斗争中步步为营，最终成为一代传奇。",
            "characters": [
                {"name": "范闲", "role": "主角", "desc": "性格现代的古代人，机智聪慧"},
                {"name": "范建", "role": "养父", "desc": "户部侍郎，深藏不露"},
                {"name": "陈萍萍", "role": "检察院院长", "desc": "表面冷酷，实则护犊情深"},
                {"name": "庆帝", "role": "皇帝", "desc": "四大宗师之一，城府极深"},
                {"name": "林婉儿", "role": "女主", "desc": "鸡腿姑娘，温婉可爱"},
                {"name": "范若若", "role": "妹妹", "desc": "才女，兄控"},
            ],
            "highlights": [
                "范闲朝堂斗诗：醉酒背诗三百首，震惊四座",
                "澹泊书局：开创古代出版业先河",
                "范闲vs庆帝：父子终极对决",
                "陈萍萍之死：悲情英雄的落幕",
                "范闲隐退：事了拂衣去，深藏身与名"
            ]
        },
        {
            "title": "我真的没想重生啊",
            "author": "柳暗花又明",
            "type": "都市重生",
            "status": "已完结",
            "chapters": 1500,
            "description": "商业精英沈列重生回到高考前夕，利用前世记忆和商业头脑，在都市中步步为营，打造商业帝国的同时收获爱情和友情。",
            "characters": [
                {"name": "沈列", "role": "主角", "desc": "重生者，商业天才"},
                {"name": "陈正伦", "role": "挚友", "desc": "义气兄弟，后期重要伙伴"},
                {"name": "江华", "role": "商业对手", "desc": "与主角亦敌亦友"},
            ],
            "highlights": [
                "重生高考：提前交卷震惊全场",
                "创业起步：从校园代理到商业帝国",
                "商战经典：多次经典商业案例",
                "情感纠葛：多位红颜知己的感情线",
                "阶层跨越：从普通人到商业巨擘"
            ]
        },
        {
            "title": "凡人修仙传",
            "author": "忘语",
            "type": "仙侠修真",
            "status": "已完结",
            "chapters": "3000+",
            "description": "一个资质平庸的少年韩立，偶得神秘小瓶，凭借坚韧不拔的心性和机灵的头脑，一步步踏入修仙之路，最终飞升灵界。",
            "characters": [
                {"name": "韩立", "role": "主角", "desc": "资质平庸但心性坚韧，善于隐忍"},
                {"name": "南宫婉", "role": "女主", "desc": "掩月宗天灵根，与韩立多世情缘"},
                {"name": "向之礼", "role": "化神期前辈", "desc": "人界最强存在之一"},
                {"name": "大衍神君", "role": "元婴期傀儡师", "desc": "韩立师傅，留下诸多遗产"},
            ],
            "highlights": [
                "小绿瓶：逆天宝物，加速灵药成熟",
                "韩立结丹：天南修仙界震动",
                "元婴后期：人界第一人",
                "灵界篇：更大世界，更多机缘",
                "飞升仙界：凡人成仙的传奇",
            ]
        }
    ],
    "movies": [
        {"title": "流浪地球3", "year": "2025", "director": "郭帆", "description": "太阳即将毁灭，人类在地球表面建造出巨大的推进器，寻找新家园。", "highlights": ["科幻大作", "国产科幻巅峰"]},
    ],
    "links": [
        {"name": "起点中文网", "url": "https://www.qidian.com"},
        {"name": "纵横中文网", "url": "https://www.zongheng.com"},
        {"name": "豆瓣读书", "url": "https://book.douban.com"},
    ]
}

# 个人数据
PERSONAL_DATA = {
    "profile": {
        "name": "小明",
        "education": "211计算机本科",
        "location": "📍 杭州",
        "hometown": "🏠 湖北",
        "background": "北京高校计算机专业毕业",
        "goals": [
            "🏢 入职杭州科技企业（阿里、网易、海康等）",
            "📝 备考浙江公务员/事业编",
            "📈 提升技术实力和综合素质",
        ]
    },
    "interests": {
        "sports": "🏀 NBA忠实球迷 | 🦾库里粉丝 | ⚽足球世界杯",
        "tech": "🤖 AI人工智能 | 🚗 新能源汽车 | 📱 科技新品",
        "world": "🌍 国际局势 | ⚔️ 军事动态 | 🇺🇸 中美关系",
        "entertainment": "📚 玄幻小说 | 🎬 科幻电影 | 🎮 游戏"
    }
}

# ==============================================================================
# 【7】页面路由
# ==============================================================================
@app.route('/')
def index():
    """首页 - 杭州活动"""
    return render_template('index.html', activities=ACTIVITY_DATA)

@app.route('/hub')
def hub():
    """个人中心"""
    return render_template('hub.html', personal=PERSONAL_DATA)

@app.route('/sports')
def sports():
    """体育资讯"""
    news = init_default_news()
    sports_data = SPORTS_DATA.copy()
    sports_data['nba']['news'] = news['sports_nba']
    sports_data['football']['highlights'] = news['sports_football']
    return render_template('sports.html', data=sports_data, news=news)

@app.route('/tech')
def tech():
    """科技资讯"""
    news = init_default_news()
    tech_data = TECH_DATA.copy()
    tech_data['ai']['latest'] = news['tech_ai']
    tech_data['tech_news']['categories'] = [
        {"name": "Apple苹果", "icon": "🍎", "events": [e for e in news['tech_products'] if e.get('category') == 'Apple']},
        {"name": "英伟达NVIDIA", "icon": "🎮", "events": [e for e in news['tech_products'] if e.get('category') == 'NVIDIA']},
        {"name": "Tesla特斯拉", "icon": "🚗", "events": [e for e in news['tech_products'] if e.get('category') == 'Tesla']},
        {"name": "小米", "icon": "📱", "events": [e for e in news['tech_products'] if e.get('category') == '小米']},
    ]
    return render_template('tech.html', data=tech_data, news=news)

@app.route('/world')
def world():
    """世界局势"""
    news = init_default_news()
    world_data = WORLD_DATA.copy()
    world_data['regions'][0]['topics'] = [t for t in news['world_news'] if t.get('region') == '美国']
    world_data['regions'][1]['topics'] = [t for t in news['world_news'] if t.get('region') == '欧洲']
    world_data['regions'][2]['topics'] = [t for t in news['world_news'] if t.get('region') == '亚洲']
    return render_template('world.html', data=world_data, news=news)

@app.route('/entertainment')
def entertainment():
    """小说影视"""
    return render_template('entertainment.html', data=NOVEL_DATA)

@app.route('/job')
def job():
    """求职导航"""
    return render_template('job.html', jobs=JOB_DATA, company_links=COMPANY_LINKS)

@app.route('/study')
def study():
    """测开学习"""
    return render_template('study.html', data=STUDY_DATA)

@app.route('/tech_learning')
def tech_learning():
    """计算机技术学习树"""
    return render_template('tech_learning.html')

@app.route('/ai_learning')
def ai_learning():
    """AI学习知识库"""
    return render_template('ai_learning.html')

@app.route('/projects')
def projects():
    """项目库"""
    projects_list = load_projects()
    return render_template('projects.html', projects=projects_list)

@app.route('/growth')
def growth():
    """成长记录"""
    growth_data = load_growth()
    return render_template('growth.html', data=growth_data)

@app.route('/news_admin')
def news_admin():
    """资讯管理后台"""
    return render_template('news_admin.html')

# ==============================================================================
# 【8】资讯管理API
# ==============================================================================
@app.route('/api/news', methods=['GET'])
def api_get_news():
    """获取所有资讯"""
    return jsonify(init_default_news())

@app.route('/api/news/<category>', methods=['GET'])
def api_get_news_by_category(category):
    """按分类获取资讯"""
    news = init_default_news()
    if category in news:
        return jsonify({"data": news[category], "category": category})
    return jsonify({"error": "分类不存在"}), 404

@app.route('/api/news', methods=['POST'])
def api_add_news():
    """添加资讯"""
    data = request.get_json()
    category = data.get('category')
    title = data.get('title')
    source = data.get('source', '手动添加')
    
    if not category or not title:
        return jsonify({"error": "缺少必要参数"}), 400
    
    news = init_default_news()
    new_item = {
        "title": title,
        "source": source,
        "time": datetime.now().strftime("%Y-%m-%d"),
        "hot": False
    }
    
    if category in news:
        news[category].insert(0, new_item)
        news[category] = news[category][:30]  # 只保留最近30条
    else:
        news[category] = [new_item]
    
    save_news(news)
    return jsonify({"message": "添加成功", "data": new_item})

@app.route('/api/news/<category>/<int:index>', methods=['DELETE'])
def api_delete_news(category, index):
    """删除资讯"""
    news = init_default_news()
    if category in news and 0 <= index < len(news[category]):
        deleted = news[category].pop(index)
        save_news(news)
        return jsonify({"message": "删除成功", "data": deleted})
    return jsonify({"error": "删除失败"}), 404

@app.route('/api/news/update', methods=['POST'])
def api_update_news():
    """批量更新资讯"""
    data = request.get_json()
    news = init_default_news()
    
    if 'category' in data and 'items' in data:
        news[data['category']] = data['items'] + news.get(data['category'], [])
        news[data['category']] = news[data['category']][:30]
    
    save_news(news)
    return jsonify({"message": "更新成功", "last_updated": news['last_updated']})

# ==============================================================================
# 【9】项目库API
# ==============================================================================
@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    """获取项目列表"""
    return jsonify({"data": load_projects()})

@app.route('/api/projects', methods=['POST'])
def api_add_project():
    """上传项目文件"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    tech_stack = request.form.get('tech_stack', '')
    
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    project = {
        "id": str(uuid.uuid4().hex[:8]),
        "title": title,
        "description": description,
        "tech_stack": tech_stack,
        "filename": file.filename,
        "stored_filename": unique_filename,
        "file_size": os.path.getsize(filepath),
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    projects = load_projects()
    projects.insert(0, project)
    save_projects(projects)
    
    return jsonify({"message": "上传成功", "data": project})

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    """删除项目"""
    projects = load_projects()
    projects = [p for p in projects if p['id'] != project_id]
    save_projects(projects)
    return jsonify({"message": "删除成功"})

@app.route('/api/projects/<project_id>/download')
def api_download_project(project_id):
    """下载项目文件"""
    projects = load_projects()
    project = next((p for p in projects if p['id'] == project_id), None)
    if not project:
        return jsonify({"error": "项目不存在"}), 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], project['stored_filename'], as_attachment=True, download_name=project['filename'])

# ==============================================================================
# 【10】成长记录API
# ==============================================================================
@app.route('/api/growth', methods=['GET'])
def api_get_growth():
    """获取成长记录"""
    return jsonify(load_growth())

@app.route('/api/growth', methods=['POST'])
def api_add_growth():
    """添加成长记录"""
    data = request.get_json()
    year = data.get('year')
    week = data.get('week')
    day = data.get('day')
    content = data.get('content')
    record_type = data.get('type', 'daily')
    
    growth_data = load_growth()
    
    if year not in growth_data['years']:
        growth_data['years'][year] = {"weeks": {}, "months": {}, "summary": ""}
    
    if record_type == 'daily':
        if week not in growth_data['years'][year]['weeks']:
            growth_data['years'][year]['weeks'][week] = {"days": {}}
        growth_data['years'][year]['weeks'][week]['days'][day] = {
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    elif record_type == 'weekly':
        growth_data['years'][year]['weeks'][week] = {
            "summary": content,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    elif record_type == 'monthly':
        growth_data['years'][year]['months'][data.get('month')] = {
            "summary": content,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    
    save_growth(growth_data)
    return jsonify({"message": "保存成功"})

@app.route('/api/growth/<year>/<week>', methods=['DELETE'])
def api_delete_week(year, week):
    """删除周记录"""
    growth_data = load_growth()
    if year in growth_data['years'] and week in growth_data['years'][year]['weeks']:
        del growth_data['years'][year]['weeks'][week]
        save_growth(growth_data)
    return jsonify({"message": "删除成功"})

# ==============================================================================
# 【11】其他API
# ==============================================================================
@app.route('/api/activities')
def api_activities():
    """获取活动列表"""
    return jsonify({"data": ACTIVITY_DATA})

@app.route('/api/jobs')
def api_jobs():
    """获取职位列表"""
    return jsonify({"data": JOB_DATA})

@app.route('/api/study')
def api_study():
    """获取学习资料"""
    return jsonify({"data": STUDY_DATA})

# ==============================================================================
# 【12】启动应用
# ==============================================================================
if __name__ == '__main__':
    init_default_news()  # 初始化资讯数据
    app.run(debug=True, host='0.0.0.0', port=5000)
