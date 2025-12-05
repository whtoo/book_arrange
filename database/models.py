"""
数据库模型定义模块
定义 ORM 数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base

# 创建基类
Base = declarative_base()


class BookInfo(Base):
    """图书元信息表

    存储图书的基本信息和分类结果
    """
    __tablename__ = 'book_info'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 文件名（唯一）
    filename = Column(String, unique=True, nullable=False,
                     comment='文件名，包含扩展名')

    # 文件完整路径
    file_path = Column(String, nullable=False,
                      comment='文件在系统中的完整路径')

    # 文件大小（字节）
    file_size = Column(Integer,
                      comment='文件大小，单位为字节')

    # 文件扩展名
    file_ext = Column(String,
                     comment='文件扩展名，如 .pdf, .epub 等')

    # 分类标签
    category_tag = Column(String,
                         comment='分类标签，如 "计算机", "文学" 等。未分类时为空')

    # 创建时间
    created_at = Column(DateTime, default=datetime.now,
                       comment='记录创建时间')

    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now,
                       comment='记录最后更新时间')

    def __repr__(self):
        """字符串表示"""
        return (f"<BookInfo(id={self.id}, filename='{self.filename}', "
                f"category='{self.category_tag}')>")

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_ext': self.file_ext,
            'category_tag': self.category_tag,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ClassificationTask(Base):
    """分类任务记录表

    追踪图书分类任务的执行进度和状态
    """
    __tablename__ = 'classification_task'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 任务唯一标识
    task_id = Column(String, unique=True, nullable=False,
                    comment='任务唯一标识，格式: task_YYYYMMDD_HHMMSS')

    # 总文件数
    total_files = Column(Integer, nullable=False,
                        comment='任务需要处理的总文件数')

    # 已处理文件数
    processed_files = Column(Integer, default=0,
                            comment='已经处理完成的文件数量')

    # 已完成文件列表 (JSON格式)
    completed_files = Column(Text,
                            comment='已完成分类的文件路径列表，JSON格式存储')

    # 待处理文件列表 (JSON格式)
    pending_files = Column(Text,
                          comment='待处理的文件路径列表，JSON格式存储')

    # 完成标记
    is_completed = Column(Boolean, default=False, nullable=False,
                         comment='任务是否完成标记')

    # 创建时间
    created_at = Column(DateTime, default=datetime.now,
                       comment='任务创建时间')

    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now,
                       comment='任务状态最后更新时间')

    def __repr__(self):
        """字符串表示"""
        return (f"<ClassificationTask(task_id='{self.task_id}', "
                f"progress={self.processed_files}/{self.total_files}, "
                f"completed={self.is_completed})>")

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'completed_files': self.completed_files,
            'pending_files': self.pending_files,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_progress_percentage(self) -> float:
        """获取任务进度百分比

        Returns:
            进度百分比 (0-100)
        """
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100

    def is_active(self) -> bool:
        """检查任务是否进行中

        Returns:
            True 表示任务进行中，False 表示已完成或尚未开始
        """
        return not self.is_completed and self.processed_files > 0
