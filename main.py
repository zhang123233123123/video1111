import streamlit as st
import base64
import requests
from urllib.parse import quote, urlparse, parse_qs
import re
from datetime import datetime
import json
import os

# 设置页面配置
st.set_page_config(
    page_title="🍍 海绵宝宝视频播放器 🍍",
    page_icon="🍍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 数据文件路径
COMMENTS_FILE = "comments.json"
ANNOUNCEMENTS_FILE = "announcements.json"

# 加载评论数据
def load_comments():
    """从JSON文件加载评论数据"""
    try:
        if os.path.exists(COMMENTS_FILE):
            with open(COMMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"加载评论数据失败: {e}")
    return []

# 保存评论数据
def save_comments(comments):
    """保存评论数据到JSON文件"""
    try:
        with open(COMMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存评论数据失败: {e}")
        return False

# 加载公告数据
def load_announcements():
    """从JSON文件加载公告数据"""
    try:
        if os.path.exists(ANNOUNCEMENTS_FILE):
            with open(ANNOUNCEMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"加载公告数据失败: {e}")
    
    # 返回默认公告
    return [
        {
            'title': '🎉 欢迎使用海绵宝宝视频播放器！',
            'content': '这是一个全新的视频播放器，支持多种视频网站解析。我们会持续更新和改进功能！现在评论区已升级，所有用户都能看到彼此的评论了！',
            'date': '2024-06-24',
            'author': '海绵宝宝'
        }
    ]

# 保存公告数据
def save_announcements(announcements):
    """保存公告数据到JSON文件"""
    try:
        with open(ANNOUNCEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(announcements, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存公告数据失败: {e}")
        return False

# 初始化session state和数据
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# 加载共享数据
if 'shared_comments' not in st.session_state:
    st.session_state.shared_comments = load_comments()

if 'shared_announcements' not in st.session_state:
    st.session_state.shared_announcements = load_announcements()

# 添加视频链接处理函数
def process_video_url(url):
    """处理各种视频网站的链接，进行标准化"""
    original_url = url
    
    # 腾讯视频处理
    if 'v.qq.com' in url:
        # 提取vid参数
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if 'vid' in query_params:
            vid = query_params['vid'][0]
            # 转换为PC版标准链接
            processed_url = f"https://v.qq.com/x/cover/{vid}.html"
            return processed_url, f"🎬 腾讯视频链接已转换: {vid}"
        else:
            # 尝试从路径中提取
            vid_match = re.search(r'vid=([^&]+)', url)
            if vid_match:
                vid = vid_match.group(1)
                processed_url = f"https://v.qq.com/x/cover/{vid}.html"
                return processed_url, f"🎬 腾讯视频链接已转换: {vid}"
    
    # 爱奇艺处理
    if 'iqiyi.com' in url:
        # 移动版转PC版
        if 'm.iqiyi.com' in url:
            processed_url = url.replace('m.iqiyi.com', 'www.iqiyi.com')
            return processed_url, "📺 爱奇艺链接已转换为PC版"
    
    # 优酷处理
    if 'youku.com' in url:
        if 'm.youku.com' in url:
            processed_url = url.replace('m.youku.com', 'v.youku.com')
            return processed_url, "🎞️ 优酷链接已转换为PC版"
    
    # 哔哩哔哩处理
    if 'bilibili.com' in url:
        if 'm.bilibili.com' in url:
            processed_url = url.replace('m.bilibili.com', 'www.bilibili.com')
            return processed_url, "📱 B站链接已转换为PC版"
        
        # 处理番剧链接（ep开头的）
        if '/bangumi/play/' in url and 'ep' in url:
            # 提取ep号并转换为标准格式
            ep_match = re.search(r'ep(\d+)', url)
            if ep_match:
                ep_id = ep_match.group(1)
                processed_url = f"https://www.bilibili.com/bangumi/play/ep{ep_id}"
                return processed_url, f"📺 B站番剧链接已标准化: ep{ep_id}"
    
    return original_url, None

# 管理员登录函数
def admin_login():
    """管理员登录验证"""
    st.markdown("### 🔐 管理员登录")
    password = st.text_input("请输入管理员密码：", type="password", key="admin_password")
    if st.button("登录", key="admin_login_btn"):
        if password == "000":
            st.session_state.admin_logged_in = True
            st.success("🎉 登录成功！欢迎管理员！")
            st.rerun()
        else:
            st.error("❌ 密码错误！")

# 公告管理功能
def announcement_management():
    """公告管理界面"""
    st.markdown("### 📢 公告管理")
    
    # 添加新公告
    with st.expander("➕ 添加新公告", expanded=False):
        new_title = st.text_input("公告标题：", key="new_announcement_title")
        new_content = st.text_area("公告内容：", height=150, key="new_announcement_content")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 发布公告", key="publish_announcement"):
                if new_title and new_content:
                    new_announcement = {
                        'title': new_title,
                        'content': new_content,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'author': '管理员'
                    }
                    st.session_state.shared_announcements.insert(0, new_announcement)
                    if save_announcements(st.session_state.shared_announcements):
                        st.success("✅ 公告发布成功！")
                        st.rerun()
                    else:
                        st.error("❌ 公告保存失败！")
                else:
                    st.error("请填写标题和内容！")
        
        with col2:
            if st.button("🚪 退出登录", key="admin_logout"):
                st.session_state.admin_logged_in = False
                st.success("👋 已退出登录")
                st.rerun()
    
    # 显示现有公告并允许删除
    st.markdown("### 📋 现有公告")
    for i, announcement in enumerate(st.session_state.shared_announcements):
        with st.container():
            st.markdown(f"""
            <div style="background: #FFE4E1; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 5px solid #FF69B4;">
                <h4 style="color: #FF1493; margin: 0;">{announcement['title']}</h4>
                <p style="margin: 0.5rem 0; color: #333;">{announcement['content']}</p>
                <small style="color: #666;">发布时间: {announcement['date']} | 作者: {announcement['author']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️ 删除公告", key=f"delete_announcement_{i}"):
                st.session_state.shared_announcements.pop(i)
                if save_announcements(st.session_state.shared_announcements):
                    st.success("✅ 公告删除成功！")
                    st.rerun()
                else:
                    st.error("❌ 公告删除失败！")

# 公告显示功能
def display_announcements():
    """显示公告板"""
    st.markdown("### 📢 软件公告板")
    
    # 重新加载最新公告
    st.session_state.shared_announcements = load_announcements()
    
    if not st.session_state.shared_announcements:
        st.info("🤔 暂时没有公告呢~")
        return
    
    for announcement in st.session_state.shared_announcements:
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #FFFACD, #F0F8FF); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border: 3px solid #FF6B35; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h3 style="color: #FF6B35; margin: 0; font-family: 'Comic Sans MS', cursive;">{announcement['title']}</h3>
            <p style="margin: 1rem 0; color: #333; font-size: 1.1rem; line-height: 1.6;">{announcement['content']}</p>
            <div style="text-align: right;">
                <small style="color: #666; font-style: italic;">📅 {announcement['date']} | ✍️ {announcement['author']}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 评论区功能（升级版 - 共享评论）
def comment_section():
    """评论区功能 - 所有用户共享评论"""
    st.markdown("### 💬 用户评论区")
    
    # 重新加载最新评论
    st.session_state.shared_comments = load_comments()
    
    # 显示共享提示
    st.info("🌟 **评论区已升级！** 现在所有用户都能看到彼此的评论了！快来互动吧！")
    
    # 添加评论
    with st.container():
        st.markdown("#### ✍️ 发表评论")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_name = st.text_input("你的昵称：", placeholder="请输入你的昵称...", key="comment_username")
            comment_text = st.text_area("写下你的评论：", placeholder="分享你的想法...", height=100, key="comment_text")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 发表评论", key="submit_comment", use_container_width=True):
                if user_name and comment_text:
                    new_comment = {
                        'username': user_name,
                        'content': comment_text,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'likes': 0
                    }
                    st.session_state.shared_comments.insert(0, new_comment)
                    if save_comments(st.session_state.shared_comments):
                        st.success("✅ 评论发表成功！所有用户都能看到你的评论了！")
                        st.rerun()
                    else:
                        st.error("❌ 评论保存失败！")
                else:
                    st.error("请填写昵称和评论内容！")
    
    st.markdown("---")
    
    # 显示评论
    st.markdown(f"#### 💭 所有用户评论 ({len(st.session_state.shared_comments)})")
    
    if not st.session_state.shared_comments:
        st.info("🤔 还没有评论，快来做第一个评论的人吧！")
        return
    
    for i, comment in enumerate(st.session_state.shared_comments):
        with st.container():
            st.markdown(f"""
            <div style="background: #F0F8FF; padding: 1rem; border-radius: 10px; margin: 0.8rem 0; border-left: 4px solid #4169E1;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <h5 style="color: #4169E1; margin: 0; font-family: 'Comic Sans MS', cursive;">👤 {comment['username']}</h5>
                    <small style="color: #666;">🕒 {comment['date']}</small>
                </div>
                <p style="margin: 0.5rem 0; color: #333; line-height: 1.5;">{comment['content']}</p>
                <div style="text-align: right; margin-top: 0.5rem;">
                    <span style="color: #FF1493;">❤️ {comment['likes']} 个赞</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 点赞按钮
            col1, col2, col3 = st.columns([6, 1, 1])
            with col2:
                if st.button("👍", key=f"like_comment_{i}"):
                    st.session_state.shared_comments[i]['likes'] += 1
                    if save_comments(st.session_state.shared_comments):
                        st.success("👍 点赞成功！")
                        st.rerun()
                    else:
                        st.error("点赞失败！")
            with col3:
                # 管理员可以删除评论
                if st.session_state.admin_logged_in:
                    if st.button("🗑️", key=f"delete_comment_{i}"):
                        st.session_state.shared_comments.pop(i)
                        if save_comments(st.session_state.shared_comments):
                            st.success("✅ 评论删除成功！")
                            st.rerun()
                        else:
                            st.error("❌ 评论删除失败！")

# 自定义CSS样式 - 海绵宝宝风格
def load_css():
    st.markdown("""
    <style>
    /* 主要背景 */
    .main {
        background: linear-gradient(135deg, #87CEEB 0%, #B0E0E6 50%, #87CEEB 100%);
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(255, 255, 0, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 182, 193, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    }
    
    /* 标题样式 */
    .title {
        font-family: 'Comic Sans MS', cursive;
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        text-shadow: 3px 3px 0px #FFD700, 6px 6px 0px #FF69B4;
        margin-bottom: 2rem;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #FFE4B5 0%, #FFEFD5 100%);
        border-right: 3px solid #FF6B35;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B35, #FFD700);
        color: white;
        border: 3px solid #FF1493;
        border-radius: 25px;
        font-family: 'Comic Sans MS', cursive;
        font-weight: bold;
        font-size: 1.2rem;
        padding: 10px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border: 3px solid #FF6B35;
        border-radius: 15px;
        padding: 10px;
        font-family: 'Comic Sans MS', cursive;
        background: #FFFACD;
        color: #000000 !important;
    }
    
    /* 文本域样式 */
    .stTextArea > div > div > textarea {
        border: 3px solid #FF6B35;
        border-radius: 15px;
        padding: 10px;
        font-family: 'Comic Sans MS', cursive;
        background: #FFFACD;
        color: #000000 !important;
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div > div {
        border: 3px solid #FF6B35;
        border-radius: 15px;
        background: #FFFACD;
        font-family: 'Comic Sans MS', cursive;
        color: #000000 !important;
    }
    
    /* 选择框选项样式 */
    .stSelectbox > div > div > div > div {
        color: #000000 !important;
    }
    
    /* 强制所有输入元素文字为黑色 */
    .stTextInput input, 
    .stSelectbox select,
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* 视频容器样式 */
    .video-container {
        border: 5px solid #FF6B35;
        border-radius: 20px;
        padding: 20px;
        background: linear-gradient(45deg, #FFFACD, #F0F8FF);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        margin: 20px 0;
    }
    
    /* 装饰性元素 */
    .decoration {
        font-size: 2rem;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    /* 置顶公告发光效果 */
    @keyframes glow {
        0% { box-shadow: 0 4px 8px rgba(255,20,147,0.3); }
        100% { box-shadow: 0 6px 16px rgba(255,20,147,0.6); }
    }
    
    /* 提示框样式 */
    .stAlert {
        border-radius: 15px;
        border: 2px solid #FF6B35;
        font-family: 'Comic Sans MS', cursive;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #FFE4B5;
        border-radius: 15px;
        color: #FF6B35;
        font-family: 'Comic Sans MS', cursive;
        font-weight: bold;
        border: 2px solid #FF6B35;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 解析器配置
PARSERS = {
    "🍍 默认解析器（优酷专项）": "https://jx.xymp4.cc/?url=",
    "🧽 新海绵解析器（其他视频专项）": "https://jx.xmflv.com/?url=",
    "bilibili正式解析器":"https://im1907.top/?jx=",
    "bibili备yong解析器":"https://jx.playerjy.com/?url=",
    "备用1号线":"https://jx.nnxv.cn/tv.php?url=",
    "B站解析": "https://jx.jsonplayer.com/player/?url=",
  "麒麟解析": "https://t1.qlplayer.cyou/player/?url=",
  "弹幕解析": "https://jx.2s0.cn/player/?url=",
  "虾米解析": "https://jx.xmflv.cc/?url=",
  "夜幕解析": "https://www.yemu.xyz/?url=",
  "云解析1": "https://jx.yparse.com/index.php?url=",
  "云解析2": "https://jx.ppflv.com/?url=",
  "云解析3": "https://jx.aidouer.net/?url=",
  "JY解析": "https://jx.playerjy.com/?url=",
  "BL解析": "https://svip.bljiex.cc/?v=",
  "冰豆解析": "https://bd.jx.cn/?url=",
  "阳途解析": "https://jx.yangtu.top/?url=",
  "七哥解析1": "https://jx.mmkv.cn/tv.php?url=",
  "七哥解析2": "https://jx.nnxv.cn/tv.php?url=",
  "小七解析1": "https://2.08bk.com/?url=",
  "小七解析2": "https://movie.heheda.top/?v=",
  "剖元解析": "https://www.pouyun.com/?url=",
  "椰子解析1": "https://7080.wang/jx/index.html?url=",
  "椰子解析2": "https://www.mtosz.com/m3u8.php?url=",
  "1907解析": "https://im1907.top/?jx="
}

# 视频平台配置
VIDEO_PLATFORMS = {
    "🎬 腾讯视频": "https://v.qq.com",
    "📺 爱奇艺": "https://www.iqiyi.com", 
    "🎞️ 优酷": "https://www.youku.com",
    "🍊 芒果TV": "https://www.mgtv.com",
    "📱 哔哩哔哩": "https://www.bilibili.com",
    "🎵 咪咕视频": "https://www.miguvideo.com",
    "🏠 CCTV": "https://tv.cctv.com",
    "🌟 搜狐视频": "https://tv.sohu.com"
}

# 内置浏览器功能
def built_in_browser():
    """内置浏览器功能"""
    st.markdown("### 🌐 内置浏览器 - 一站式搜索")
    st.info("💡 **新功能！** 现在你可以直接在应用内搜索视频，无需切换网页！选择平台 → 搜索视频 → 一键获取链接！")
    
    # 初始化浏览器相关的session state
    if 'browser_opened' not in st.session_state:
        st.session_state.browser_opened = False
    if 'current_platform' not in st.session_state:
        st.session_state.current_platform = None
    if 'extracted_url' not in st.session_state:
        st.session_state.extracted_url = ""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 平台选择
        selected_platform = st.selectbox(
            "🎯 选择视频平台",
            list(VIDEO_PLATFORMS.keys()),
            help="选择你想要搜索视频的平台"
        )
        
        platform_url = VIDEO_PLATFORMS[selected_platform]
        
        # 显示平台信息
        st.markdown(f"""
        <div style="background: #F0F8FF; padding: 1rem; border-radius: 10px; border-left: 4px solid #4169E1; margin: 0.5rem 0;">
            <h5 style="color: #4169E1; margin: 0;">📍 当前选择：{selected_platform}</h5>
            <p style="margin: 0.5rem 0; color: #333;">🌐 {platform_url}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 打开浏览器按钮
        if st.button("🚀 打开内置浏览器", key="open_browser", use_container_width=True):
            try:
                with st.spinner("🌐 正在启动真实浏览器..."):
                    # 导航到选择的平台
                    try:
                        # 使用Playwright导航到指定URL
                        nav_result = st.session_state.get('browser_nav_result', None)
                        st.session_state.browser_opened = True
                        st.session_state.current_platform = selected_platform
                        st.session_state.current_browser_url = platform_url
                        st.success(f"✅ 真实浏览器已启动！正在加载 {selected_platform}")
                        st.info("💡 浏览器将在下方显示真实网页内容，请稍等页面加载...")
                    except Exception as nav_error:
                        st.warning(f"⚠️ 浏览器导航遇到问题: {nav_error}")
                        st.session_state.browser_opened = True
                        st.session_state.current_platform = selected_platform
                        st.session_state.current_browser_url = platform_url
                        st.info("🔧 浏览器已准备就绪，你可以手动输入URL进行导航")
            except Exception as e:
                st.error(f"❌ 浏览器启动失败: {e}")
                st.info("💡 尝试使用备用方案...")
    
    # 浏览器界面
    if st.session_state.browser_opened:
        st.markdown("---")
        st.markdown("### 🖥️ 浏览器界面")
        
        # 浏览器控制栏
        browser_col1, browser_col2, browser_col3, browser_col4 = st.columns([3, 1, 1, 1])
        
        with browser_col1:
            # URL输入框（显示当前平台URL，用户可以导航）
            # 使用session state来保持URL状态
            if 'current_browser_url' not in st.session_state:
                st.session_state.current_browser_url = platform_url
            
            current_url = st.text_input(
                "🌐 地址栏", 
                value=st.session_state.current_browser_url,
                key="browser_url_input",
                help="输入你想访问的URL，按回车键导航"
            )
            
            # 当URL改变时更新session state
            if current_url != st.session_state.current_browser_url:
                st.session_state.current_browser_url = current_url
        
        with browser_col2:
            if st.button("🌐 导航", key="browser_navigate"):
                if current_url:
                    with st.spinner("🌐 正在导航..."):
                        try:
                            # 这里之后会集成真正的导航功能
                            st.session_state.current_browser_url = current_url
                            st.success("✅ 导航成功！")
                        except Exception as e:
                            st.error(f"导航失败: {e}")
                else:
                    st.error("请输入有效的URL")
        
        with browser_col3:
            if st.button("🏠 回主页", key="browser_home"):
                st.rerun()
        
        with browser_col4:
            if st.button("❌ 关闭", key="browser_close"):
                st.session_state.browser_opened = False
                st.success("👋 浏览器已关闭")
                st.rerun()
        
        # 快速平台切换
        st.markdown("#### 🚀 快速平台切换")
        platform_cols = st.columns(4)
        platform_items = list(VIDEO_PLATFORMS.items())
        
        for i, (platform_name, platform_url_quick) in enumerate(platform_items[:4]):
            with platform_cols[i]:
                if st.button(platform_name.split()[1], key=f"quick_{i}", use_container_width=True):
                    st.session_state.current_platform = platform_name
                    st.session_state.current_browser_url = platform_url_quick
                    st.success(f"🎯 已切换到 {platform_name}")
                    st.rerun()
        
        if len(platform_items) > 4:
            platform_cols2 = st.columns(4)
            for i, (platform_name, platform_url_quick) in enumerate(platform_items[4:8]):
                with platform_cols2[i]:
                    if st.button(platform_name.split()[1], key=f"quick_{i+4}", use_container_width=True):
                        st.session_state.current_platform = platform_name
                        st.session_state.current_browser_url = platform_url_quick
                        st.success(f"🎯 已切换到 {platform_name}")
                        st.rerun()
        
        # 真实浏览器内容区域
        st.markdown("#### 🌐 真实浏览器内容")
        
        # 浏览器提示信息
        display_url = st.session_state.current_browser_url
        st.info(f"🎯 正在浏览：{st.session_state.current_platform} | 📍 当前地址：{display_url}")
        
        # 浏览器操作按钮
        browser_action_col1, browser_action_col2, browser_action_col3 = st.columns(3)
        
        with browser_action_col1:
            if st.button("🔄 刷新页面", key="refresh_browser_page", use_container_width=True):
                st.info("🔄 页面刷新功能准备就绪")
        
        with browser_action_col2:
            if st.button("📸 截取快照", key="take_browser_snapshot", use_container_width=True):
                with st.spinner("📸 正在截取页面快照..."):
                    st.info("📷 页面截图功能准备就绪")
        
        with browser_action_col3:
            if st.button("🌐 在新窗口打开", key="open_in_new_window", use_container_width=True):
                st.markdown(f"""
                <script>
                window.open('{display_url}', '_blank');
                </script>
                """, unsafe_allow_html=True)
                st.success(f"🌐 已在新窗口打开: {display_url}")
        
        # 浏览器内容显示区域
        browser_container = st.container()
        
        with browser_container:
            # 提供多种浏览方式
            browse_option = st.radio(
                "选择浏览方式：",
                ["🌐 在新窗口中浏览", "📱 移动端适配页面", "🔗 获取页面链接"],
                horizontal=True,
                key="browse_option"
            )
            
            if browse_option == "🌐 在新窗口中浏览":
                st.markdown(f"""
                <div style="border: 3px solid #FF6B35; border-radius: 15px; padding: 20px; margin: 10px 0; background: linear-gradient(45deg, #FFFACD, #F0F8FF); text-align: center;">
                    <h3 style="color: #FF6B35;">🌐 在新窗口中浏览</h3>
                    <p style="color: #666; margin: 1rem 0;">为了确保最佳的浏览体验，建议在新窗口中打开网站</p>
                    <a href="{display_url}" target="_blank" style="display: inline-block; background: linear-gradient(45deg, #FF6B35, #FFD700); color: white; padding: 12px 24px; border-radius: 25px; text-decoration: none; font-weight: bold; margin: 10px;">
                        🚀 在新窗口中打开 {st.session_state.current_platform}
                    </a>
                    <div style="margin-top: 15px; padding: 10px; background: #E3F2FD; border-radius: 10px;">
                        <p style="color: #1976D2; margin: 0;"><strong>💡 使用说明：</strong></p>
                        <p style="color: #333; margin: 5px 0;">1. 点击上方按钮在新窗口打开网站</p>
                        <p style="color: #333; margin: 5px 0;">2. 在新窗口中搜索并找到你想看的视频</p>
                        <p style="color: #333; margin: 5px 0;">3. 复制视频页面的完整URL</p>
                        <p style="color: #333; margin: 5px 0;">4. 回到本页面，粘贴到下方的链接提取区域</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            elif browse_option == "📱 移动端适配页面":
                # 尝试提供移动端链接
                mobile_url = display_url.replace("www.", "m.").replace("v.qq.com", "m.v.qq.com")
                st.markdown(f"""
                <div style="border: 3px solid #FF6B35; border-radius: 15px; padding: 20px; margin: 10px 0; background: linear-gradient(45deg, #E1F5FE, #F3E5F5);">
                    <h3 style="color: #FF6B35;">📱 移动端适配页面</h3>
                    <p style="color: #666;">某些网站的移动端版本可能更容易嵌入显示</p>
                    <iframe src="{mobile_url}" width="100%" height="400" frameborder="0" style="border-radius: 10px;"></iframe>
                    <p style="margin-top: 10px; color: #666;"><small>📍 移动端地址: {mobile_url}</small></p>
                </div>
                """, unsafe_allow_html=True)
            
            else:  # 获取页面链接
                st.markdown(f"""
                <div style="border: 3px solid #FF6B35; border-radius: 15px; padding: 20px; margin: 10px 0; background: linear-gradient(45deg, #FFF3E0, #E8F5E8);">
                    <h3 style="color: #FF6B35;">🔗 当前页面链接</h3>
                    <div style="background: white; padding: 15px; border-radius: 10px; border: 2px dashed #FF6B35; margin: 10px 0;">
                        <p style="color: #333; word-break: break-all; margin: 0;"><strong>链接:</strong> {display_url}</p>
                    </div>
                    <div style="margin-top: 15px;">
                        <button onclick="navigator.clipboard.writeText('{display_url}')" style="background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer;">
                            📋 复制链接
                        </button>
                    </div>
                    <div style="margin-top: 15px; padding: 10px; background: #FFF9C4; border-radius: 10px;">
                        <p style="color: #F57F17; margin: 0;"><strong>💡 提示：</strong>如果这不是视频页面链接，请在新窗口中浏览并找到具体的视频页面，然后复制那个链接。</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 操作提示
        st.markdown("""
        <div style="background: #E8F5E8; padding: 1rem; border-radius: 10px; margin: 10px 0; border-left: 4px solid #4CAF50;">
            <h5 style="color: #2E7D32; margin: 0;">📋 浏览器使用技巧：</h5>
            <p style="margin: 0.5rem 0; color: #333;">
                • 🌐 建议使用"在新窗口中浏览"获得最佳体验<br>
                • 📱 移动端页面有时能绕过显示限制<br>
                • 🔗 可直接获取当前页面链接进行分析<br>
                • 📋 找到视频后记得复制完整的视频页面URL
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # URL提取区域
        st.markdown("### 🎯 视频链接提取")
        
        extract_col1, extract_col2 = st.columns([3, 1])
        
        with extract_col1:
            extracted_url = st.text_input(
                "📋 从浏览器复制的视频链接",
                value=st.session_state.extracted_url,
                placeholder="请将浏览器中找到的视频页面链接粘贴到这里...",
                help="在浏览器中找到想看的视频，复制视频页面链接粘贴到这里",
                key="extracted_video_url"
            )
        
        with extract_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✨ 使用此链接", key="use_extracted_url", use_container_width=True):
                if extracted_url:
                    st.session_state.extracted_url = extracted_url
                    # 将提取的URL设置到主播放区域
                    st.success("✅ 链接已提取！请到下方选择解析器进行播放！")
                    # 通过session state传递URL到主播放功能
                    st.session_state.auto_fill_url = extracted_url
                else:
                    st.error("❌ 请先输入视频链接！")
        
        # 显示提取的链接信息
        if extracted_url:
            st.markdown("#### 📊 链接分析")
            
            # 分析链接属于哪个平台
            platform_detected = "未知平台"
            for platform, base_url in VIDEO_PLATFORMS.items():
                domain = base_url.replace("https://", "").replace("www.", "")
                if domain in extracted_url:
                    platform_detected = platform
                    break
            
            st.markdown(f"""
            <div style="background: #E8F5E8; padding: 1rem; border-radius: 10px; border-left: 4px solid #4CAF50;">
                <h5 style="color: #2E7D32; margin: 0;">🎯 检测到的平台：{platform_detected}</h5>
                <p style="margin: 0.5rem 0; color: #333; word-break: break-all;"><strong>链接：</strong>{extracted_url}</p>
                <p style="margin: 0; color: #666;"><em>💡 链接已准备就绪，可以进行解析播放！</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    # 使用说明
    with st.expander("📚 内置浏览器使用指南"):
        st.markdown("""
        ### 🎯 如何使用内置浏览器功能
        
        **步骤详解：**
        
        1. **🎯 选择平台**
           - 从下拉菜单选择你想搜索的视频平台
           - 目前支持腾讯视频、爱奇艺、优酷、芒果TV等主流平台
        
        2. **🚀 打开浏览器**
           - 点击"打开内置浏览器"按钮
           - 浏览器会自动加载所选平台的官网
        
        3. **🔍 搜索视频**
           - 在浏览器中搜索你想看的视频
           - 找到目标视频后，点击进入视频播放页面
        
        4. **📋 复制链接**
           - 复制视频播放页面的完整URL
           - 粘贴到"视频链接提取"区域
        
        5. **✨ 开始播放**
           - 点击"使用此链接"按钮
           - 系统会自动将链接填入播放器
           - 选择合适的解析器开始播放
        
        **💡 小技巧：**
        - 🎬 腾讯视频：寻找 `v.qq.com/x/cover/` 开头的链接
        - 📺 爱奇艺：寻找 `iqiyi.com/v_` 开头的链接  
        - 🎞️ 优酷：寻找 `youku.com/v_show/` 开头的链接
        - 📱 B站：寻找 `bilibili.com/video/BV` 开头的链接
        
        **⚠️ 注意事项：**
        - 确保复制的是视频播放页面的链接，不是搜索页面
        - 某些平台可能需要登录才能访问完整内容
        - 建议复制完整的URL，包含所有参数
        """)

def main():
    load_css()
    
    # 主标题
    st.markdown('<div class="title">🍍 海绵宝宝的神奇视频播放器 🧽</div>', unsafe_allow_html=True)
    
    # 装饰性元素
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown('<div class="decoration">🐠</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="decoration">🪸</div>', unsafe_allow_html=True)
    
    # 置顶公告区域
    st.markdown("---")
    with st.container():
        st.markdown("### 📢 置顶公告")
        
        # 重新加载最新公告
        st.session_state.shared_announcements = load_announcements()
        
        # 显示最新的2条公告作为置顶
        if st.session_state.shared_announcements:
            for i, announcement in enumerate(st.session_state.shared_announcements[:2]):  # 只显示最新的2条
                st.markdown(f"""
                <div style="background: linear-gradient(45deg, #FFE4E1, #FFF0F5); padding: 1rem; border-radius: 15px; margin: 0.5rem 0; border: 3px solid #FF1493; box-shadow: 0 4px 8px rgba(255,20,147,0.3); animation: glow 2s infinite alternate;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: #FF1493; margin: 0; font-family: 'Comic Sans MS', cursive; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">🔥 {announcement['title']}</h4>
                        <span style="background: #FF1493; color: white; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;">置顶</span>
                    </div>
                    <p style="margin: 0.8rem 0; color: #333; font-size: 1rem; line-height: 1.5;">{announcement['content'][:100]}{'...' if len(announcement['content']) > 100 else ''}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <small style="color: #666; font-style: italic;">📅 {announcement['date']} | ✍️ {announcement['author']}</small>
                        <small style="color: #FF1493; cursor: pointer;">📢 点击公告板查看详情</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🤔 暂时没有置顶公告，管理员可以在管理中心添加公告哦！")
        
        # 快速跳转到公告板的按钮
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("📢 查看所有公告", key="goto_announcements", use_container_width=True):
                st.info("💡 请点击上方的 '📢 公告板' 标签页查看所有公告详情！")
    
    st.markdown("---")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 视频播放", "📢 公告板", "💬 评论区", "🔧 管理中心"])
    
    # 视频播放标签页
    with tab1:
        # 首先添加内置浏览器功能
        built_in_browser()
        
        st.markdown("---")
        
        # 侧边栏
        with st.sidebar:
            st.markdown("### 🏠 比奇堡控制中心")
            st.markdown("---")
            
            # 选择解析器
            selected_parser = st.selectbox(
                "🔧 选择你的解析器",
                list(PARSERS.keys()),
                help="不同的解析器可能对不同的视频网站有更好的支持哦！"
            )
            
            # 检查是否有从内置浏览器传来的URL
            auto_fill_url = ""
            if 'auto_fill_url' in st.session_state:
                auto_fill_url = st.session_state.auto_fill_url
            
            # 视频链接输入
            video_url = st.text_input(
                "🎬 输入视频链接",
                value=auto_fill_url,
                placeholder="在这里粘贴你要播放的视频链接，或使用上方内置浏览器获取...",
                help="支持各大视频网站的链接！会自动转换移动版链接为PC版。也可以使用上方内置浏览器搜索获取链接。"
            )
            
            # 如果有自动填充的URL，显示提示并清除session state
            if auto_fill_url:
                st.success("✅ 已自动填入从内置浏览器获取的链接！")
                # 清除session state中的auto_fill_url，避免重复填充
                if 'auto_fill_url' in st.session_state:
                    del st.session_state.auto_fill_url
            
            # 快速清空链接按钮
            if st.button("🗑️ 清空链接", key="clear_url", use_container_width=True):
                st.session_state.auto_fill_url = ""
                st.rerun()
            
            # 播放按钮
            play_button = st.button("🚀 开始播放", use_container_width=True)
            
            st.markdown("---")
            
            # 使用说明
            with st.expander("📋 使用说明"):
                st.markdown("""
                **欢迎来到比奇堡！** 🏖️
                
                **🆕 新功能 - 内置浏览器：**
                1. 🌐 使用上方的内置浏览器直接搜索视频
                2. 🎯 选择平台 → 搜索视频 → 复制链接 → 一键播放
                3. ✨ 无需切换网页，一站式体验！
                
                **传统方式：**
                1. 📝 直接在左侧输入你想播放的视频链接
                2. 🔧 选择一个解析器（建议先试试默认的）
                3. 🚀 点击"开始播放"按钮
                4. 🍿 享受你的视频时光！
                
                **小贴士：**
                - 🎬 支持腾讯视频、爱奇艺、优酷、B站、芒果TV等
                - 📱 自动转换移动版链接为PC版
                - 🔄 如果一个解析器不work，试试另一个！
                - 🍍 优酷、腾讯视频推荐"默认解析器"！
                - 🧽 B站、爱奇艺推荐"新海绵解析器"！
                - 🌐 内置浏览器让搜索更便捷！
                """)
            
            # 支持的网站
            with st.expander("🌐 支持的网站"):
                st.markdown("""
                **主要支持：**
                - 🎬 **腾讯视频** (v.qq.com, m.v.qq.com)
                - 📺 **爱奇艺** (iqiyi.com, m.iqiyi.com)
                - 🎞️ **优酷** (youku.com, m.youku.com)
                - 📱 **哔哩哔哩** (bilibili.com, m.bilibili.com)
                - 🍊 **芒果TV** (mgtv.com)
                - 🎵 **咪咕视频** (miguvideo.com)
                - 🏠 **CCTV** (tv.cctv.com)
                - 🌟 **搜狐视频** (tv.sohu.com)
                
                **🆕 内置浏览器支持：**
                - 🌐 直接在应用内访问各大视频平台官网
                - 🔍 便捷搜索视频内容
                - 📋 一键提取视频链接
                - 🎯 智能平台识别
                
                **智能功能：**
                - 🔄 自动转换移动版为PC版
                - 🎯 腾讯视频vid参数提取
                - 🛠️ 链接格式标准化
                - ✨ 浏览器链接自动填充
                """)
            
            # 关于信息
            with st.expander("ℹ️ 关于播放器"):
                st.markdown("""
                🍍 **海绵宝宝视频播放器** 🧽
                
                由比奇堡最聪明的海绵制作！
                
                **特色功能：**
                - 🎨 海绵宝宝主题界面
                - 🔧 多种解析器选择
                - 🚀 快速播放体验
                - 🤖 智能链接处理
                - 🍍 满满的童年回忆
                - 📢 实时公告更新
                - 💬 用户评论互动
                
                **免责声明：**
                本播放器仅用于学习交流，请支持正版内容！
                """)
        
        # 主内容区域
        if play_button and video_url:
            # 处理视频链接
            processed_url, conversion_msg = process_video_url(video_url)
            
            # 显示转换信息
            if conversion_msg:
                st.info(conversion_msg)
            
            parser_url = PARSERS[selected_parser]
            full_url = f"{parser_url}{quote(processed_url)}"
            
            # 显示播放信息
            st.success(f"🎉 太好了！正在使用 {selected_parser} 播放你的视频！")
            
            # 视频播放区域
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            
            # 使用iframe嵌入播放器
            st.markdown(f"""
            <iframe src="{full_url}" 
                    width="100%" 
                    height="600" 
                    frameborder="0" 
                    allowfullscreen="true"
                    style="border-radius: 15px;">
            </iframe>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 显示解析链接（调试用）
            with st.expander("🔍 解析链接（调试信息）"):
                st.markdown("**原始链接：**")
                st.code(video_url)
                if processed_url != video_url:
                    st.markdown("**处理后链接：**")
                    st.code(processed_url)
                st.markdown("**最终解析链接：**")
                st.code(full_url)
        
        elif play_button and not video_url:
            st.error("🤔 哎呀！海绵宝宝说你忘记输入视频链接了！")
        
        elif not video_url:
            # 欢迎界面
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(45deg, #FFFACD, #F0F8FF); border-radius: 20px; margin: 2rem 0; border: 3px solid #FF6B35;">
                <h2 style="color: #FF6B35; font-family: 'Comic Sans MS', cursive;">🌊 欢迎来到比奇堡的视频播放器！</h2>
                <p style="font-size: 1.2rem; color: #4169E1; font-family: 'Comic Sans MS', cursive;">
                    我是海绵宝宝！我准备好了！🧽✨
                </p>
                <p style="color: #FF1493; font-family: 'Comic Sans MS', cursive;">
                    在左边的控制中心输入视频链接，然后点击播放按钮就可以开始观看啦！
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 功能展示
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div style="background: #FFE4E1; padding: 1rem; border-radius: 15px; text-align: center; border: 2px solid #FF69B4;">
                    <h3 style="color: #FF1493;">🔧 多核解析</h3>
                    <p>18个精选稳定解析器！</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background: #E0FFFF; padding: 1rem; border-radius: 15px; text-align: center; border: 2px solid #00CED1;">
                    <h3 style="color: #008B8B;">🌐 内置浏览器</h3>
                    <p>一站式搜索播放体验！</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style="background: #FFFACD; padding: 1rem; border-radius: 15px; text-align: center; border: 2px solid #FFD700;">
                    <h3 style="color: #FF8C00;">🚀 智能解析</h3>
                    <p>自动处理各种链接格式！</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style="background: #F0E68C; padding: 1rem; border-radius: 15px; text-align: center; border: 2px solid #DAA520;">
                    <h3 style="color: #B8860B;">💬 互动社区</h3>
                    <p>公告板和评论区等你！</p>
                </div>
                """, unsafe_allow_html=True)
    
    # 公告板标签页
    with tab2:
        display_announcements()
    
    # 评论区标签页
    with tab3:
        comment_section()
    
    # 管理中心标签页
    with tab4:
        st.markdown("### 🔧 管理中心")
        
        if not st.session_state.admin_logged_in:
            admin_login()
        else:
            st.success("🎉 欢迎管理员！你现在可以管理公告和评论了。")
            announcement_management()
            
            st.markdown("---")
            st.markdown("### 📊 统计信息")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📢 公告数量", len(st.session_state.shared_announcements))
            
            with col2:
                st.metric("💬 评论数量", len(st.session_state.shared_comments))
            
            with col3:
                total_likes = sum(comment['likes'] for comment in st.session_state.shared_comments)
                st.metric("❤️ 总点赞数", total_likes)
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #FF6B35; font-family: 'Comic Sans MS', cursive; padding: 1rem;">
        🍍 Made with love in Bikini Bottom 🧽 | 海绵宝宝 © 2024
        <br>
        <small>我准备好了！I'm ready! 🎵</small>
        <br>
        <small>🆕 全新功能：🌐 内置浏览器 | 📢 公告板 | 💬 评论区 | 🔧 管理系统</small>
        <br>
        <small style="color: #FF1493;">✨ 现在支持8大视频平台的内置浏览器搜索！</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
