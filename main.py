import random
import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

BASE_URL = "https://hguofichp.cn:10086"
PAGE_SIZE = 50  # 每页数量
SEARCH_PAGES = 10  # 搜索时扫描的页数


@register("astrbot_plugin_6657langen", "6657bot", "从 sb6657.cn 获取随机烂梗或按关键词搜索烂梗", "1.0.0")
class LangenPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def _fetch_json(self, session: aiohttp.ClientSession, url: str) -> dict | None:
        """通用 GET 请求，返回 JSON"""
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=15),
                ssl=False,
            ) as resp:
                data = await resp.json()
                if data.get("code") == 200:
                    return data
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
                    barrage = data["data"]["barrage"]
                    meme_id = data["data"].get("id", "")
                    yield event.plain_result(f"🎲 随机烂梗 #{meme_id}\n\n{barrage}")
                else:
                    yield event.plain_result("获取烂梗失败，请稍后再试~")
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
        try:
            async with aiohttp.ClientSession() as session:
                # 先获取总数
                first_page = await self._fetch_json(
                    session,
                    f"{BASE_URL}/machine/Page?tags=&pageNum=1&pageSize={PAGE_SIZE}",
                )
                if not first_page or not first_page.get("data"):
                    yield event.plain_result("搜索烂梗失败，请稍后再试~")
                    return

                total_items = first_page["data"].get("total", 0)
                total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)

                # 从第一页结果中先筛选
                found = [
                    item for item in first_page["data"].get("list", [])
                    if keyword.lower() in item.get("barrage", "").lower()
                ]

                # 随机选取更多页继续搜索
                pages_to_scan = random.sample(
                    range(2, total_pages + 1),
                    min(SEARCH_PAGES - 1, total_pages - 1),
                )
                for page_num in pages_to_scan:
                    page_data = await self._fetch_json(
                        session,
                        f"{BASE_URL}/machine/Page?tags=&pageNum={page_num}&pageSize={PAGE_SIZE}",
                    )
                    if page_data and page_data.get("data"):
                        for item in page_data["data"].get("list", []):
                            if keyword.lower() in item.get("barrage", "").lower():
                                found.append(item)

                if not found:
                    yield event.plain_result(f"没有找到包含「{keyword}」的烂梗 😢")
                    return

                chosen = random.choice(found)
                barrage = chosen["barrage"]
                meme_id = chosen.get("id", "")
                yield event.plain_result(
                    f"🔍 搜索「{keyword}」找到 {len(found)} 条相关结果，随机一条：\n\n"
                    f"#{meme_id} {barrage}"
                )
        except Exception as e:
            logger.error(f"搜索烂梗失败: {e}")
            yield event.plain_result("搜索烂梗失败，网络异常，请稍后再试~")
