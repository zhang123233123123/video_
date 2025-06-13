#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VIP视频解析测试脚本
专门测试您的腾讯视频链接解析功能
"""

import sys
import json
from enhanced_parser import EnhancedVIPParser

def test_tencent_video():
    """测试腾讯视频解析"""
    # 您提供的链接
    test_url = 'https://v.qq.com/x/cover/mcv8hkc8zk8lnov/m4101qychtr.html'
    
    print("🎬 VIP视频解析测试")
    print("=" * 60)
    print(f"📋 测试链接: {test_url}")
    print(f"🎯 目标视频: 《完美世界》")
    print("-" * 60)
    
    # 创建解析器
    parser = EnhancedVIPParser()
    
    # 1. 平台检测
    print("\n🔍 步骤1: 平台检测")
    platform_info = parser.detect_platform(test_url)
    if platform_info:
        print(f"✅ 检测成功: {platform_info['name']}")
    else:
        print("❌ 平台检测失败")
        return
    
    # 2. 视频解析
    print("\n📡 步骤2: 视频信息解析")
    result = parser.parse_video(test_url)
    
    if result['success']:
        print("✅ 解析成功!")
        print(f"   📺 标题: {result['title']}")
        print(f"   🏷️ 平台: {result['platform']}")
        print(f"   🆔 视频ID: {result.get('vid', 'N/A')}")
        print(f"   👑 VIP内容: {'是' if result.get('vip_content') else '否'}")
        
        # 3. 解析线路
        print(f"\n🔗 步骤3: 生成解析线路 ({len(result.get('parse_urls', []))} 个)")
        for i, parse_url in enumerate(result.get('parse_urls', []), 1):
            print(f"   {i}. {parse_url['name']}")
            print(f"      {parse_url['url']}")
            print()
        
        # 4. 推荐使用方式
        print("💡 使用建议:")
        print("   1. 复制上述任一解析链接")
        print("   2. 在浏览器中打开")
        print("   3. 如果无法播放，尝试其他线路")
        print("   4. 建议使用'高清稳定'或'快速解析'线路")
        
        return True
        
    else:
        print(f"❌ 解析失败: {result['error']}")
        return False

def test_multiple_platforms():
    """测试多个平台"""
    test_urls = [
        ('腾讯视频', 'https://v.qq.com/x/cover/mcv8hkc8zk8lnov/m4101qychtr.html'),
        ('爱奇艺', 'https://www.iqiyi.com/v_1kbyav4p5r4.html'),
        ('优酷', 'https://v.youku.com/v_show/id_XNTEzNjY4MjQ0OA==.html'),
    ]
    
    parser = EnhancedVIPParser()
    
    print("\n" + "=" * 60)
    print("🔄 多平台解析测试")
    print("=" * 60)
    
    for platform_name, url in test_urls:
        print(f"\n📱 测试 {platform_name}")
        print("-" * 30)
        
        result = parser.parse_video(url)
        
        if result['success']:
            print(f"✅ {result['title']}")
            print(f"   解析线路: {len(result.get('parse_urls', []))} 个")
        else:
            print(f"❌ {result['error']}")

if __name__ == "__main__":
    try:
        # 主要测试您的腾讯视频链接
        success = test_tencent_video()
        
        if success:
            print("\n🎉 测试完成！您的VIP视频解析器已就绪！")
            print("\n📝 下一步操作:")
            print("   1. 运行: streamlit run app.py")
            print("   2. 在浏览器中打开应用")
            print("   3. 输入视频链接进行解析")
            print("   4. 选择合适的解析线路观看")
        else:
            print("\n⚠️ 解析未完全成功，但这很正常")
            print("   VIP内容解析依赖第三方接口的可用性")
            print("   建议直接使用应用测试多个解析线路")
        
        # 可选：测试其他平台
        if len(sys.argv) > 1 and sys.argv[1] == '--all':
            test_multiple_platforms()
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        print("请检查网络连接和依赖包安装情况") 