#!/usr/bin/env python3
"""
Book Sort CLI - 智能图书分类系统的命令行接口
"""

import sys
import os
import click
from typing import Optional

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from database.database_manager import DatabaseManager
from database.models import BookInfo, ClassificationTask
from scanners.file_scanner import FileScanner
from services.ai_categorization_service import AICategorizationService
from services.file_manager import FileManager
from utils.task_manager import TaskManager
from book_sort import BookSortController, create_components
import json


@click.group()
@click.version_option(version="1.0.0", prog_name="book-sort")
def cli():
    """📚 Book Sort - 基于 AI 的智能图书分类系统

    使用 DeepSeek AI 自动将图书文件分类整理到相应的目录中。
    """
    pass


@cli.command()
@click.option(
    "--src-dir",
    "-s",
    type=click.Path(exists=False),
    help=f"源目录路径（存放未分类图书），默认: 从config.yaml读取",
)
@click.option(
    "--target-dir",
    "-t",
    type=click.Path(exists=False),
    help=f"目标目录路径（存放已分类图书），默认: 从config.yaml读取",
)
@click.option(
    "--batch-size", "-b", type=int, help=f"批处理大小，默认: 从config.yaml读取"
)
def classify(
    src_dir: Optional[str], target_dir: Optional[str], batch_size: Optional[int]
):
    """🚀 执行图书分类

    扫描源目录中的图书文件，使用 AI 自动分类，并将文件移动到目标目录的相应子目录中。
    """
    try:
        config_manager = ConfigManager()

        if not src_dir:
            src_dir = config_manager.get_default_src_dir()
            click.echo(click.style(f"使用默认源目录: {src_dir}", fg="cyan"))

        if not target_dir:
            target_dir = config_manager.get_default_target_dir()
            click.echo(click.style(f"使用默认目标目录: {target_dir}", fg="cyan"))

        if batch_size:
            config_manager._config["batch_max_size"] = batch_size
            click.echo(click.style(f"批处理大小已覆盖为: {batch_size}", fg="cyan"))

        click.echo(click.style("🚀 开始图书分类", fg="blue", bold=True))
        click.echo("=" * 60)
        click.echo(f"📁 源目录: {src_dir}")
        click.echo(f"📁 目标目录: {target_dir}")
        click.echo(f"🤖 API 服务: {config_manager.get_deepseek_api_url()}")
        click.echo(f"📚 支持格式: {', '.join(config_manager.get_book_extensions())}")
        click.echo(f"📦 批次大小: {config_manager.get_batch_max_size()}")
        click.echo()

        components = create_components(config_manager)

        controller = BookSortController(
            config_manager=config_manager,
            database_manager=components["database_manager"],
            file_scanner=components["file_scanner"],
            ai_service=components["ai_service"],
            file_manager=components["file_manager"],
            task_manager=components["task_manager"],
        )

        controller.run(src_dir, target_dir)

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  用户中断，程序退出", fg="yellow")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ 程序执行失败: {e}", fg="red")
        click.echo("\n🔧 请检查：", fg="yellow")
        click.echo("   1. 配置文件是否正确")
        click.echo("   2. 目录路径是否存在")
        click.echo("   3. 网络连接是否正常")
        click.echo("   4. API 密钥是否有效")
        sys.exit(1)


@cli.group()
def config():
    """⚙️  配置管理"""
    pass


@config.command()
def show():
    """显示当前配置"""
    try:
        config_manager = ConfigManager()

        click.echo(click.style("📋 当前配置", fg="blue", bold=True))
        click.echo("=" * 60)
        click.echo(f"API URL: {config_manager.get_deepseek_api_url()}")
        click.echo(
            f"API 密钥: {'已配置' if config_manager.get_deepseek_api_key() else '未配置'}"
        )
        click.echo(f"批处理大小: {config_manager.get_batch_max_size()}")
        click.echo(f"支持的格式: {', '.join(config_manager.get_book_extensions())}")
        click.echo(f"未分类文件夹: {config_manager.get_uncat_folder()}")
        click.echo(f"默认源目录: {config_manager.get_default_src_dir()}")
        click.echo(f"默认目标目录: {config_manager.get_default_target_dir()}")
        click.echo()

        # 检查 API 密钥
        if not config_manager.get_deepseek_api_key():
            click.echo(click.style("⚠️  警告: API 密钥未配置", fg="yellow"), nl=False)
            click.echo("，请设置 DEEPSEEK_API_KEY 环境变量或在 config.yaml 中配置")
        else:
            click.echo(click.style("✓ API 密钥已配置", fg="green"))

    except Exception as e:
        click.echo(click.style(f"❌ 读取配置失败: {e}", fg="red"))
        sys.exit(1)


