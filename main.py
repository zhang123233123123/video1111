import streamlit as st
import base64
import requests
from urllib.parse import quote, urlparse, parse_qs
import re
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="🍍 海绵宝宝视频播放器 🍍",
    page_icon="🍍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'announcements' not in st.session_state:
    st.session_state.announcements = [
        {
            'title': '🎉 欢迎使用海绵宝宝视频播放器！',
            'content': '这是一个全新的视频播放器，支持多种视频网站解析。我们会持续更新和改进功能！',
            'date': '2024-01-01',
            'author': '海绵宝宝'
        }
    ]

if 'comments' not in st.session_state:
    st.session_state.comments = []

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

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
                    st.session_state.announcements.insert(0, new_announcement)
                    st.success("✅ 公告发布成功！")
                    st.rerun()
                else:
                    st.error("请填写标题和内容！")
        
        with col2:
            if st.button("🚪 退出登录", key="admin_logout"):
                st.session_state.admin_logged_in = False
                st.success("👋 已退出登录")
                st.rerun()
    
    # 显示现有公告并允许删除
    st.markdown("### 📋 现有公告")
    for i, announcement in enumerate(st.session_state.announcements):
        with st.container():
            st.markdown(f"""
            <div style="background: #FFE4E1; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 5px solid #FF69B4;">
                <h4 style="color: #FF1493; margin: 0;">{announcement['title']}</h4>
                <p style="margin: 0.5rem 0; color: #333;">{announcement['content']}</p>
                <small style="color: #666;">发布时间: {announcement['date']} | 作者: {announcement['author']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️ 删除公告", key=f"delete_announcement_{i}"):
                st.session_state.announcements.pop(i)
                st.success("✅ 公告删除成功！")
                st.rerun()

# 公告显示功能
def display_announcements():
    """显示公告板"""
    st.markdown("### 📢 软件公告板")
    
    if not st.session_state.announcements:
        st.info("🤔 暂时没有公告呢~")
        return
    
    for announcement in st.session_state.announcements:
        st.markdown(f"""
        <div style="background: linear-gradient(45deg, #FFFACD, #F0F8FF); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border: 3px solid #FF6B35; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h3 style="color: #FF6B35; margin: 0; font-family: 'Comic Sans MS', cursive;">{announcement['title']}</h3>
            <p style="margin: 1rem 0; color: #333; font-size: 1.1rem; line-height: 1.6;">{announcement['content']}</p>
            <div style="text-align: right;">
                <small style="color: #666; font-style: italic;">📅 {announcement['date']} | ✍️ {announcement['author']}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 评论区功能
def comment_section():
    """评论区功能"""
    st.markdown("### 💬 用户评论区")
    
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
                    st.session_state.comments.insert(0, new_comment)
                    st.success("✅ 评论发表成功！")
                    st.rerun()
                else:
                    st.error("请填写昵称和评论内容！")
    
    st.markdown("---")
    
    # 显示评论
    st.markdown(f"#### 💭 所有评论 ({len(st.session_state.comments)})")
    
    if not st.session_state.comments:
        st.info("🤔 还没有评论，快来做第一个评论的人吧！")
        return
    
    for i, comment in enumerate(st.session_state.comments):
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
                    st.session_state.comments[i]['likes'] += 1
                    st.rerun()
            with col3:
                # 管理员可以删除评论
                if st.session_state.admin_logged_in:
                    if st.button("🗑️", key=f"delete_comment_{i}"):
                        st.session_state.comments.pop(i)
                        st.success("✅ 评论删除成功！")
                        st.rerun()

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
    "bibili解析器":"https://jx.playerjy.com/?url=",
    "备用1号线":"https://jx.nnxv.cn/tv.php?url="
}

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
        
        # 显示最新的2条公告作为置顶
        if st.session_state.announcements:
            for i, announcement in enumerate(st.session_state.announcements[:2]):  # 只显示最新的2条
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
            
            # 视频链接输入
            video_url = st.text_input(
                "🎬 输入视频链接",
                placeholder="在这里粘贴你要播放的视频链接...",
                help="支持各大视频网站的链接！会自动转换移动版链接为PC版。"
            )
            
            # 播放按钮
            play_button = st.button("🚀 开始播放", use_container_width=True)
            
            st.markdown("---")
            
            # 使用说明
            with st.expander("📋 使用说明"):
                st.markdown("""
                **欢迎来到比奇堡！** 🏖️
                
                1. 📝 在上方输入你想播放的视频链接
                2. 🔧 选择一个解析器（建议先试试默认的）
                3. 🚀 点击"开始播放"按钮
                4. 🍿 享受你的视频时光！
                
                **小贴士：**
                - 🎬 支持腾讯视频、爱奇艺、优酷、B站等
                - 📱 自动转换移动版链接为PC版
                             - 🔄 如果一个解析器不work，试试另一个！
                 - 🍍 优酷、腾讯视频推荐"默认解析器"！
                 - 🧽 B站、爱奇艺推荐"新海绵解析器"！
                """)
            
            # 支持的网站
            with st.expander("🌐 支持的网站"):
                st.markdown("""
                **主要支持：**
                - 🎬 **腾讯视频** (v.qq.com, m.v.qq.com)
                - 📺 **爱奇艺** (iqiyi.com, m.iqiyi.com)
                - 🎞️ **优酷** (youku.com, m.youku.com)
                - 📱 **哔哩哔哩** (bilibili.com, m.bilibili.com)
                - 🎵 **其他主流视频网站**
                
                **智能功能：**
                - 🔄 自动转换移动版为PC版
                - 🎯 腾讯视频vid参数提取
                - 🛠️ 链接格式标准化
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
                    <h3 style="color: #FF1493;">🔧 双核解析</h3>
                    <p>4个精选稳定解析器！</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="background: #E0FFFF; padding: 1rem; border-radius: 15px; text-align: center; border: 2px solid #00CED1;">
                    <h3 style="color: #008B8B;">🎨 海绵主题</h3>
                    <p>满满的比奇堡风格界面！</p>
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
                st.metric("📢 公告数量", len(st.session_state.announcements))
            
            with col2:
                st.metric("💬 评论数量", len(st.session_state.comments))
            
            with col3:
                total_likes = sum(comment['likes'] for comment in st.session_state.comments)
                st.metric("❤️ 总点赞数", total_likes)
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #FF6B35; font-family: 'Comic Sans MS', cursive; padding: 1rem;">
        🍍 Made with love in Bikini Bottom 🧽 | 海绵宝宝 © 2024
        <br>
        <small>我准备好了！I'm ready! 🎵</small>
        <br>
        <small>新功能：📢 公告板 | 💬 评论区 | 🔧 管理系统</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
