from __future__ import annotations

import json
import os
from urllib.parse import urlencode, quote
from bs4 import BeautifulSoup
from common import Requester, Story

class PRTSClient:
    HOME = "https://prts.wiki/"
    API = "https://prts.wiki/api.php"

    CACHE_FILE = "prts_cache.json"

    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://prts.wiki/",
        "Accept": "text/html,application/xhtml+xml",
    }

    def __init__(self, use_cache=True, requester=None):
        self.requester = requester or Requester()
        self.session = self.requester.session
        self.initialized = False
        self.use_cache = use_cache

        self.memory_cache = None     # 全量密录缓存
        self.cookie_cache = None     # Cookie 缓存

        if use_cache:
            self._load_cache()

    # ------------------------------------------------------
    # 缓存系统
    # ------------------------------------------------------
    def _load_cache(self):
        """加载本地缓存"""
        if not os.path.exists(self.CACHE_FILE):
            return

        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Cookie
            if "cookies" in data:
                for k, v in data["cookies"].items():
                    self.session.cookies.set(k, v)
                print("✔ 已加载缓存 Cookie")
                self.initialized = True

            # 密录数据
            if "char_memory" in data:
                self.memory_cache = data["char_memory"]
                print(f"✔ 已加载缓存密录记录：{len(self.memory_cache)} 条")

        except Exception as e:
            print("⚠ 无法读取缓存:", e)

    def _save_cache(self):
        """保存缓存文件"""
        data = {}

        # 保存 Cookie
        data["cookies"] = {k: v for k, v in self.session.cookies.items()}

        # 保存密录
        if self.memory_cache is not None:
            data["char_memory"] = self.memory_cache

        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("💾 缓存已保存。")

    # ------------------------------------------------------
    # 初始化 Cookie
    # ------------------------------------------------------
    def init(self):
        """若已有缓存 Cookie则直接使用，否则访问首页获取新的 Cookie"""
        if self.initialized:
            return

        print("🌐 初始化：正在获取 PRTS Cookie ...")

        r = self.requester.get(self.HOME, headers=self.BASE_HEADERS)
        r.raise_for_status()

        print("✔ Cookie 初始化成功：")
        for k, v in self.session.cookies.items():
            print("  ", k, "=", v)

        self.initialized = True
        self._save_cache()

    def refresh(self):
        """强制重新获取 Cookie"""
        print("🔄 刷新 Cookie ...")
        self.session.cookies.clear()
        self.initialized = False
        self.init()

    # ------------------------------------------------------
    # Cargo Query
    # ------------------------------------------------------
    def cargoquery(self, tables, fields, where=None, limit=5000):
        self.init()  # 自动初始化 Cookie

        params = {
            "action": "cargoquery",
            "format": "json",
            "tables": tables,
            "fields": fields,
            "limit": str(limit),
        }

        if where:
            params["where"] = where

        url = self.API + "?" + urlencode(params, quote_via=quote)

        r = self.session.get(url, headers=self.BASE_HEADERS)
        r.raise_for_status()

        data = r.json()
        return data.get("cargoquery", []), data

    # ------------------------------------------------------
    # 全量密录数据（MemoryList同款）
    # ------------------------------------------------------
    def get_all_memory(self):
        """返回全量密录数据，优先使用本地缓存"""
        if self.memory_cache is not None:
            return self.memory_cache

        print("⬇ 正在从服务器加载全量密录数据 ...")

        fields = (
            "_pageName=page,elite,level,favor,"
            "storySetName,storyIntro,storyTxt,storyIndex,medal"
        )

        rows, raw = self.cargoquery(
            tables="char_memory",
            fields=fields,
            limit=5000
        )

        print(f"✔ 已获取 {len(rows)} 条密录记录")

        # 保存缓存
        self.memory_cache = rows
        self._save_cache()

        return rows

    # ------------------------------------------------------
    # 搜索某干员密录（完全本地，不请求服务器）
    # ------------------------------------------------------
    def search_memory(self, name):
        """在缓存中搜索 page == 干员名 的密录"""
        rows = self.get_all_memory()  # 保证已经加载缓存或从服务器获得

        result = [r for r in rows if r["title"]["page"] == name]
        return result

    def get_story_content_by_name(self, name: str) -> list[Story]:
        """获取指定干员的未解析密录文本内容"""
        entries = self.search_memory(name)
        stories = []
        for entry in entries:
            url = f"{self.HOME}w/{entry['title']['storyTxt']}"
            try:
                html = self.session.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                content = soup.find("pre", id="datas_txt")
                if content is None:
                    raise ValueError(f"无法找到密录内容的预格式化文本块，页面结构可能已更改: {url}")
                content = content.get_text()
                story = Story(
                    name=entry['title']['storySetName'],
                    intro=entry['title']['storyIntro'],
                    origin_content=content
                )
                stories.append(story)
            except Exception as e:
                print(f"⚠ 获取密录 '{entry['title']['storySetName']}' 时出错: {e}")
                continue

        return stories