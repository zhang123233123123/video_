#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优酷视频解析修复版本
专门处理 v.youku.com/video?vid= 格式的链接
"""

import requests
import re
import json
import base64
from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional, Dict, Any

class YoukuFixer:
    """优酷解析修复器"""
    
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
        
        # 更新的第三方解析接口
        self.parse_apis = [
            'https://jx.xmflv.com/?url={}',
            'https://jx.618g.com/?url={}', 
            'https://api.bb3.buzz/jiexi/?url={}',
            'https://okjx.cc/?url={}',
            'https://jx.jsonplayer.com/player/?url={}',
            'https://jx.bozrc.com:4433/player/?url={}'
        ]
    
    def extract_youku_vid(self, url: str) -> Optional[str]:
        """提取优酷视频ID - 支持多种格式"""
        try:
            # 解析URL
            parsed = urlparse(url)
            
            # 方法1: 从URL参数中提取vid
            if 'vid' in parsed.query:
                params = parse_qs(parsed.query)
                if 'vid' in params and params['vid']:
                    vid = params['vid'][0]
                    print(f"从URL参数提取到vid: {vid}")
                    return vid
            
            # 方法2: 从路径中提取 /id_xxx.html 格式
            path_match = re.search(r'/id_([^.]+)\.html', url)
            if path_match:
                vid = path_match.group(1)
                print(f"从路径提取到vid: {vid}")
                return vid
            
            # 方法3: 从页面内容中提取
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    html = response.text
                    
                    # 多种正则表达式模式
                    patterns = [
                        r'videoId["\']?\s*:\s*["\']([^"\']+)["\']',
                        r'vid["\']?\s*:\s*["\']([^"\']+)["\']',
                        r'"vid"\s*:\s*"([^"]+)"',
                        r'data-vid="([^"]+)"',
                        r'showid[=:]([^&\s]+)'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, html)
                        if match:
                            vid = match.group(1)
                            print(f"从页面内容提取到vid: {vid}")
                            return vid
            except Exception as e:
                print(f"获取页面内容失败: {e}")
            
            return None
            
        except Exception as e:
            print(f"提取视频ID失败: {e}")
            return None
    
    def parse_youku_video(self, url: str) -> Dict[str, Any]:
        """解析优酷视频"""
        try:
            print(f"开始解析优酷视频: {url}")
            
            # 提取视频ID
            vid = self.extract_youku_vid(url)
            if not vid:
                return {
                    'success': False,
                    'error': '无法提取视频ID，请检查链接格式'
                }
            
            print(f"成功提取视频ID: {vid}")
            
            # 尝试获取视频标题
            title = self.get_video_title(url)
            
            # 生成解析链接
            parse_urls = []
            for i, api_template in enumerate(self.parse_apis, 1):
                parse_url = api_template.format(url)
                parse_urls.append({
                    'name': f'解析线路{i}',
                    'url': parse_url
                })
            
            return {
                'success': True,
                'title': title,
                'vid': vid,
                'original_url': url,
                'parse_urls': parse_urls,
                'best_parse_url': parse_urls[0]['url'] if parse_urls else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'优酷解析错误: {str(e)}'
            }
    
    def get_video_title(self, url: str) -> str:
        """获取视频标题"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                html = response.text
                
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    title = title_match.group(1).replace(' - 优酷视频', '').strip()
                    return title
                
                # 备用标题提取方法
                title_patterns = [
                    r'"title"\s*:\s*"([^"]+)"',
                    r'data-title="([^"]+)"',
                    r'<h1[^>]*>([^<]+)</h1>'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, html)
                    if match:
                        return match.group(1).strip()
                        
        except Exception as e:
            print(f"获取标题失败: {e}")
        
        return "优酷视频"
    
    def test_parse_api(self, api_url: str) -> Dict[str, Any]:
        """测试解析接口可用性"""
        try:
            response = requests.get(api_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text.lower()
                # 检查是否包含视频相关内容
                if any(keyword in content for keyword in ['video', 'mp4', 'iframe', 'player', 'src']):
                    return {
                        'success': True,
                        'status': '可用',
                        'response_time': response.elapsed.total_seconds()
                    }
                else:
                    return {
                        'success': False,
                        'status': '无视频内容',
                        'response_time': response.elapsed.total_seconds()
                    }
            else:
                return {
                    'success': False,
                    'status': f'HTTP {response.status_code}',
                    'response_time': response.elapsed.total_seconds()
                }
                
        except Exception as e:
            return {
                'success': False,
                'status': f'错误: {str(e)}',
                'response_time': 0
            }

def test_youku_link():
    """测试优酷链接解析"""
    fixer = YoukuFixer()
    
    # 测试链接
    test_url = "https://v.youku.com/video?vid=XNjQ4MzA5ODkwOA==&s=bdfb0949ae4c4ac39168&scm=20140719.apircmd.298496.video_XNjQ4MzA5ODkwOA==&spm=a2hkt.13141534.1_6.d_1_13"
    
    print("=" * 60)
    print("优酷视频解析测试")
    print("=" * 60)
    
    # 解析视频
    result = fixer.parse_youku_video(test_url)
    
    if result['success']:
        print(f"✅ 解析成功!")
        print(f"标题: {result['title']}")
        print(f"视频ID: {result['vid']}")
        print(f"原链接: {result['original_url']}")
        print("\n可用解析线路:")
        
        for i, parse_info in enumerate(result['parse_urls'], 1):
            print(f"{i}. {parse_info['name']}")
            print(f"   {parse_info['url']}")
            
            # 测试前3个接口
            if i <= 3:
                test_result = fixer.test_parse_api(parse_info['url'])
                if test_result['success']:
                    print(f"   ✅ 可用 (响应时间: {test_result['response_time']:.2f}s)")
                else:
                    print(f"   ❌ {test_result['status']}")
            print()
    else:
        print(f"❌ 解析失败: {result['error']}")

if __name__ == "__main__":
    test_youku_link() 