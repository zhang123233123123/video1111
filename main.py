import streamlit as st
import base64
import requests
from urllib.parse import quote
import re

# 设置页面配置
st.set_page_config(
    page_title="🍍 海绵宝宝视频播放器 🍍",
    page_icon="🍍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div > div {
        border: 3px solid #FF6B35;
        border-radius: 15px;
        background: #FFFACD;
        font-family: 'Comic Sans MS', cursive;
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
    
    /* 提示框样式 */
    .stAlert {
        border-radius: 15px;
        border: 2px solid #FF6B35;
        font-family: 'Comic Sans MS', cursive;
    }
    </style>
    """, unsafe_allow_html=True)

# 解析器配置
PARSERS = {
    "🍍 默认解析器": "https://jx.xymp4.cc/?url=",
    "🧽 海绵解析器": "https://parse.ikunfei.top/parse/?url=",
    "⭐ 派大星解析器": "https://jx.jsonplayer.com/player/?url=",
    "🦀 蟹老板解析器": "https://jx.bozrc.com:4433/player/?url=",
    "🏠 比奇堡解析器": "https://jx.m3u8.tv/jiexi/?url=",
    "🎵 章鱼哥解析器": "https://jx.parwix.com:4433/player/?url=",
    "🔥 火焰解析器": "https://jx.blbo.cc:4433/?url=",
    "🌊 海洋解析器": "https://jx.playerjy.com/?url="
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
            help="支持各大视频网站的链接！"
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
            - 如果一个解析器不work，试试其他的！
            - 海绵宝宝推荐使用"海绵解析器"！
            - 记得检查视频链接是否正确哦！
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
            - 🍍 满满的童年回忆
            
            **免责声明：**
            本播放器仅用于学习交流，请支持正版内容！
            """)
    
    # 主内容区域
    if play_button and video_url:
        parser_url = PARSERS[selected_parser]
        full_url = f"{parser_url}{quote(video_url)}"
        
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: #FFE4E1; padding: 1rem; border-radius: 15px; text-align: center; border: 2px solid #FF69B4;">
                <h3 style="color: #FF1493;">🔧 多解析器</h3>
                <p>8个不同的解析器供你选择！</p>
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
                <h3 style="color: #FF8C00;">🚀 快速播放</h3>
                <p>输入链接即可快速播放！</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #FF6B35; font-family: 'Comic Sans MS', cursive; padding: 1rem;">
        🍍 Made with love in Bikini Bottom 🧽 | 海绵宝宝 © 2024
        <br>
        <small>我准备好了！I'm ready! 🎵</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 