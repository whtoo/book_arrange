"""
文件管理器模块
负责文件移动、目录创建和文件名处理
"""
import os
import shutil
from typing import List


class FileManager:
    """文件管理器，封装文件操作"""

    def __init__(self, uncat_folder: str = '其他'):
        """初始化文件管理器

        Args:
            uncat_folder: 未分类文件夹名称，默认为 '其他'
        """
        self.uncat_folder = uncat_folder

    def move_file_to_category(self,
                             file_path: str,
                             target_dir: str,
                             category: str) -> str:
        """将文件移动到指定分类目录

        Args:
            file_path: 源文件完整路径
            target_dir: 目标根目录
            category: 分类名称

        Returns:
            目标文件完整路径

        Raises:
            Exception: 文件操作失败
        """
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()

        # 确定分类目录
        category_dir = self.create_category_directory(target_dir, category)

        # 构建目标文件路径
        target_path = os.path.join(category_dir, filename)

        # 处理文件名冲突
        target_path = self.handle_duplicate_filename(target_path)

        # 移动文件
        try:
            shutil.move(file_path, target_path)
            print(f"✓ 移动文件: {filename} -> {category}")
            return target_path
        except Exception as e:
            print(f"✗ 移动文件失败 {filename}: {e}")
            raise

    def create_category_directory(self, target_dir: str, category: str) -> str:
        """创建分类目录（如果不存在）

        Args:
            target_dir: 目标根目录
            category: 分类名称

        Returns:
            分类目录的完整路径
        """
        category_dir = os.path.join(target_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        return category_dir

    def handle_duplicate_filename(self, target_path: str) -> str:
        """处理目标路径文件名冲突

        如果目标文件已存在，自动在文件名后添加计数器

        Args:
            target_path: 目标文件路径

        Returns:
            处理后的目标文件路径
        """
        if not os.path.exists(target_path):
            return target_path

        directory = os.path.dirname(target_path)
        filename = os.path.basename(target_path)
        base_name, ext = os.path.splitext(filename)

        counter = 1
        while os.path.exists(target_path):
            new_name = f"{base_name}_{counter}{ext}"
            target_path = os.path.join(directory, new_name)
            counter += 1

        return target_path

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

    def get_existing_categories(self, directory: str) -> List[str]:
        """获取目录中现有的分类（子目录）

        Args:
            directory: 要扫描的目录

        Returns:
            分类名称列表
        """
        categories = []
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path) and item != self.uncat_folder:
                    categories.append(item)
        except Exception as e:
            print(f"获取现有分类时出错: {e}")

        return categories

    def scan_books(self, directory: str, extensions: List[str]) -> List[str]:
        """扫描目录获取图书文件列表

        Args:
            directory: 要扫描的目录
            extensions: 支持的文件扩展名列表

        Returns:
            图书文件完整路径列表
        """
        book_files = []
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in extensions:
                        book_files.append(file_path)
        except Exception as e:
            print(f"扫描目录时发生未知错误: {e}")

        return book_files
