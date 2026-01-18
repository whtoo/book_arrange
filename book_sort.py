"""
Book Sort 主程序 - 重构版本
智能图书分类系统的主控制器和程序入口
"""

import argparse
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Optional

# 添加当前目录到 Python 路径，以便导入模块
sys.path.insert(0, ".")

from config.config_manager import ConfigManager
from database.database_manager import DatabaseManager
from database.models import BookInfo
from scanners.file_scanner import FileScanner
from services.ai_categorization_service import AICategorizationService
from services.file_manager import FileManager
from utils.task_manager import TaskManager


class BookSortController:
    """Book Sort 系统主控制器

    负责协调各个组件，编排整个分类流程
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        database_manager: DatabaseManager,
        file_scanner: FileScanner,
        ai_service: AICategorizationService,
        file_manager: FileManager,
        task_manager: TaskManager,
    ):
        """初始化主控制器

        Args:
            config_manager: 配置管理器
            database_manager: 数据库管理器
            file_scanner: 文件扫描器
            ai_service: AI 分类服务
            file_manager: 文件管理器
            task_manager: 任务管理器
        """
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.file_scanner = file_scanner
        self.ai_service = ai_service
        self.file_manager = file_manager
        self.task_manager = task_manager

    def run(self, src_dir: str, target_dir: str) -> None:
        """运行图书分类系统

        Args:
            src_dir: 源目录路径
            target_dir: 目标目录路径

        Raises:
            Exception: 系统运行失败
        """
        try:
            print("=" * 60)
            print("🚀 Book Sort 智能图书分类系统")
            print("=" * 60)

            # 1. 检查目录访问权限
            print("1️⃣ 检查目录权限...")
            self.file_scanner.check_directory_access(src_dir)
            self.file_scanner.check_directory_access(target_dir)
            print("✓ 权限检查通过")

            # 2. 初始化数据库
            print("2️⃣ 初始化数据库...")
            db_path = self.config_manager.get_database_path(target_dir)
            self.database_manager.init_database()
            print("✓ 数据库初始化完成")

            # 3. 扫描图书文件
            print("3️⃣ 扫描图书文件...")
            book_extensions = self.config_manager.get_book_extensions()
            book_files = self.file_scanner.scan_books(src_dir)

            if not book_files:
                print("❌ 未找到可分类的图书文件")
                return

            print(f"✓ 发现 {len(book_files)} 个图书文件")

            # 4. 获取现有分类
            print("4️⃣ 获取现有分类...")
            uncat_folder = self.config_manager.get_uncat_folder()
            existing_categories = self.file_scanner.get_existing_categories(
                target_dir, uncat_folder
            )
            print(
                f"✓ 发现现有分类: {existing_categories if existing_categories else '无'}"
            )

            # 5. 创建分类任务
            print("5️⃣ 创建分类任务...")
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session = self.database_manager.get_session()

            try:
                task = self.task_manager.create_task(session, task_id, book_files)
                print(f"✓ 创建分类任务 {task_id}")
                print(f"  总文件数: {task.total_files}")
                print(f"  批处理大小: {self.config_manager.get_batch_max_size()}")

                # 6. 异步执行分类
                print("\n6️⃣ 开始异步分类...")
                asyncio.run(self._process_classification(session, task, target_dir))

                # Get final task status for summary
                final_session = self.database_manager.get_session()
                try:
                    final_task = self.task_manager.get_task(final_session, task.task_id)
                    if final_task:
                        print(f"\n✅ 分类任务完成")
                        print(
                            f"   处理文件总数: {final_task.processed_files}/{final_task.total_files}"
                        )
                finally:
                    final_session.close()

            except Exception as e:
                print(f"❌ 分类任务执行失败: {e}")
                raise
            finally:
                session.close()

        except Exception as e:
            print(f"❌ 系统运行失败: {e}")
            raise

    async def _process_classification(self, session, task, target_dir: str) -> None:
        """处理分类任务（异步）

        Args:
            session: 数据库会话
            task: 分类任务对象
            target_dir: 目标目录
        """
        batch_size = self.config_manager.get_batch_max_size()
        uncat_folder = self.config_manager.get_uncat_folder()

        # 持续处理直到任务完成
        while not self.task_manager.is_task_completed(task):
            # 获取当前任务状态
            progress_info = self.task_manager.get_task_progress(session, task.task_id)
            if not progress_info:
                break

            # Get the actual pending files list from the task object
            current_session = self.database_manager.get_session()
            try:
                task_obj = self.task_manager.get_task(current_session, task.task_id)
                if not task_obj or not task_obj.pending_files:
                    break

                import json

                pending_files_list = json.loads(task_obj.pending_files)

                if not pending_files_list:
                    break

                batch_files = pending_files_list[:batch_size]
                batch_filenames = [self._get_filename_from_path(f) for f in batch_files]

                print(f"\n📦 正在处理批次，包含 {len(batch_files)} 个文件...")

                # 调用 AI 服务进行分类
                existing_categories = self.file_scanner.get_existing_categories(
                    target_dir, uncat_folder
                )
                classification_results = await self.ai_service.classify_books(
                    batch_filenames, existing_categories
                )

                if not classification_results:
                    print("⚠️  API未返回有效的分类结果，将使用默认分类")

                # 处理分类结果
                completed_files_list = []
                for file_path in batch_files:
                    try:
                        filename = self._get_filename_from_path(file_path)
                        category = classification_results.get(filename, uncat_folder)

                        # 移动文件
                        target_path = self.file_manager.move_file_to_category(
                            file_path, target_dir, category
                        )

                        # 更新数据库
                        book_info = self.database_manager.get_or_create_book_info(
                            current_session, filename, target_path
                        )
                        self.database_manager.update_book_category(
                            current_session, filename, category
                        )

                        # 记录完成状态
                        completed_files_list.append(file_path)

                    except Exception as e:
                        print(f"✗ 处理文件失败: {e}")
                        # 即使出错，也将其标记为完成，避免无限循环
                        completed_files_list.append(file_path)

                # 更新任务进度
                completed_count = progress_info["processed_files"] + len(
                    completed_files_list
                )

                # Get existing completed files and add new ones
                existing_completed = (
                    json.loads(task_obj.completed_files)
                    if task_obj.completed_files
                    else []
                )
                all_completed = existing_completed + completed_files_list

                # Calculate remaining pending files
                remaining_pending = [
                    f for f in pending_files_list if f not in completed_files_list
                ]

                self.task_manager.update_task_progress(
                    current_session,
                    task.task_id,
                    completed_count,
                    all_completed,
                    remaining_pending,
                )

                # 更新后重新获取并显示最新进度
                updated_progress = self.task_manager.get_task_progress(
                    current_session, task.task_id
                )
                if updated_progress:
                    print(
                        f"   当前进度: {updated_progress['processed_files']}/{updated_progress['total_files']} "
                        f"({updated_progress['percentage']:.1f}%)"
                    )

                print(f"✓ 批次处理完成")

            except Exception as e:
                print(f"✗ 批次处理失败: {e}")
                raise
            finally:
                current_session.close()

    def _get_filename_from_path(self, file_path: str) -> str:
        """从文件路径中提取文件名

        Args:
            file_path: 文件完整路径

        Returns:
            文件名
        """
        import os

        return os.path.basename(file_path)


def create_components(config_manager: ConfigManager):
    """创建系统组件

    Args:
        config_manager: 配置管理器

    Returns:
        包含所有组件的字典
    """
    # 创建数据库管理器
    db_path = config_manager.get_database_path(config_manager.get_default_target_dir())
    database_manager = DatabaseManager(db_path)

    # 创建其他组件
    file_scanner = FileScanner(config_manager.get_book_extensions())
    ai_service = AICategorizationService(
        config_manager.get_deepseek_api_url(),
        config_manager.get_deepseek_api_key(),
        config_manager.get_batch_max_size(),
    )
    file_manager = FileManager(config_manager.get_uncat_folder())
    task_manager = TaskManager(database_manager)

    return {
        "database_manager": database_manager,
        "file_scanner": file_scanner,
        "ai_service": ai_service,
        "file_manager": file_manager,
        "task_manager": task_manager,
    }


def main():
    """主程序入口"""
    try:
        # 1. 创建配置管理器
        config_manager = ConfigManager()

        # 2. 解析命令行参数
        parser = argparse.ArgumentParser(
            description="使用 AI 对图书进行智能分类",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例用法:
  %(prog)s                                      # 使用默认路径
  %(prog)s --src_dir /path/to/books             # 指定源目录
  %(prog)s --src_dir /src --target_dir /dest    # 指定源和目标目录
            """,
        )

        default_src_dir = config_manager.get_default_src_dir()
        default_target_dir = config_manager.get_default_target_dir()

        parser.add_argument(
            "--src_dir",
            type=str,
            default=default_src_dir,
            help=f"待分类图书的源目录 (默认: {default_src_dir})",
        )
        parser.add_argument(
            "--target_dir",
            type=str,
            default=default_target_dir,
            help=f"存放分类后图书的目标目录 (默认: {default_target_dir})",
        )

        args = parser.parse_args()

        # 3. 显示配置信息
        print(f"📁 源目录: {args.src_dir}")
        print(f"📁 目标目录: {args.target_dir}")
        print(f"🤖 API 服务: {config_manager.get_deepseek_api_url()}")
        print(f"📚 支持格式: {', '.join(config_manager.get_book_extensions())}")
        print()

        # 4. 创建系统组件
        components = create_components(config_manager)

        # 5. 创建主控制器
        controller = BookSortController(
            config_manager=config_manager,
            database_manager=components["database_manager"],
            file_scanner=components["file_scanner"],
            ai_service=components["ai_service"],
            file_manager=components["file_manager"],
            task_manager=components["task_manager"],
        )

        # 6. 运行系统
        controller.run(args.src_dir, args.target_dir)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断，程序退出")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        print("\n🔧 请检查：")
        print("   1. 配置文件是否正确")
        print("   2. 目录路径是否存在")
        print("   3. 网络连接是否正常")
        print("   4. API 密钥是否有效")
        sys.exit(1)


if __name__ == "__main__":
    main()
