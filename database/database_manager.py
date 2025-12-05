"""
数据库管理器模块
负责数据库连接、初始化和数据操作
"""
import json
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, BookInfo, ClassificationTask


class DatabaseManager:
    """数据库管理器，封装数据库操作"""

    def __init__(self, db_path: str):
        """初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """获取数据库会话

        Returns:
            SQLAlchemy Session 对象
        """
        return self.SessionLocal()

    def init_database(self) -> None:
        """初始化数据库，创建所有表

        Raises:
            Exception: 数据库初始化失败
        """
        try:
            Base.metadata.create_all(self.engine)
            print("数据库初始化完成")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            raise

    def get_or_create_book_info(self,
                               session: Session,
                               filename: str,
                               file_path: str) -> BookInfo:
        """获取或创建图书记录

        如果记录已存在则返回现有记录，否则创建新记录

        Args:
            session: 数据库会话
            filename: 文件名
            file_path: 文件完整路径

        Returns:
            BookInfo 对象

        Raises:
            Exception: 数据库操作失败
        """
        import os

        book = session.query(BookInfo).filter_by(filename=filename).first()
        if not book:
            try:
                file_stat = os.stat(file_path)
                book = BookInfo(
                    filename=filename,
                    file_path=file_path,
                    file_size=file_stat.st_size,
                    file_ext=os.path.splitext(filename)[1].lower()
                )
                session.add(book)
                session.commit()
            except Exception as e:
                session.rollback()
                print(f"创建图书记录失败: {e}")
                raise
        return book

    def update_book_category(self,
                           session: Session,
                           filename: str,
                           category: str) -> bool:
        """更新图书分类

        Args:
            session: 数据库会话
            filename: 文件名
            category: 分类标签

        Returns:
            True 表示更新成功，False 表示未找到记录

        Raises:
            Exception: 数据库操作失败
        """
        from datetime import datetime

        book = session.query(BookInfo).filter_by(filename=filename).first()
        if book:
            try:
                book.category_tag = category
                book.updated_at = datetime.now()
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print(f"更新图书分类失败: {e}")
                raise
        return False

    def get_book_by_filename(self,
                           session: Session,
                           filename: str) -> Optional[BookInfo]:
        """根据文件名查询图书

        Args:
            session: 数据库会话
            filename: 文件名

        Returns:
            BookInfo 对象或 None
        """
        return session.query(BookInfo).filter_by(filename=filename).first()

    def get_books_by_category(self,
                            session: Session,
                            category: str) -> List[BookInfo]:
        """根据分类查询图书

        Args:
            session: 数据库会话
            category: 分类名称

        Returns:
            BookInfo 对象列表
        """
        return session.query(BookInfo).filter_by(category_tag=category).all()

    def create_classification_task(self,
                                 session: Session,
                                 task_id: str,
                                 files: List[str]) -> ClassificationTask:
        """创建分类任务

        Args:
            session: 数据库会话
            task_id: 任务唯一标识
            files: 文件路径列表

        Returns:
            ClassificationTask 对象

        Raises:
            Exception: 数据库操作失败
        """
        try:
            task = ClassificationTask(
                task_id=task_id,
                total_files=len(files),
                pending_files=json.dumps(files),
                completed_files=json.dumps([])
            )
            session.add(task)
            session.commit()
            return task
        except Exception as e:
            session.rollback()
            print(f"创建分类任务失败: {e}")
            raise

    def update_classification_task(self,
                                 session: Session,
                                 task: ClassificationTask,
                                 processed_files: int,
                                 completed_files_list: List[str],
                                 pending_files_list: List[str]) -> None:
        """更新分类任务状态

        Args:
            session: 数据库会话
            task: ClassificationTask 对象
            processed_files: 已处理文件数
            completed_files_list: 已完成文件路径列表
            pending_files_list: 待处理文件路径列表

        Raises:
            Exception: 数据库操作失败
        """
        from datetime import datetime

        try:
            task.processed_files = processed_files
            task.completed_files = json.dumps(completed_files_list)
            task.pending_files = json.dumps(pending_files_list)
            task.is_completed = len(pending_files_list) == 0
            task.updated_at = datetime.now()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"更新任务状态失败: {e}")
            raise

    def get_task_by_id(self,
                     session: Session,
                     task_id: str) -> Optional[ClassificationTask]:
        """根据任务ID查询任务

        Args:
            session: 数据库会话
            task_id: 任务唯一标识

        Returns:
            ClassificationTask 对象或 None
        """
        return session.query(ClassificationTask).filter_by(task_id=task_id).first()

    def get_all_tasks(self, session: Session) -> List[ClassificationTask]:
        """获取所有任务

        Args:
            session: 数据库会话

        Returns:
            ClassificationTask 对象列表
        """
        return session.query(ClassificationTask).all()

    def get_pending_tasks(self, session: Session) -> List[ClassificationTask]:
        """获取未完成任务

        Args:
            session: 数据库会话

        Returns:
            未完成的 ClassificationTask 对象列表
        """
        return session.query(ClassificationTask).filter_by(is_completed=False).all()
