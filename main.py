import asyncio
import random
import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig

BASE_URL = "https://hguofichp.cn:10086"

# 默认值（与 _conf_schema.json 保持一致）
DEFAULT_PAGE_SIZE = 200
DEFAULT_CONCURRENT_LIMIT = 8
DEFAULT_SEARCH_PAGES = 10


@register("astrbot_plugin_6657langen", "6657bot", "从 sb6657.cn 获取随机烂梗或按关键词搜索烂梗", "1.0.0")
class LangenPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config

    async def _fetch_json(self, session: aiohttp.ClientSession, url: str) -> dict | None:
        """通用 GET 请求，返回 JSON"""
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                data = await resp.json()
                if data.get("code") == 200:
                    return data
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"请求失败 {url}: {e}")
        return None

    @filter.command("烂梗", alias={"随机烂梗", "langen"})
    async def random_langen(self, event: AstrMessageEvent):
        """随机获取一条烂梗"""
        try:
            async with aiohttp.ClientSession() as session:
                data = await self._fetch_json(session, f"{BASE_URL}/machine/getRandOne")
                if data and data.get("data"):
                    barrage = data["data"].get("barrage", "（内容为空）")
                    meme_id = data["data"].get("id", "")
                    yield event.plain_result(f"🎲 随机烂梗 #{meme_id}\n\n{barrage}")
                else:
                    yield event.plain_result("获取烂梗失败，请稍后再试~")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"获取随机烂梗失败: {e}")
            yield event.plain_result("获取烂梗失败，网络异常，请稍后再试~")

    @filter.command("搜梗", alias={"查梗", "找梗", "sougen"})
    async def search_langen(self, event: AstrMessageEvent, keyword: str = ""):
        """根据关键词搜索烂梗，用法：/搜梗 关键词"""
        if not keyword.strip():
            yield event.plain_result("请输入要搜索的关键词，例如：/搜梗 donk")
            return

        keyword = keyword.strip()
        kw = keyword.lower()

        # 读取配置
        search_mode = self.config.get("search_mode", "full") if self.config else "full"
        page_size = self.config.get("page_size", DEFAULT_PAGE_SIZE) if self.config else DEFAULT_PAGE_SIZE
        concurrent_limit = self.config.get("concurrent_limit", DEFAULT_CONCURRENT_LIMIT) if self.config else DEFAULT_CONCURRENT_LIMIT
        search_pages = self.config.get("search_pages", DEFAULT_SEARCH_PAGES) if self.config else DEFAULT_SEARCH_PAGES

        try:
            async with aiohttp.ClientSession() as session:
                # 先获取总数
                first_page = await self._fetch_json(
                    session,
                    f"{BASE_URL}/machine/Page?tags=&pageNum=1&pageSize={page_size}",
                )
                if not first_page or not first_page.get("data"):
                    yield event.plain_result("搜索烂梗失败，请稍后再试~")
                    return

                total_items = first_page["data"].get("total", 0)
                total_pages = max(1, (total_items + page_size - 1) // page_size)

                # 从第一页结果中先筛选
                found = [
                    item for item in first_page["data"].get("list", [])
                    if kw in item.get("barrage", "").lower()
                ]

                # 根据搜索模式决定要扫描的页面
                if search_mode == "random":
                    pages_to_scan = random.sample(
                        range(2, total_pages + 1),
                        min(search_pages, total_pages - 1),
                    ) if total_pages > 1 else []
                else:
                    # 全站搜索：拉取所有剩余页面
                    pages_to_scan = list(range(2, total_pages + 1))

                # 使用信号量限制并发，通过 asyncio.gather 并发拉取
                semaphore = asyncio.Semaphore(concurrent_limit)

                async def _fetch_page(page_num: int) -> list:
                    async with semaphore:
                        page_data = await self._fetch_json(
                            session,
                            f"{BASE_URL}/machine/Page?tags=&pageNum={page_num}&pageSize={page_size}",
                        )
                        if page_data and page_data.get("data"):
                            return [
                                item for item in page_data["data"].get("list", [])
                                if kw in item.get("barrage", "").lower()
                            ]
                        return []

                results = await asyncio.gather(
                    *[_fetch_page(p) for p in pages_to_scan],
                    return_exceptions=True,
                )
                for result in results:
                    if isinstance(result, list):
                        found.extend(result)

                if not found:
                    yield event.plain_result(f"没有找到包含「{keyword}」的烂梗 😢")
                    return

                chosen = random.choice(found)
                barrage = chosen.get("barrage", "（内容为空）")
                meme_id = chosen.get("id", "")

                scanned = len(pages_to_scan) + 1  # +1 for first page
                if search_mode == "random":
                    scope_text = f"在随机抽样的 {scanned}/{total_pages} 页中"
                else:
                    scope_text = f"在全站 {total_items} 条烂梗中"

                yield event.plain_result(
                    f"🔍 搜索「{keyword}」{scope_text}"
                    f"找到 {len(found)} 条相关结果，随机一条：\n\n"
                    f"#{meme_id} {barrage}"
                )
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"搜索烂梗失败: {e}")
            yield event.plain_result("搜索烂梗失败，网络异常，请稍后再试~")
