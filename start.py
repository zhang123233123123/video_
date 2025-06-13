#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
海绵宝宝影视启动脚本
一键启动您的VIP视频解析器
"""

import os
import sys
import subprocess
import webbrowser
import time

def print_logo():
    """打印海绵宝宝影视LOGO"""
    logo = """
    🧽🌊🧽🌊🧽🌊🧽🌊🧽🌊🧽🌊🧽🌊🧽
    🌊                                       🌊
    🧽    欢迎使用 海绵宝宝影视 VIP解析器    🧽
    🌊                                       🌊
    🧽     比奇堡最强的视频解析工具！        🧽
    🌊                                       🌊
    🧽🌊🧽🌊🧽🌊🧽🌊🧽🌊🧽🌊🧽🌊🧽
    """
    print(logo)

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖包...")
    try:
        import streamlit
        import requests
        print("✅ 依赖包检查完成")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("正在安装依赖包...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖包安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败，请手动运行: pip install -r requirements.txt")
            return False

def start_app():
    """启动应用"""
    print("🚀 启动海绵宝宝影视...")
    
    # 启动streamlit应用
    try:
        # 在新的进程中启动streamlit
        env = os.environ.copy()
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.port", "8501",
            "--browser.serverAddress", "localhost"
        ], env=env)
        
        print("⏳ 等待应用启动...")
        time.sleep(3)
        
        # 自动打开浏览器
        url = "http://localhost:8501"
        print(f"🌐 应用地址: {url}")
        
        try:
            webbrowser.open(url)
            print("🎉 浏览器已自动打开！")
        except:
            print("⚠️ 无法自动打开浏览器，请手动访问上述地址")
        
        print("\n" + "="*50)
        print("🧽 海绵宝宝影视已启动！")
        print("📱 支持手机、电脑访问")
        print("🎬 支持腾讯视频、爱奇艺、优酷等平台")
        print("👑 专门解析VIP内容")
        print("🔄 按 Ctrl+C 停止服务")
        print("="*50)
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务...")
            process.terminate()
            print("👋 海绵宝宝影视已停止，下次再见！")
            
    except FileNotFoundError:
        print("❌ 找不到streamlit，请确保已安装: pip install streamlit")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

def main():
    """主函数"""
    print_logo()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查文件
    if not os.path.exists("app.py"):
        print("❌ 找不到app.py文件")
        return
    
    if not os.path.exists("enhanced_parser.py"):
        print("❌ 找不到enhanced_parser.py文件")
        return
    
    # 启动应用
    start_app()

if __name__ == "__main__":
    main() 