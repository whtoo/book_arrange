"""
AI 分类服务模块
负责调用 DeepSeek API 对图书进行分类
"""
import json
import asyncio
import aiohttp
import re
from typing import List, Dict, Optional


class AICategorizationService:
    """AI 分类服务，封装 DeepSeek API 调用"""

    def __init__(self, api_url: str, api_key: str, batch_size: int = 50):
        """初始化 AI 分类服务

        Args:
            api_url: DeepSeek API URL
            api_key: DeepSeek API 密钥
            batch_size: 批处理大小，默认为 50
        """
        self.api_url = api_url
        self.api_key = api_key
        self.batch_size = batch_size

    async def classify_books(self,
                           titles: List[str],
                           existing_categories: List[str]) -> Dict[str, str]:
        """对一批图书标题进行分类

        Args:
            titles: 图书标题列表
            existing_categories: 现有分类列表

        Returns:
            分类结果字典，键为文件名，值为分类标签
        """
        if not titles:
            return {}

        async with aiohttp.ClientSession() as session:
            return await self._classify_with_deepseek(session, titles, existing_categories)

    async def _classify_with_deepseek(self,
                                    session: aiohttp.ClientSession,
                                    titles: List[str],
                                    existing_categories: List[str]) -> Dict[str, str]:
        """使用 DeepSeek API 进行分类（内部方法）

        Args:
            session: aiohttp ClientSession
            titles: 图书标题列表
            existing_categories: 现有分类列表

        Returns:
            分类结果字典
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "BookSort/1.0"
        }

        category_list = ", ".join(existing_categories) if existing_categories else "无"
        book_list_str = "\n".join([f"- {title}" for title in titles])

        system_prompt = (
            f"你是一个专业的图书分类系统。"
            f"现有分类如下: [{category_list}]。"
            f"请根据以下书名列表，为每本书从现有分类中选择一个最合适的分类标签。"
            f"如果都不匹配，可以根据书名内容创建一个新的、简洁的分类标签。"
            f"请以JSON格式返回结果,键是书名,值是分类标签。"
            f"例如: {{'book1.pdf': '分类1', 'book2.epub': '分类2'}}"
        )

        user_prompt = f"请为以下书籍进行分类：\n{book_list_str}"

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "stream": False
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=60, connect=10)

                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()

                        if not response_text:
                            print(f"警告: API返回空响应 (尝试 {attempt + 1}/{max_retries})")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                                continue
                            return {}

                        return self._parse_response(response_text)

                    else:
                        error_text = await response.text()
                        print(f"API请求失败: {response.status} - {error_text}")

                        if response.status == 429:
                            print("遇到速率限制，等待5秒后重试...")
                            await asyncio.sleep(5)
                            continue

                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        return {}

            except asyncio.TimeoutError:
                print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                return {}

            except aiohttp.ClientPayloadError as e:
                print(f"传输编码错误: {e} (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                return {}

            except Exception as e:
                print(f"分类图书时出错: {e} (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                return {}

        return {}

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """解析 API 响应文本

        Args:
            response_text: API 响应文本

        Returns:
            分类结果字典
        """
        try:
            data = json.loads(response_text)

            if 'choices' not in data or not data['choices']:
                print(f"错误: API响应缺少choices字段: {data}")
                return {}

            content = data['choices'][0]['message']['content']

            if not content.strip():
                print("错误: content字段为空")
                return {}

            classification_result = json.loads(content)
            return classification_result

        except json.JSONDecodeError as parse_error:
            print(f"JSON解析失败: {parse_error}")
            print(f"尝试从响应中提取JSON模式...")

            try:
                json_match = re.search(r'\{[^{}]*\}', response_text)
                if json_match:
                    extracted_json = json.loads(json_match.group())
                    print(f"成功从响应中提取JSON: {extracted_json}")
                    return extracted_json
            except:
                print("提取的JSON仍然无效")

            return {}

        except (KeyError, IndexError) as parse_error:
            print(f"响应结构错误: {parse_error}")
            return {}

    def _build_prompt(self, titles: List[str], categories: List[str]) -> str:
        """构建 API 调用提示词（备用方法）

        Args:
            titles: 图书标题列表
            categories: 现有分类列表

        Returns:
            提示词字符串
        """
        category_list = ", ".join(categories) if categories else "无"
        book_list = "\n".join([f"- {title}" for title in titles])

        return (
            f"你是一个专业的图书分类系统。"
            f"现有分类如下: [{category_list}]。"
            f"请根据以下书名列表，为每本书从现有分类中选择一个最合适的分类标签。"
            f"如果都不匹配，可以根据书名内容创建一个新的、简洁的分类标签。"
            f"请以JSON格式返回结果。\n\n"
            f"书名列表:\n{book_list}"
        )
