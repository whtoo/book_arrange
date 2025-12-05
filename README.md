# 📚 Book Sort

基于 AI 的智能图书分类系统，使用 DeepSeek API 自动将图书文件分类整理到相应的目录中。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 项目简介

Book Sort 是一个智能图书分类工具，通过 AI 技术自动识别和分类您的电子书库。系统支持批量处理 PDF、EPUB、MOBI、DJVU 和 TXT 格式的图书文件。

## ✨ 核心特性

- **AI 智能分类**: 基于 DeepSeek AI 自动识别图书内容并智能分类
- **批量处理**: 支持批量处理，一次性分类大量图书文件
- **异步处理**: 采用异步架构，提高处理效率
- **任务恢复**: 支持中断后继续，已处理的文件无需重复分类
- **灵活配置**: 支持自定义源目录、目标目录和文件类型
- **安全可靠**: 本地数据库记录，保护您的图书元数据
- **模块设计**: 采用依赖注入架构，易于扩展和维护

## 🚀 快速开始

### 环境要求

- Python 3.8+
- DeepSeek API 密钥（或其他兼容的 OpenAI API）

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/whtoo/book_arrange.git
cd book_arrange
```

2. **安装依赖**

需要预先激活 conda 环境：

```bash
# 激活 conda 环境
conda activate fastapi-env

# 安装 Python 依赖
pip install -r requirements.txt
```

3. **配置 API 密钥**

编辑 `config.yaml` 文件，设置您的 DeepSeek API 密钥：

```yaml
# DeepSeek API 配置
deepseek_api_url: "https://api.deepseek.com/v1/chat/completions"
deepseek_api_key: "YOUR_API_KEY_HERE"  # 设置 DEEPSEEK_API_KEY 环境变量或在此替换

# 批处理配置
batch_max_size: 16  # 批处理大小，建议 4-50 之间
```

**安全建议**：推荐将 API 密钥设置为环境变量：

```bash
export DEEPSEEK_API_KEY="sk-your-actual-api-key"
```

然后在 `config.yaml` 中将 `deepseek_api_key` 留空。

4. **运行程序**

```bash
# 使用默认配置（使用 config.yaml 中的路径）
python book_sort.py

# 指定自定义路径
python book_sort.py --src_dir /path/to/your/books --target_dir /path/to/sorted/books
```

## 📁 项目结构

```
book_arrange/
├── config/                      # 配置管理模块
│   └── config_manager.py       # 配置管理器
├── database/                     # 数据持久化层
│   ├── models.py                # ORM 模型
│   └── database_manager.py      # 数据库操作
├── services/                     # 业务逻辑层
│   ├── ai_categorization_service.py   # AI 分类服务
│   └── file_manager.py          # 文件管理服务
├── scanners/                     # 文件系统扫描
│   └── file_scanner.py          # 目录扫描器
├── utils/                        # 工具类
│   └── task_manager.py          # 任务进度管理
├── book_sort.py                 # 主程序入口
├── config.yaml                  # 配置文件
├── requirements.txt            # Python 依赖
├── README.md                   # 项目说明
└── CLAUDE.md                   # Claude Code 开发指南
```

## 🔧 配置说明

### config.yaml 配置项

```yaml
# DeepSeek API 配置（必需）
deepseek_api_url: "https://api.deepseek.com/v1/chat/completions"
deepseek_api_key: "YOUR_API_KEY_HERE"

# 批处理设置
batch_max_size: 16  # 每批处理的文件数量

# 支持的文件类型
book_exts:
  - ".pdf"
  - ".epub"
  - ".mobi"
  - ".djvu"
  - ".txt"

# 默认目录路径
default_paths:
  src_dir: "/Users/blitz/Downloads"           # 源目录（存放未分类图书）
  target_dir: "/Users/blitz/Documents/Books"  # 目标目录（存放已分类图书）

# 未分类文件夹名称
uncat: "其他"
```

### 命令行参数

```bash
python book_sort.py [选项]

