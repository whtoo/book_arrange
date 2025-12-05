"""
文件扫描器模块
负责扫描文件系统，获取文件列表和分类信息
"""
import os
from typing import List


class FileScanner:
    """文件扫描器，负责文件系统扫描"""

    def __init__(self, book_extensions: List[str] = None):
        """初始化文件扫描器

        Args:
            book_extensions: 支持的图书文件扩展名列表
        """
        self.book_extensions = book_extensions or [
            '.pdf', '.epub', '.mobi', '.djvu', '.txt'
        ]

    def scan_books(self, directory: str) -> List[str]:
        """扫描目录获取图书文件列表（仅根目录）

        Args:
            directory: 要扫描的目录路径

        Returns:
            图书文件完整路径列表
        """
        book_files = []
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in self.book_extensions:
                        book_files.append(file_path)
        except Exception as e:
            print(f"扫描目录时发生未知错误: {e}")

        return book_files

    def get_existing_categories(self, directory: str, uncat_folder: str = '其他') -> List[str]:
        """获取所有现有的分类名称（即子目录）

        Args:
            directory: 要扫描的目录
            uncat_folder: 未分类文件夹名称，默认为 '其他'

        Returns:
            分类名称列表
        """
        categories = []
        try:
            for item in os.listdir(directory):
                if os.path.isdir(os.path.join(directory, item)) and item != uncat_folder:
                    categories.append(item)
        except Exception as e:
            print(f"获取现有分类时出错: {e}")

        return categories

    def check_directory_access(self, directory: str) -> None:
        """检查目录访问权限

        Args:
            directory: 要检查的目录路径

        Raises:
            PermissionError: 无访问权限
            FileNotFoundError: 目录不存在
        """
        try:
            os.listdir(directory)
        except PermissionError:
            print(f"\n错误：无法访问目录 '{directory}'。")
            print("这通常是由于缺少 '完全磁盘访问权限' 导致的。")
            print("\n请按照以下步骤授予权限：")
            print("1. 打开 '系统设置' > '隐私与安全性'。")
            print("2. 向下滚动并选择 '完全磁盘访问权限'。")
            print("3. 点击 '+' 按钮，将您的终端应用程序（例如 'Terminal' 或 'iTerm'）添加到列表中。")
            print("\n授权后，请重新运行脚本。")
            raise
        except FileNotFoundError:
            print(f"\n错误：目录 '{directory}' 不存在。请检查路径是否正确。")
            raise
