#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优酷视频首选解析器
使用 jx.xymp4.cc 作为首选解析接口
"""

import requests
import time
from urllib.parse import urlparse, parse_qs, quote
from typing import Dict, Any, Optional

class YoukuPreferredParser:
    """优酷首选解析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.youku.com/',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 首选解析器排序（用户验证可用的放在最前面）
        self.preferred_apis = [
            {
                'name': '🥇 优酷首选',
                'url': 'https://jx.xymp4.cc/?url={}',
                'priority': 1,
                'note': '用户验证可用'
            },
            {
                'name': '🥈 稳定解析',
                'url': 'https://www.8090g.cn/?url={}',
                'priority': 2,
                'note': '响应时间0.72秒'
            },
            {
                'name': '🥉 高清解析',
                'url': 'https://jx.m3u8.tv/jiexi/?url={}',
                'priority': 3,
                'note': '响应时间1.32秒'
            },
            {
                'name': '🏅 全网VIP',
                'url': 'https://www.yemu.xyz/?url={}',
                'priority': 4,
                'note': '响应时间1.54秒'
            },
            {
                'name': '⚡ 极速播放',
                'url': 'https://jx.xyflv.cc/?url={}',
                'priority': 5,
                'note': '响应时间1.61秒'
            }
        ]
    
    def extract_youku_info(self, url: str) -> Dict[str, Any]:
        """提取优酷视频信息"""
        try:
            parsed = urlparse(url)
            vid = ''
            title = '优酷视频'
            
            # 从URL参数提取vid
            if 'vid' in parsed.query:
                params = parse_qs(parsed.query)
                if 'vid' in params and params['vid']:
                    vid = params['vid'][0]
            
            # 获取视频标题
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    html = response.text
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', html)
                    if title_match:
                        title = title_match.group(1).replace(' - 优酷视频', '').strip()
            except:
                pass
            
            return {
                'success': True,
                'vid': vid,
                'title': title,
                'original_url': url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'提取信息失败: {str(e)}'
            }
    
    def get_preferred_parse_url(self, url: str) -> str:
        """获取首选解析链接"""
        encoded_url = quote(url, safe=':/?#[]@!$&\'()*+,;=')
        return self.preferred_apis[0]['url'].format(encoded_url)
    
    def get_all_parse_urls(self, url: str) -> list:
        """获取所有解析链接"""
        encoded_url = quote(url, safe=':/?#[]@!$&\'()*+,;=')
        
        parse_urls = []
        for api in self.preferred_apis:
            parse_url = api['url'].format(encoded_url)
            parse_urls.append({
                'name': api['name'],
                'url': parse_url,
                'priority': api['priority'],
                'note': api['note']
            })
        
        return parse_urls
    
    def parse_youku_video(self, url: str) -> Dict[str, Any]:
        """解析优酷视频（使用首选解析器）"""
        try:
            # 提取视频信息
            info = self.extract_youku_info(url)
            if not info['success']:
                return info
            
            # 生成解析链接
            parse_urls = self.get_all_parse_urls(url)
            preferred_url = self.get_preferred_parse_url(url)
            
            return {
                'success': True,
                'title': info['title'],
                'vid': info['vid'],
                'original_url': url,
                'preferred_parse_url': preferred_url,
                'all_parse_urls': parse_urls,
                'recommendation': '建议优先使用首选解析链接，经用户验证可用'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'解析失败: {str(e)}'
            }

def test_preferred_parser():
    """测试优酷首选解析器"""
    parser = YoukuPreferredParser()
    
    # 测试链接
    test_url = "https://v.youku.com/video?vid=XNjQ4MzA5ODkwOA==&s=bdfb0949ae4c4ac39168&scm=20140719.apircmd.298496.video_XNjQ4MzA5ODkwOA==&spm=a2hkt.13141534.1_6.d_1_13"
    
    print("=" * 80)
    print("🎬 优酷视频首选解析器测试")
    print("=" * 80)
    
    result = parser.parse_youku_video(test_url)
    
    if result['success']:
        print(f"✅ 解析成功!")
        print(f"📺 视频标题: {result['title']}")
        print(f"🆔 视频ID: {result['vid']}")
        print(f"🔗 原始链接: {result['original_url']}")
        print()
        
        print("🥇 **首选解析链接** (用户验证可用):")
        print(f"   {result['preferred_parse_url']}")
        print()
        
        print("📋 所有可用解析线路:")
        for i, parse_info in enumerate(result['all_parse_urls'], 1):
            print(f"{i}. {parse_info['name']}")
            print(f"   链接: {parse_info['url']}")
            print(f"   说明: {parse_info['note']}")
            print()
        
        print(f"💡 {result['recommendation']}")
        
    else:
        print(f"❌ 解析失败: {result['error']}")

if __name__ == "__main__":
    test_preferred_parser() 