"""
配置管理器模块
负责加载和管理应用程序配置
"""
import os
import yaml
from typing import Dict, Any, Optional, List


class ConfigManager:
    """配置管理器，负责加载和管理应用程序配置"""

    def __init__(self, config_path: str = 'config.yaml'):
        """初始化配置管理器

        Args:
            config_path: 配置文件路径，默认为 'config.yaml'
        """
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: 配置文件格式错误
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            print(f"配置文件加载成功: {self.config_path}")
        except FileNotFoundError:
            print(f"错误: 找不到配置文件 {self.config_path}")
            # 使用默认配置
            self._config = self._get_default_config()
            print("使用默认配置")
        except yaml.YAMLError as e:
            print(f"错误: 配置文件格式错误: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置

        Returns:
            默认配置字典
        """
        return {
            'deepseek_api_url': "https://api.deepseek.com/v1/chat/completions",
            'deepseek_api_key': "sk-your-api-key-here",
            'batch_max_size': 50,
            'book_exts': ['.pdf', '.epub', '.mobi', '.djvu', '.txt'],
            'uncat': '其他',
            'default_paths': {
                'src_dir': "/Users/blitz/Downloads",
                'target_dir': "/Users/blitz/Documents/Books"
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置项键名，支持点号分隔的嵌套键 (如 'default_paths.src_dir')
            default: 默认值

        Returns:
            配置项值
        """
        if '.' in key:
            keys = key.split('.')
            value = self._config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        return self._config.get(key, default)

    def get_deepseek_api_url(self) -> str:
        """获取 DeepSeek API URL

        Returns:
            DeepSeek API URL
        """
        return self.get('deepseek_api_url')

    def get_deepseek_api_key(self) -> str:
        """获取 DeepSeek API 密钥

        Returns:
            DeepSeek API 密钥
        """
        # 优先从环境变量获取
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if api_key:
            return api_key
        return self.get('deepseek_api_key', '')

    def get_batch_max_size(self) -> int:
        """获取批处理最大大小

        Returns:
            批处理最大大小
        """
        return self.get('batch_max_size', 50)

    def get_book_extensions(self) -> List[str]:
        """获取支持的图书文件扩展名

        Returns:
            支持的文件扩展名列表
        """
        return self.get('book_exts', ['.pdf', '.epub', '.mobi', '.djvu', '.txt'])

    def get_uncat_folder(self) -> str:
        """获取未分类文件夹名称

        Returns:
            未分类文件夹名称
        """
        return self.get('uncat', '其他')

    def get_database_path(self, target_dir: str) -> str:
        """获取数据库路径

        Args:
            target_dir: 目标目录

        Returns:
            数据库完整路径
        """
        return os.path.join(target_dir, 'book_classification.db')

    def get_default_src_dir(self) -> str:
        """获取默认源目录

        Returns:
            默认源目录路径
        """
        return self.get('default_paths.src_dir', '/Users/blitz/Downloads')

    def get_default_target_dir(self) -> str:
        """获取默认目标目录

        Returns:
            默认目标目录路径
        """
        return self.get('default_paths.target_dir', '/Users/blitz/Documents/Books')