选项:
  -h, --help                      显示帮助信息
  --src_dir SRC_DIR              源目录路径
  --target_dir TARGET_DIR        目标目录路径
```

## 🎯 使用示例

### 示例 1：基本使用

```bash
# 准备目录
mkdir -p ~/Downloads/books_to_sort
mkdir -p ~/Documents/organized_books

# 将图书文件放入源目录
cp ~/Downloads/*.pdf ~/Downloads/books_to_sort/
cp ~/Downloads/*.epub ~/Downloads/books_to_sort/

# 运行分类
python book_sort.py --src_dir ~/Downloads/books_to_sort --target_dir ~/Documents/organized_books
```

### 示例 2：使用环境变量配置 API 密钥

```bash
# 设置环境变量
export DEEPSEEK_API_KEY="sk-your-actual-key-here"

# 修改 config.yaml 中的 deepseek_api_key 为空
deepseek_api_key:  # 从环境变量读取

# 运行程序
python book_sort.py
```

## 💾 数据处理

### 数据库文件

系统在目标目录自动创建 `books.db` 数据库文件，存储图书元数据。

### 分类目录

图书将被移动到目标目录下的分类子目录，例如：

```
~/Documents/Books/
├── 计算机科学/
│   ├── Python编程入门.pdf
│   └── 算法导论.epub
├── 文学/
│   ├── 红楼梦.txt
│   └── 1984.pdf
└── 其他/
    └── 未分类文档.pdf
```

## 🧪 测试

运行测试脚本来验证系统配置：

```bash
python test_refactored.py
```

测试内容包括：
- 配置管理器功能
- 数据库操作
- AI 服务连接
- 文件管理功能

## 🐛 故障排除

### 常见问题

#### 1. API 连接错误

**问题**: `API请求失败: 401 - Unauthorized`

**解决**:
- 检查 `config.yaml` 中的 API 密钥是否正确
- 确认 API 密钥有足够的使用额度
- 验证网络连接是否正常

#### 2. 目录权限错误

**问题**: `错误：无法访问目录 '/path/to/directory'`

**解决**:
- 确认目录路径存在
- 给予程序访问权限：`chmod 755 /path/to/directory`
- macOS 用户需要在"系统偏好设置 > 安全性与隐私 > 隐私 > 完全磁盘访问权限"中授予终端权限

#### 3. 依赖导入错误

**问题**: `ImportError: No module named 'sqlalchemy'`

**解决**:
```bash
pip install sqlalchemy aiohttp PyYAML
```

### 性能调优

如果处理大量文件时遇到性能问题：

1. **调整批处理大小**：在 `config.yaml` 中减小 `batch_max_size`
2. **使用更快的网络**：AI API 调用是主要瓶颈
3. **分批处理**：将大量文件分成多个小批次处理

## 🏗️ 架构设计

### 核心组件

- **BookSortController** (`book_sort.py`): 主控制器，协调各组件工作
- **AICategorizationService** (`services/ai_categorization_service.py`): AI 分类服务
- **DatabaseManager** (`database/database_manager.py`): 数据库管理
- **FileManager** (`services/file_manager.py`): 文件操作
- **FileScanner** (`scanners/file_scanner.py`): 文件扫描
- **ConfigManager** (`config/config_manager.py`): 配置管理
- **TaskManager** (`utils/task_manager.py`): 任务管理

### 技术栈

- **异步框架**: asyncio + aiohttp
- **数据库**: SQLAlchemy
- **配置管理**: PyYAML
- **API 兼容**: OpenAI API 标准

## 📝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DeepSeek AI](https://www.deepseek.com/) - 提供强大的 AI 分类能力
- [Claude Code](https://claude.com/claude-code) - 协助项目开发

## 📞 联系方式

如果有任何问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/whtoo/book_arrange/issues)

---

**享受智能图书分类的便利！** 📚🤖

---

<div align="center">

⭐ 如果这个项目对您有帮助，请给个 Star 支持！

</div>