@config.command()
def validate():
    """验证配置"""
    try:
        config_manager = ConfigManager()

        click.echo(click.style("🔍 验证配置", fg="blue", bold=True))
        click.echo("=" * 60)

        errors = []
        warnings = []

        # 检查 API 密钥
        if not config_manager.get_deepseek_api_key():
            errors.append("API 密钥未配置")

        # 检查目录
        src_dir = config_manager.get_default_src_dir()
        if not os.path.exists(src_dir):
            errors.append(f"默认源目录不存在: {src_dir}")

        target_dir = config_manager.get_default_target_dir()
        if not os.path.exists(target_dir):
            errors.append(f"默认目标目录不存在: {target_dir}")

        # 检查批次大小
        batch_size = config_manager.get_batch_max_size()
        if batch_size < 1 or batch_size > 100:
            warnings.append(f"批处理大小 {batch_size} 可能不合理（建议 4-50）")

        # 显示结果
        if errors:
            click.echo(click.style("❌ 配置验证失败", fg="red"))
            for error in errors:
                click.echo(click.style(f"  ✗ {error}", fg="red"))
            sys.exit(1)
        elif warnings:
            click.echo(click.style("⚠️  配置验证通过，但有警告", fg="yellow"))
            for warning in warnings:
                click.echo(click.style(f"  ⚠️  {warning}", fg="yellow"))
        else:
            click.echo(click.style("✓ 配置验证通过", fg="green"))

    except Exception as e:
        click.echo(click.style(f"❌ 验证配置失败: {e}", fg="red"))
        sys.exit(1)


@cli.group()
def tasks():
    """📋 任务管理"""
    pass


@tasks.command()
@click.option(
    "--target-dir",
    "-t",
    type=click.Path(exists=False),
    help="目标目录路径，默认: 从config.yaml读取",
)
def list(target_dir: Optional[str]):
    """列出所有分类任务"""
    try:
        config_manager = ConfigManager()
        db_manager = DatabaseManager(
            config_manager.get_database_path(
                target_dir or config_manager.get_default_target_dir()
            )
        )

        session = db_manager.get_session()
        try:
            all_tasks = (
                session.query(ClassificationTask)
                .order_by(ClassificationTask.created_at.desc())
                .all()
            )

            if not all_tasks:
                click.echo("没有找到任务")
                return

            click.echo(click.style("📋 任务列表", fg="blue", bold=True))
            click.echo("=" * 80)

            for task in all_tasks:
                status_color = "green" if task.is_completed else "yellow"
                status_text = "✓ 已完成" if task.is_completed else "⟳ 进行中"

                click.echo(f"任务 ID: {task.task_id}")
                click.echo(f"状态: {click.style(status_text, fg=status_color)}")
                click.echo(
                    f"进度: {task.processed_files}/{task.total_files} "
                    f"({task.get_progress_percentage():.1f}%)"
                )
                click.echo(f"创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                click.echo("-" * 80)

        finally:
            session.close()

    except Exception as e:
        click.echo(click.style(f"❌ 列出任务失败: {e}", fg="red"))
        sys.exit(1)


@tasks.command()
@click.argument("task_id", type=str)
@click.option(
    "--target-dir",
    "-t",
    type=click.Path(exists=False),
    help="目标目录路径，默认: 从config.yaml读取",
)
def status(task_id: str, target_dir: Optional[str]):
    """查看任务状态"""
    try:
        config_manager = ConfigManager()
        target_dir = target_dir or config_manager.get_default_target_dir()
        db_manager = DatabaseManager(config_manager.get_database_path(target_dir))

        session = db_manager.get_session()
        try:
            task = session.query(ClassificationTask).filter_by(task_id=task_id).first()

            if not task:
                click.echo(click.style(f"❌ 任务不存在: {task_id}", fg="red"))
                sys.exit(1)

            click.echo(click.style("📊 任务详情", fg="blue", bold=True))
            click.echo("=" * 60)
            click.echo(f"任务 ID: {task.task_id}")

            status_color = "green" if task.is_completed else "yellow"
            status_text = "✓ 已完成" if task.is_completed else "⟳ 进行中"
            click.echo(f"状态: {click.style(status_text, fg=status_color)}")

            click.echo(
                f"进度: {task.processed_files}/{task.total_files} "
                f"({task.get_progress_percentage():.1f}%)"
            )

            pending_count = (
                len(json.loads(task.pending_files)) if task.pending_files else 0
            )
            completed_count = (
                len(json.loads(task.completed_files)) if task.completed_files else 0
            )

            click.echo(f"待处理: {pending_count} 个文件")
            click.echo(f"已完成: {completed_count} 个文件")
            click.echo(f"创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"更新时间: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        finally:
            session.close()

    except Exception as e:
        click.echo(click.style(f"❌ 查看任务状态失败: {e}", fg="red"))
        sys.exit(1)


@cli.command()
def version():
    """显示版本信息"""
    click.echo("Book Sort CLI v1.0.0")
    click.echo("基于 AI 的智能图书分类系统")


if __name__ == "__main__":
    cli()
