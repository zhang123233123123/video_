#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频解析调试工具
用于测试和调试视频解析功能
"""

import sys
import json
from video_parser import VideoParser

def test_url_parsing():
    """测试URL解析功能"""
    test_urls = [
        'https://v.qq.com/x/cover/mcv8hkc8zk8lnov/m4101qychtr.html',
        'https://www.iqiyi.com/v_1fbzh2w5p54.html',
        'https://v.youku.com/v_show/id_XNTkxNjcwMjg0OA==.html',
        'https://www.bilibili.com/video/BV1xx411c7mD',
        'https://www.mgtv.com/b/332759/3567533.html'
    ]
    
    parser = VideoParser()
    
    print("🎬 视频解析测试")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. 测试链接: {url}")
        print("-" * 40)
        
        # 检测平台
        platform_info = parser.detect_platform(url)
        if platform_info:
            print(f"✅ 平台检测: {platform_info['name']}")
        else:
            print("❌ 平台检测: 不支持的平台")
            continue
        
        # 解析视频
        result = parser.parse_video(url)
        
        if result['success']:
            print("✅ 解析成功:")
            print(f"   标题: {result['title']}")
            print(f"   时长: {result['duration']}")
            print(f"   平台: {result['platform']}")
            print(f"   视频ID: {result.get('vid', 'N/A')}")
            print(f"   播放URL: {result.get('play_url', 'N/A')}")
        else:
            print(f"❌ 解析失败: {result['error']}")

def test_specific_url(url: str):
    """测试特定URL"""
    parser = VideoParser()
    
    print(f"🎯 测试特定链接: {url}")
    print("=" * 50)
    
    # 检测平台
    platform_info = parser.detect_platform(url)
    if platform_info:
        print(f"✅ 平台检测: {platform_info['name']}")
        
        # 解析视频
        result = parser.parse_video(url)
        
        print("\n📋 详细解析结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result['success']:
            print(f"\n🎬 播放链接: {result.get('play_url', 'N/A')}")
        
    else:
        print("❌ 不支持的平台")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 测试命令行提供的URL
        test_url = sys.argv[1]
        test_specific_url(test_url)
    else:
        # 运行所有测试
        test_url_parsing()
        
        # 专门测试用户提供的链接
        print("\n" + "=" * 60)
        print("🎯 测试用户提供的腾讯视频链接")
        test_specific_url('https://v.qq.com/x/cover/mcv8hkc8zk8lnov/m4101qychtr.html') 