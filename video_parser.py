import requests
import re
import json
from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional, Dict, Any, List
import base64
import time

class VideoParser:
    """视频解析器主类"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 支持的视频平台配置
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
        
        # 第三方解析接口（示例）
        self.parse_apis = [
            'https://api.web.api.com/jx/',
            'https://api.xty.com/jx/',
            'https://api.vip.com/jx/'
        ]
    
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
            return result
        except Exception as e:
            return {
                'success': False,
                'error': f'解析失败: {str(e)}'
            }
    
    def _parse_tencent(self, url: str) -> Dict[str, Any]:
        """解析腾讯视频"""
        try:
            # 提取视频ID - 支持多种链接格式
            vid_match = re.search(r'vid=([a-zA-Z0-9]+)', url)
            if not vid_match:
                # 从链接末尾提取ID，如 /m4101qychtr.html
                vid_match = re.search(r'/([a-zA-Z0-9]+)\.html', url)
            if not vid_match:
                # 从cover链接提取ID，如 /cover/mcv8hkc8zk8lnov/m4101qychtr.html
                vid_match = re.search(r'/cover/[^/]+/([a-zA-Z0-9]+)\.html', url)
            if not vid_match:
                # 尝试获取页面内容来提取vid
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        html = response.text
                        # 从页面中提取vid
                        vid_match = re.search(r'"vid"\s*:\s*"([^"]+)"', html)
                        if not vid_match:
                            vid_match = re.search(r'vid=([a-zA-Z0-9]+)', html)
                except:
                    pass
            
            if not vid_match:
                return {
                    'success': False,
                    'error': '无法提取视频ID，请检查链接格式'
                }
            
            vid = vid_match.group(1)
            
            # 首先尝试直接获取页面信息
            title = '未知标题'
            try:
                page_response = requests.get(url, headers=self.headers, timeout=10)
                if page_response.status_code == 200:
                    html = page_response.text
                    # 提取标题
                    title_match = re.search(r'<title>(.*?)</title>', html)
                    if title_match:
                        title = title_match.group(1).replace(' - 腾讯视频', '').strip()
            except:
                pass
            
            # 获取视频信息
            info_url = f'https://vv.video.qq.com/getinfo?vids={vid}&platform=101001&charge=0&otype=json'
            try:
                response = requests.get(info_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    # 解析JSON数据
                    json_data = response.text
                    # 移除JSONP包装
                    json_data = re.sub(r'^QZOutputJson=', '', json_data)
                    json_data = re.sub(r';$', '', json_data)
                    
                    data = json.loads(json_data)
                    
                    if data.get('pl') and len(data['pl']['videolist']) > 0:
                        video_info = data['pl']['videolist'][0]
                        
                        return {
                            'success': True,
                            'title': video_info.get('ti', title),
                            'duration': self._format_duration(video_info.get('td', 0)),
                            'thumbnail': video_info.get('pic', ''),
                            'play_url': self._get_tencent_play_url(vid, url),
                            'quality_options': ['1080P', '720P', '480P', '360P'],
                            'vid': vid
                        }
            except Exception as api_error:
                # 如果API调用失败，返回基本信息
                return {
                    'success': True,
                    'title': title,
                    'duration': '未知',
                    'thumbnail': '',
                    'play_url': self._get_tencent_play_url(vid, url),
                    'quality_options': ['1080P', '720P', '480P', '360P'],
                    'vid': vid
                }
            
            return {
                'success': False,
                'error': '无法获取视频信息，可能是VIP内容或链接无效'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'腾讯视频解析错误: {str(e)}'
            }
    
    def _parse_iqiyi(self, url: str) -> Dict[str, Any]:
        """解析爱奇艺视频"""
        try:
            # 获取页面内容
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # 提取视频标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                title = title_match.group(1) if title_match else '未知标题'
                
                # 提取视频ID
                vid_match = re.search(r'data-player-videoid="([^"]+)"', html)
                if not vid_match:
                    vid_match = re.search(r'albumId=(\d+)', html)
                
                vid = vid_match.group(1) if vid_match else ''
                
                return {
                    'success': True,
                    'title': title.replace(' - 爱奇艺', ''),
                    'duration': '未知',
                    'thumbnail': '',
                    'play_url': self._get_iqiyi_play_url(url),
                    'quality_options': ['1080P', '720P', '480P', '360P'],
                    'vid': vid
                }
            
            return {
                'success': False,
                'error': '获取页面失败'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'爱奇艺解析错误: {str(e)}'
            }
    
    def _parse_youku(self, url: str) -> Dict[str, Any]:
        """解析优酷视频"""
        try:
            # 获取页面内容
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # 提取视频标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                title = title_match.group(1) if title_match else '未知标题'
                
                # 提取视频ID
                vid_match = re.search(r'videoId":"([^"]+)"', html)
                vid = vid_match.group(1) if vid_match else ''
                
                return {
                    'success': True,
                    'title': title.replace(' - 优酷视频', ''),
                    'duration': '未知',
                    'thumbnail': '',
                    'play_url': self._get_youku_play_url(url),
                    'quality_options': ['1080P', '720P', '480P', '360P'],
                    'vid': vid
                }
            
            return {
                'success': False,
                'error': '获取页面失败'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'优酷解析错误: {str(e)}'
            }
    
    def _parse_bilibili(self, url: str) -> Dict[str, Any]:
        """解析B站视频"""
        try:
            # B站API相对比较开放
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
                    'error': '无法提取视频ID'
                }
            
            response = requests.get(api_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 0:
                    video_info = data['data']
                    
                    return {
                        'success': True,
                        'title': video_info.get('title', '未知标题'),
                        'duration': self._format_duration(video_info.get('duration', 0)),
                        'thumbnail': video_info.get('pic', ''),
                        'play_url': url,  # B站不需要解析，直接使用原URL
                        'quality_options': ['1080P', '720P', '480P', '360P'],
                        'vid': video_info.get('bvid', video_info.get('aid', ''))
                    }
            
            return {
                'success': False,
                'error': '获取视频信息失败'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'B站解析错误: {str(e)}'
            }
    
    def _parse_mgtv(self, url: str) -> Dict[str, Any]:
        """解析芒果TV"""
        try:
            # 芒果TV解析逻辑
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                # 提取视频标题
                title_match = re.search(r'<title>(.*?)</title>', html)
                title = title_match.group(1) if title_match else '未知标题'
                
                return {
                    'success': True,
                    'title': title.replace(' - 芒果TV', ''),
                    'duration': '未知',
                    'thumbnail': '',
                    'play_url': self._get_mgtv_play_url(url),
                    'quality_options': ['1080P', '720P', '480P', '360P'],
                    'vid': ''
                }
            
            return {
                'success': False,
                'error': '获取页面失败'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'芒果TV解析错误: {str(e)}'
            }
    
    def _get_tencent_play_url(self, vid: str, original_url: str = None) -> str:
        """获取腾讯视频播放地址"""
        # 使用原始URL或构造URL
        if original_url:
            target_url = original_url
        else:
            target_url = f"https://v.qq.com/x/cover/{vid}.html"
        
        # 这里应该实现真实的URL解析逻辑
        # 由于技术限制，这里返回使用第三方解析的URL
        # 注意：实际使用时需要替换为真实可用的解析接口
        return f"https://jx.618g.com/?url={target_url}"
    
    def _get_iqiyi_play_url(self, original_url: str) -> str:
        """获取爱奇艺播放地址"""
        # 使用第三方解析接口
        return f"https://jx.618g.com/?url={original_url}"
    
    def _get_youku_play_url(self, original_url: str) -> str:
        """获取优酷播放地址"""
        # 使用优酷专用解析接口
        return f"https://jx.xymp4.cc/?url={original_url}"
    
    def _get_mgtv_play_url(self, original_url: str) -> str:
        """获取芒果TV播放地址"""
        # 使用第三方解析接口
        return f"https://jx.618g.com/?url={original_url}"
    
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
    
    def test_parse_api(self, api_url: str, video_url: str) -> Dict[str, Any]:
        """测试第三方解析API"""
        try:
            parse_url = f"{api_url}?url={video_url}"
            response = requests.get(parse_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.text
                }
            else:
                return {
                    'success': False,
                    'error': f'API返回状态码: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'API测试失败: {str(e)}'
            } 
