# AGENTS.md

Development guidelines for agentic coding assistants working in the Book Sort codebase.

## Build, Lint, Test Commands

### Environment Setup (Required)
```bash
conda activate fastapi-env
```

### Running Tests

**Run all component tests:**
```bash
python test_refactored.py
```

**Run individual test functions:**
```bash
python -c "import sys; sys.path.insert(0, '.'); from test_refactored import *; test_config_manager()"
```

**Test specific functionality:**
```bash
python test_fix.py                # API and JSON parsing tests
python test_book_classification.py # Book classification tests
python test_api.py                # Basic API connectivity tests
```

### Main Application
```bash
python book_sort.py                                    # Use default paths
python book_sort.py --src_dir /path/to/src --target_dir /path/to/target
```

### Dependencies
```bash
pip install -r requirements.txt  # aiohttp, SQLAlchemy
```

## Code Style Guidelines

### Import Organization

**Order:** Standard library → Third-party → Local imports
```python
import argparse
import asyncio
import sys
from datetime import datetime
from typing import List, Dict, Optional

from config.config_manager import ConfigManager
from database.database_manager import DatabaseManager
```

**Rules:**
- Alphabetical within each group
- Type hints from `typing` module
- Local imports use relative paths (`from .models import Base`)

### Type Hinting

**Always specify return types:**
```python
def classify_books(self, titles: List[str], existing_categories: List[str]) -> Dict[str, str]:
def get_book_extensions(self) -> List[str]:
def scan_books(self, directory: str) -> List[str]:
```

**Use `Optional[T]` for nullable returns:**
```python
def get_book_by_filename(self, session: Session, filename: str) -> Optional[BookInfo]:
```

### Naming Conventions

**Classes:** PascalCase with descriptive names
```python
class BookSortController:
class AICategorizationService:
class DatabaseManager:
```

**Functions/Methods:** snake_case with descriptive verbs
```python
def classify_books():
def create_classification_task():
def get_existing_categories():
```

**Variables:** snake_case, descriptive
```python
config_manager
database_manager
book_files
category_tag
```

**Private methods:** Prefix with underscore
```python
def _classify_with_deepseek():
def _parse_response():
def _get_filename_from_path():
```

### Error Handling

**Database operations - always include rollback:**
```python
try:
    book = BookInfo(filename=filename, file_path=file_path)
    session.add(book)
    session.commit()
except Exception as e:
    session.rollback()
    print(f"创建图书记录失败: {e}")
    raise
```

**Network operations - use specific exceptions:**
```python
except asyncio.TimeoutError:
    print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
except aiohttp.ClientPayloadError as e:
    print(f"传输编码错误: {e}")
```

**Generic exception with context:**
```python
except Exception as e:
    print(f"操作失败: {e}")
    raise
```

### Docstrings

**Chinese docstrings with triple quotes:**
```python
def classify_books(self, titles: List[str], existing_categories: List[str]) -> Dict[str, str]:
    """对一批图书标题进行分类

    Args:
        titles: 图书标题列表
        existing_categories: 现有分类列表

    Returns:
        分类结果字典，键为文件名，值为分类标签

    Raises:
        Exception: API调用失败时抛出异常
    """
```

**Required sections:** `Args:`, `Returns:`, `Raises:` (if applicable)

### Logging

**Use print statements with emojis for visual hierarchy:**
```python
print("=" * 60)
print("🚀 Book Sort 智能图书分类系统")
print("=" * 60)
print("1️⃣ 检查目录权限...")
print("✓ 权限检查通过")
print(f"❌ 未找到可分类的图书文件")
print(f"📦 正在处理批次，包含 {len(batch_files)} 个文件...")
```

**Symbols:**
- Success: `✓`
- Error: `✗`
- Warning: `⚠️`
- Steps: `1️⃣`, `2️⃣`, etc.
- Context: `🚀`, `📁`, `🤖`, `📚`

### Async/Await Patterns

**Async for I/O operations:**
```python
async def classify_books(self, titles: List[str], existing_categories: List[str]) -> Dict[str, str]:
    async with aiohttp.ClientSession() as session:
        return await self._classify_with_deepseek(session, titles, existing_categories)
```

**Timeout handling:**
```python
timeout = aiohttp.ClientTimeout(total=60, connect=10)
async with session.post(url, headers=headers, json=payload, timeout=timeout) as response:
    # process response
```

**Retry with asyncio.sleep:**
```python
for attempt in range(max_retries):
    try:
        # operation
    except Exception as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
            continue
        raise
```

### Class Structure

**Dependency injection pattern:**
```python
class BookSortController:
    def __init__(self,
                 config_manager: ConfigManager,
                 database_manager: DatabaseManager,
                 file_scanner: FileScanner,
                 ai_service: AICategorizationService):
        self.config_manager = config_manager
        self.database_manager = database_manager
        # ... assign all dependencies
```

**Composition over inheritance:** Classes don't inherit unless using SQLAlchemy models

### SQLAlchemy Models

**Standard ORM pattern:**
```python
class BookInfo(Base):
    __tablename__ = 'book_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False, comment='文件名')

    def __repr__(self):
        return f"<BookInfo(id={self.id}, filename='{self.filename}')>"

    def to_dict(self):
        return {'id': self.id, 'filename': self.filename}
```

## Testing Framework

**Custom testing (no pytest/unittest):**
```python
def test_component_name():
    """测试组件描述"""
    try:
        from module.component import Component
        component = Component()
        print("✓ Component 创建成功")
        return True
    except Exception as e:
        print(f"✗ 组件测试失败: {e}")
        return False
```

**No formal mocking required** - use fake parameters for object creation testing.

## Configuration

**Load from config.yaml with environment variable fallback:**
```python
api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key:
    return api_key
return self.get('deepseek_api_key', '')
```

**Security:** Prefer environment variables over config file for sensitive data (API keys).

## Architecture Principles

**Dependency injection** for all major components
**Separation of concerns:** config, database, services, scanners, utils
**Async for I/O**, sync for orchestration
**Session management:** Always close database sessions (try/finally or context manager)
