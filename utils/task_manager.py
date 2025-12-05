"""
任务管理器模块
负责创建和管理分类任务，追踪任务进度
"""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import ClassificationTask
from database.database_manager import DatabaseManager


class TaskManager:
    """任务管理器，负责任务的创建和状态管理"""

    def __init__(self, db_manager: DatabaseManager):
        """初始化任务管理器

        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager

    def create_task(self, session: Session, task_id: str, files: List[str]) -> ClassificationTask:
        """创建分类任务

        Args:
            session: 数据库会话
            task_id: 任务唯一标识
            files: 待处理的文件路径列表

        Returns:
            ClassificationTask 对象

        Raises:
            ValueError: 参数验证失败
            Exception: 数据库操作失败
        """
        if not task_id:
            raise ValueError("任务ID不能为空")

        if not files:
            raise ValueError("文件列表不能为空")

        try:
            return self.db_manager.create_classification_task(session, task_id, files)
        except Exception as e:
            print(f"创建任务失败: {e}")
            raise

    def update_task_progress(self,
                           session: Session,
                           task_id: str,
                           processed_files: int,
                           completed_files_list: List[str],
                           pending_files_list: List[str]) -> Optional[ClassificationTask]:
        """更新分类任务进度

        Args:
            session: 数据库会话
            task_id: 任务唯一标识
            processed_files: 已处理文件数
            completed_files_list: 已完成文件路径列表
            pending_files_list: 待处理文件路径列表

        Returns:
            更新后的 ClassificationTask 对象，如果任务不存在返回 None

        Raises:
            Exception: 数据库操作失败
        """
        task = self.get_task(session, task_id)
        if not task:
            print(f"任务不存在: {task_id}")
            return None

        try:
            self.db_manager.update_classification_task(
                session, task, processed_files, completed_files_list, pending_files_list
            )
            return task
        except Exception as e:
            print(f"更新任务进度失败: {e}")
            raise

    def get_task(self, session: Session, task_id: str) -> Optional[ClassificationTask]:
        """根据任务ID获取任务

        Args:
            session: 数据库会话
            task_id: 任务唯一标识

        Returns:
            ClassificationTask 对象或 None
        """
        return self.db_manager.get_task_by_id(session, task_id)

    def get_all_tasks(self, session: Session) -> List[ClassificationTask]:
        """获取所有任务

        Args:
            session: 数据库会话

        Returns:
            ClassificationTask 对象列表
        """
        return self.db_manager.get_all_tasks(session)

    def get_pending_tasks(self, session: Session) -> List[ClassificationTask]:
        """获取未完成的任务

        Args:
            session: 数据库会话

        Returns:
            未完成的 ClassificationTask 对象列表
        """
        return self.db_manager.get_pending_tasks(session)

    def is_task_completed(self, task: ClassificationTask) -> bool:
        """检查任务是否已完成

        Args:
            task: ClassificationTask 对象

        Returns:
            True 表示任务已完成，False 表示未完成
        """
        return task.is_completed

    def get_task_progress(self, session: Session, task_id: str) -> Optional[dict]:
        """获取任务进度信息

        Args:
            session: 数据库会话
            task_id: 任务唯一标识

        Returns:
            进度信息字典，包含 total, processed, percentage, completed 等字段
        """
        task = self.get_task(session, task_id)
        if not task:
            return None

        return {
            'task_id': task.task_id,
            'total_files': task.total_files,
            'processed_files': task.processed_files,
            'pending_files': len(json.loads(task.pending_files)) if task.pending_files else 0,
            'percentage': task.get_progress_percentage(),
            'is_completed': task.is_completed,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        }

    def resume_task(self, session: Session, task_id: str) -> Optional[ClassificationTask]:
        """恢复未完成的任务

        Args:
            session: 数据库会话
            task_id: 任务唯一标识

        Returns:
            可恢复的任务对象，如果任务不存在或已完成返回 None

        Raises:
            Exception: 数据库操作失败
        """
        task = self.get_task(session, task_id)
        if not task:
            print(f"任务不存在: {task_id}")
            return None

        if task.is_completed:
            print(f"任务已完成: {task_id}")
            return None

        pending_files = json.loads(task.pending_files) if task.pending_files else []
        if not pending_files:
            print(f"任务没有待处理的文件: {task_id}")
            return None

        print(f"恢复任务: {task_id}, 待处理文件数: {len(pending_files)}")
        return task
