#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
强化版VIP视频解析器
专门用于解析VIP视频内容，包含多个备用解析接口
"""

import requests
import re
import json
import random
import time
from urllib.parse import urlparse, parse_qs, unquote, quote
from typing import Optional, Dict, Any, List
import base64

class EnhancedVIPParser:
    """强化版VIP视频解析器"""
    
    def __init__(self):
        # 多个用户代理，随机轮换避免被识别
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # 真实可用的第三方解析接口（按优先级排序）
        self.parse_apis = [
            {
                'name': '线路1-高清稳定',
                'url': 'https://jx.xmflv.com/?url={}',
                'type': 'iframe'
            },
            {
                'name': '线路2-快速解析',  
                'url': 'https://api.bb3.buzz/jiexi/?url={}',
                'type': 'iframe'
            },
            {
                'name': '线路3-通用解析',
                'url': 'https://jx.618g.com/?url={}',
                'type': 'iframe'
            },
            {
                'name': '线路4-备用解析',
                'url': 'https://okjx.cc/?url={}',
                'type': 'iframe'
            },
            {
                'name': '线路5-VIP专用',
                'url': 'https://www.1717yun.com/jx/ty.php?url={}',
                'type': 'iframe'
            },
            {
                'name': '线路6-无广告',
                'url': 'https://vip.gaotian.love/api/?key=8CNrwNGWumgOHNK5r3H7jsDJb1XhPp&url={}',
                'type': 'iframe'
            },
            {
                'name': '线路7-超清画质',
                'url': 'https://jx.jsonplayer.com/player/?url={}',
                'type': 'iframe'
            },
            {
                'name': '线路8-极速播放',
                'url': 'https://jx.bozrc.com:4433/player/?url={}',
                'type': 'iframe'
            }
        ]
        
        # 支持的视频平台
        self.platforms = {
            'v.qq.com': {
                'name': '腾讯视频',
                'parser': self._parse_tencent,
                'patterns': [r'v\.qq\.com', r'video\.qq\.com']
            },
            'iqiyi.com': {
                'name': '爱奇艺',
                'parser': self._parse_iqiyi,
                'patterns': [r'iqiyi\.com', r'www\.iqiyi\.com']
            },
            'youku.com': {
                'name': '优酷',
                'parser': self._parse_youku,
                'patterns': [r'youku\.com', r'v\.youku\.com']
            },
            'bilibili.com': {
                'name': 'B站',
                'parser': self._parse_bilibili,
                'patterns': [r'bilibili\.com', r'www\.bilibili\.com']
            },
            'mgtv.com': {
                'name': '芒果TV',
                'parser': self._parse_mgtv,
                'patterns': [r'mgtv\.com', r'www\.mgtv\.com']
            }
        }
        
        # 请求会话，保持连接
        self.session = requests.Session()
        
    def get_random_headers(self) -> Dict[str, str]:
        """获取随机请求头"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def detect_platform(self, url: str) -> Optional[Dict[str, Any]]:
        """检测视频平台"""
        for platform_key, platform_config in self.platforms.items():
            for pattern in platform_config['patterns']:
                if re.search(pattern, url):
                    return {
                        'key': platform_key,
                        'name': platform_config['name'],
                        'parser': platform_config['parser']
                    }
        return None
    
    def test_parse_api(self, api_config: Dict[str, str], test_url: str) -> Dict[str, Any]:
        """测试解析接口可用性"""
        try:
            parse_url = api_config['url'].format(quote(test_url, safe=':/?#[]@!$&\'()*+,;='))
            headers = self.get_random_headers()
            
            response = self.session.get(parse_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 简单检测是否包含视频相关内容
                content = response.text.lower()
                if any(keyword in content for keyword in ['video', 'mp4', 'iframe', 'player']):
                    return {
                        'available': True,
                        'response_time': response.elapsed.total_seconds(),
                        'url': parse_url
                    }
            
            return {
                'available': False,
                'error': f'状态码: {response.status_code}',
                'url': parse_url
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'url': api_config['url'].format(test_url)
            }
    
    def get_all_parse_urls(self, original_url: str) -> List[Dict[str, str]]:
        """获取所有解析接口的URL"""
        encoded_url = quote(original_url, safe=':/?#[]@!$&\'()*+,;=')
        
        parse_urls = []
        for api in self.parse_apis:
            parse_url = api['url'].format(encoded_url)
            parse_urls.append({
                'name': api['name'],
                'url': parse_url,
                'type': api['type']
            })
        
        return parse_urls
    
    def parse_video(self, url: str) -> Dict[str, Any]:
        """解析视频信息"""
        platform_info = self.detect_platform(url)
        
        if not platform_info:
            return {
                'success': False,
                'error': '不支持的视频平台'
            }
        
        try:
            # 调用对应平台的解析函数
            result = platform_info['parser'](url)
            result['platform'] = platform_info['name']
            
            # 添加所有可用的解析链接
            if result['success']:
                result['parse_urls'] = self.get_all_parse_urls(url)
                result['best_parse_url'] = result['parse_urls'][0]['url'] if result['parse_urls'] else None
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'解析失败: {str(e)}'
            }
    
    def _parse_tencent(self, url: str) -> Dict[str, Any]:
        """解析腾讯视频（增强版）"""
        try:
            # 多种方式提取视频ID
            vid = None
            title = '腾讯视频'
            
            # 方式1: 从URL直接提取
            patterns = [
                r'vid=([a-zA-Z0-9]+)',
                r'/([a-zA-Z0-9]+)\.html',
                r'/cover/[^/]+/([a-zA-Z0-9]+)\.html'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    vid = match.group(1)
                    break
            
            # 方式2: 从页面HTML提取
            if not vid:
                try:
                    headers = self.get_random_headers()
                    response = self.session.get(url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        html = response.text
                        
                        # 提取标题
                        title_match = re.search(r'<title>(.*?)</title>', html)
                        if title_match:
                            title = title_match.group(1).replace(' - 腾讯视频', '').strip()
                        
                        # 提取vid
                        vid_patterns = [
                            r'"vid"\s*:\s*"([^"]+)"',
                            r'vid=([a-zA-Z0-9]+)',
                            r'data-vid="([^"]+)"',
                            r'"id"\s*:\s*"([^"]+)"'
                        ]
                        
                        for pattern in vid_patterns:
                            match = re.search(pattern, html)
                            if match:
                                vid = match.group(1)
                                break
                except:
                    pass
            
            if not vid:
                return {
                    'success': False,
                    'error': '无法提取视频ID，请检查链接是否正确'
                }
            
            return {
                'success': True,
                'title': title,
                'duration': '未知',
                'thumbnail': '',
                'vid': vid,
                'original_url': url,
                'vip_content': True  # 标记为VIP内容
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'腾讯视频解析错误: {str(e)}'
            }
    
    def _parse_iqiyi(self, url: str) -> Dict[str, Any]:
        """解析爱奇艺视频（增强版）"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=10)
            
            title = '爱奇艺视频'
            vid = ''
            
            if response.status_code == 200:
                html = response.text
                
                # 提取标题
                title_patterns = [
                    r'<title>(.*?)</title>',
                    r'"albumName"\s*:\s*"([^"]+)"',
                    r'data-share-title="([^"]+)"'
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, html)
                    if match:
                        title = match.group(1).replace(' - 爱奇艺', '').strip()
                        break
                
                # 提取视频ID
                vid_patterns = [
                    r'data-player-videoid="([^"]+)"',
                    r'"vid"\s*:\s*"([^"]+)"',
                    r'albumId[=:](\d+)',
                    r'"tvId"\s*:\s*(\d+)'
                ]
                
                for pattern in vid_patterns:
                    match = re.search(pattern, html)
                    if match:
                        vid = match.group(1)
                        break
            
            return {
                'success': True,
                'title': title,
                'duration': '未知',
                'thumbnail': '',
                'vid': vid,
                'original_url': url,
                'vip_content': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'爱奇艺解析错误: {str(e)}'
            }
    
    def _parse_youku(self, url: str) -> Dict[str, Any]:
        """解析优酷视频（增强版）"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=10)
            
            title = '优酷视频'
            vid = ''
            
            if response.status_code == 200:
                html = response.text
                
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    title = title_match.group(1).replace(' - 优酷视频', '').strip()
                
                # 提取视频ID
                vid_patterns = [
                    r'videoId["\']?\s*:\s*["\']([^"\']+)["\']',
                    r'vid["\']?\s*:\s*["\']([^"\']+)["\']',
                    r'/id_([^.]+)\.html'
                ]
                
                for pattern in vid_patterns:
                    match = re.search(pattern, html)
                    if match:
                        vid = match.group(1)
                        break
            
            return {
                'success': True,
                'title': title,
                'duration': '未知',
                'thumbnail': '',
                'vid': vid,
                'original_url': url,
                'vip_content': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'优酷解析错误: {str(e)}'
            }
    
    def _parse_bilibili(self, url: str) -> Dict[str, Any]:
        """解析B站视频（增强版）"""
        try:
            # B站相对开放，但也有部分VIP内容
            bv_match = re.search(r'BV([a-zA-Z0-9]+)', url)
            av_match = re.search(r'av(\d+)', url)
            
            if bv_match:
                bvid = 'BV' + bv_match.group(1)
                api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
            elif av_match:
                aid = av_match.group(1)
                api_url = f'https://api.bilibili.com/x/web-interface/view?aid={aid}'
            else:
                return {
                    'success': False,
                    'error': '无法提取B站视频ID'
                }
            
            headers = self.get_random_headers()
            response = self.session.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 0:
                    video_info = data['data']
                    
                    return {
                        'success': True,
                        'title': video_info.get('title', 'B站视频'),
                        'duration': self._format_duration(video_info.get('duration', 0)),
                        'thumbnail': video_info.get('pic', ''),
                        'vid': video_info.get('bvid', video_info.get('aid', '')),
                        'original_url': url,
                        'vip_content': False  # B站大部分内容免费
                    }
            
            return {
                'success': False,
                'error': 'B站API调用失败'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'B站解析错误: {str(e)}'
            }
    
    def _parse_mgtv(self, url: str) -> Dict[str, Any]:
        """解析芒果TV（增强版）"""
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=10)
            
            title = '芒果TV'
            vid = ''
            
            if response.status_code == 200:
                html = response.text
                
                # 提取标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    title = title_match.group(1).replace(' - 芒果TV', '').strip()
                
                # 提取视频ID
                vid_patterns = [
                    r'"vid"\s*:\s*"([^"]+)"',
                    r'vid=([^&]+)',
                    r'/b/\d+/(\d+)\.html'
                ]
                
                for pattern in vid_patterns:
                    match = re.search(pattern, html)
                    if match:
                        vid = match.group(1)
                        break
            
            return {
                'success': True,
                'title': title,
                'duration': '未知',
                'thumbnail': '',
                'vid': vid,
                'original_url': url,
                'vip_content': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'芒果TV解析错误: {str(e)}'
            }
    
    def _format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if seconds == 0:
            return "未知"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return [config['name'] for config in self.platforms.values()]
    
    def get_parse_apis_info(self) -> List[Dict[str, str]]:
        """获取解析接口信息"""
        return [
            {
                'name': api['name'],
                'url': api['url'].replace('{}', '[视频链接]'),
                'type': api['type']
            }
            for api in self.parse_apis
        ] 