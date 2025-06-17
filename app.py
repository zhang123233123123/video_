import streamlit as st
import requests
import re
import json
from urllib.parse import urlparse, parse_qs
import base64
from typing import Optional, Dict, Any
from enhanced_parser import EnhancedVIPParser

# 页面配置
st.set_page_config(
    page_title="海绵宝宝影视",
    page_icon="🧽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 简洁黑白主题样式
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background-color: white;
        color: black;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: white;
        color: black;
        border: 2px solid black;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .video-container {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        background: white;
        border: 1px solid #ddd;
    }
    
    .control-panel {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border: 1px solid #ddd;
    }
    
    .warning-box {
        background: white;
        border: 2px solid black;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: black;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* 侧边栏 */
    .css-1d391kg {
        background-color: white;
    }
    
    .stSelectbox > div > div {
        background: white;
        border: 1px solid black;
        border-radius: 4px;
        color: black;
    }
    
    .stButton > button {
        background: white;
        color: black;
        border-radius: 6px;
        border: 1px solid black;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        font-weight: normal;
    }
    
    .stButton > button:hover {
        background: #f8f9fa;
        border: 1px solid black;
        transform: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    
    .route-info {
        background: white;
        padding: 0.8rem;
        border-radius: 6px;
        border: 1px solid black;
        margin: 0.5rem 0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        color: black;
    }
    
    /* 文本颜色 */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        background: white;
        color: black;
        border: 1px solid black;
        border-radius: 4px;
    }
    
    /* 信息框样式 */
    .stInfo, .stSuccess, .stWarning, .stError {
        background: white;
        border: 1px solid black;
        color: black;
    }
    
    /* 展开器样式 */
    .streamlit-expanderHeader {
        background: white;
        color: black;
        border: 1px solid black;
    }
    
    /* 代码框样式 */
    .stCode {
        background: #f8f9fa;
        color: black;
        border: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# VideoParser类已移到video_parser.py模块中

def main():
    """主函数"""
    
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>海绵宝宝影视</h1>
        <p>支持腾讯视频、爱奇艺、优酷等主流平台的VIP内容解析</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 警告提示
    st.markdown("""
    <div class="warning-box">
        <strong>重要提醒：</strong><br>
        • 本工具仅供学习和研究使用<br>
        • 请尊重版权，支持正版内容<br>
        • 用户需承担使用风险和法律责任
    </div>
    """, unsafe_allow_html=True)
    
    # 创建强化版解析器实例
    parser = EnhancedVIPParser()
    
    # 侧边栏设置（简化版）
    with st.sidebar:
        # 简洁主题侧边栏
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: white; 
                    border: 2px solid black; border-radius: 8px; margin-bottom: 1rem;">
            <h2 style="color: black; margin: 0.5rem 0;">海绵宝宝影视</h2>
            <p style="color: black; margin: 0; font-size: 0.9rem;">简洁高效的视频解析</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 支持的平台
        st.header("支持平台")
        platforms = parser.get_supported_platforms()
        for i, platform in enumerate(platforms):
            if platform == "优酷":
                st.write(f"• {platform} 🎯 (专线)")
            else:
                st.write(f"• {platform}")
        
        st.markdown("---")
        
        # 优酷专线信息
        st.header("🚀 优酷专线")
        st.markdown("""
        <div style="background: #e8f5e8; padding: 0.8rem; border-radius: 6px; 
                    border: 1px solid #4CAF50; margin: 0.5rem 0;">
            <strong style="color: #2E7D32;">优酷专线特色</strong><br>
            <small style="color: #388E3C;">
            • 专门优化的解析算法<br>
            • 6条优酷专用线路<br>
            • 更高的解析成功率<br>
            • 支持优酷VIP内容
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 解析线路信息
        st.header("解析线路")
        api_info = parser.get_parse_apis_info()
        
        # 分类显示解析线路
        youku_apis = [api for api in api_info if '优酷专线' in api['name']]
        general_apis = [api for api in api_info if '优酷专线' not in api['name']]
        
        # 优酷专线
        if youku_apis:
            st.markdown("**优酷专线：**")
            for i, api in enumerate(youku_apis[:3], 1):  # 显示前3个优酷专线
                st.markdown(f"""
                <div class="route-info" style="border-color: #4CAF50;">
                    <strong>专线{i}</strong><br>
                    <small>{api['name']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # 通用线路
        st.markdown("**通用线路：**")
        for i, api in enumerate(general_apis[:3], 1):  # 显示前3个通用线路
            st.markdown(f"""
            <div class="route-info">
                <strong>线路{i}</strong><br>
                <small>{api['name']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        total_apis = len(youku_apis) + len(general_apis)
        if total_apis > 6:
            st.info(f"还有 {total_apis - 6} 个备用线路")
        
        st.markdown("---")
        
        # 使用提示
        st.header("使用小贴士")
        st.markdown("""
        <div style="background: white; padding: 0.8rem; border-radius: 6px; 
                    border: 1px solid black; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);">
            <small style="color: black;">
            <strong>线路选择</strong><br>
            • 推荐使用高清稳定线路<br>
            • 卡顿时切换其他线路<br><br>
            
            <strong>播放技巧</strong><br>
            • 支持全屏播放<br>
            • 可复制链接到浏览器<br>
            • 手机端同样适用
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    # 主内容区
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("视频链接输入")
        
        # 视频链接输入
        video_url = st.text_input(
            "请输入视频链接",
            placeholder="https://v.qq.com/x/cover/...",
            help="支持腾讯视频、爱奇艺、优酷等平台链接"
        )
        
        # 解析按钮
        if st.button("解析视频", type="primary"):
            if video_url:
                with st.spinner("正在解析视频..."):
                    try:
                        # 显示解析步骤
                        st.info("正在检测视频平台...")
                        platform_info = parser.detect_platform(video_url)
                        
                        if platform_info:
                            st.success(f"检测到平台：{platform_info['name']}")
                            
                            st.info("正在解析视频信息...")
                            # 解析视频信息
                            result = parser.parse_video(video_url)
                        else:
                            st.error("不支持的视频平台，请检查链接格式")
                            return
                        
                        if result['success']:
                            # 保存到解析记录
                            if 'parse_history' not in st.session_state:
                                st.session_state.parse_history = []
                            st.session_state.parse_history.append(result['title'])
                            
                            # 显示视频信息
                            st.subheader("视频信息")
                            st.write(f"**标题：** {result['title']}")
                            st.write(f"**平台：** {result['platform']}")
                            st.write(f"**时长：** {result['duration']}")
                            
                            if result.get('thumbnail'):
                                st.image(result['thumbnail'], width=300)
                            
                            # 视频播放区域
                            st.subheader("VIP视频播放")
                            
                            # 显示VIP标识和专线信息
                            if result.get('vip_content'):
                                if result.get('platform_special') == '优酷专线':
                                    st.success("🎯 检测到优酷视频，正在使用优酷专线解析！")
                                    st.info("优酷专线采用专门优化的解析算法，解析成功率更高")
                                else:
                                    st.info("检测到VIP内容，正在使用解析服务")
                            
                            # 解析线路选择
                            if result.get('parse_urls'):
                                if result.get('platform_special') == '优酷专线':
                                    st.subheader("🚀 优酷专线解析 - 选择线路")
                                else:
                                    st.subheader("选择解析线路")
                                
                                # 初始化session state
                                if 'selected_route_index' not in st.session_state:
                                    st.session_state.selected_route_index = 0
                                
                                # 线路选择（使用唯一key防止重载）
                                parse_options = [f"{i+1}. {url['name']}" for i, url in enumerate(result['parse_urls'])]
                                selected_index = st.selectbox(
                                    "选择播放线路（如果当前线路无法播放，请尝试其他线路）",
                                    range(len(parse_options)),
                                    format_func=lambda x: parse_options[x],
                                    index=st.session_state.selected_route_index,
                                    key=f"route_selector_{hash(video_url)}"
                                )
                                
                                # 更新session state
                                st.session_state.selected_route_index = selected_index
                                selected_parse_url = result['parse_urls'][selected_index]['url']
                                
                                # 显示播放器
                                video_html = f"""
                                <div class="video-container">
                                    <iframe 
                                        src="{selected_parse_url}" 
                                        width="100%" 
                                        height="450" 
                                        frameborder="0" 
                                        allowfullscreen
                                        style="border-radius: 10px;"
                                        allow="autoplay; fullscreen"
                                    >
                                    </iframe>
                                </div>
                                """
                                
                                st.markdown(video_html, unsafe_allow_html=True)
                                
                                # 显示当前使用的解析接口（简洁风格）
                                st.markdown(f"""
                                <div class="route-info" style="text-align: center;">
                                    <strong>当前线路: {result['parse_urls'][selected_index]['name']}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 快速切换按钮
                                st.markdown("### 快速切换线路")
                                cols = st.columns(min(4, len(result['parse_urls'])))
                                for i, parse_url in enumerate(result['parse_urls'][:4]):
                                    with cols[i]:
                                        if st.button(f"线路{i+1}", key=f"quick_switch_{i}"):
                                            st.session_state.selected_route_index = i
                                            st.rerun()
                                
                                # 备用链接
                                with st.expander("查看所有解析链接"):
                                    for i, parse_url in enumerate(result['parse_urls']):
                                        status = "当前使用" if i == selected_index else "备用"
                                        st.markdown(f"""
                                        <div style="background: white; 
                                                    padding: 0.8rem; margin: 0.5rem 0; border-radius: 6px; 
                                                    border: 2px solid {'black' if i == selected_index else '#ddd'};">
                                            <strong>{parse_url['name']}</strong> - {status}<br>
                                            <code style="background: #f8f9fa; padding: 0.2rem; border-radius: 4px; font-size: 0.8em; color: black;">
                                                {parse_url['url'][:60]}...
                                            </code>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.warning("无法获取解析链接，请检查视频链接是否正确")
                            
# 播放控制已集成到线路选择中
                                
                        else:
                            st.error(f"解析失败：{result['error']}")
                            
                    except Exception as e:
                        st.error(f"解析失败：{str(e)}")
            else:
                st.warning("请输入视频链接")
    
    with col2:
        # 简洁主题的使用说明
        st.markdown("""
        <div style="background: white; 
                    padding: 1.5rem; border-radius: 8px; border: 2px solid black; 
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); margin-bottom: 1rem;">
            <h2 style="color: black; text-align: center; margin-bottom: 1rem;">使用指南</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 如何使用
        1. **复制视频链接**
           - 从腾讯视频、爱奇艺等平台复制链接
        2. **粘贴到输入框**
           - 输入完整的视频页面地址
        3. **点击解析按钮**
           - 系统将自动识别平台并解析
        4. **选择播放线路**
           - 多个线路供您选择
        5. **开始观看**
           - 支持全屏、倍速播放
        
        ### 特色功能
        • **多线路解析** - 8条备用线路
        • **VIP内容支持** - 专门解析VIP视频
        • **快速切换** - 一键切换播放线路
        • **响应式设计** - 手机电脑都适用
        • **智能重试** - 自动尝试最佳线路
        
        ### 海绵宝宝影视优势
        • **比奇堡最强** - 专业VIP解析
        • **稳定可靠** - 多重备用保障
        • **简单易用** - 一键式操作
        • **界面简洁** - 简洁黑白主题
        """)
        
        # 最近解析记录（简洁风格）
        st.markdown("""
        <div style="background: white; 
                    padding: 1rem; border-radius: 6px; border: 2px solid black; 
                    margin-top: 1rem;">
            <h3 style="color: black; margin-bottom: 0.5rem;">最近解析</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if 'parse_history' not in st.session_state:
            st.session_state.parse_history = []
        
        if st.session_state.parse_history:
            for i, record in enumerate(st.session_state.parse_history[-5:], 1):
                st.markdown(f"""
                <div style="background: white; 
                            padding: 0.5rem; margin: 0.3rem 0; border-radius: 4px; 
                            border-left: 4px solid black;">
                    <small style="color: black;"><strong>{i}.</strong> {record}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem; color: black; font-style: italic;">
                还没有解析记录哦～<br>
                快来试试解析你喜欢的视频吧！
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
