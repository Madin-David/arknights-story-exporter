from __future__ import annotations

from bs4 import BeautifulSoup
from tqdm import tqdm
from common import Requester, Story

class StoryParser:
    def __init__(self, requester=None):
        self.PRTS_ROOT = "https://prts.wiki"
        self.STORY_URL = f"{self.PRTS_ROOT}/w/剧情一览"
        self.results = []
        self.requester = requester or Requester()
        self._parse()

    def _parse(self):
        response = self.requester.get(self.STORY_URL)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        # 所有 wikitable 是剧情表
        tables = soup.find_all("table", class_="wikitable")

        for table in tables:
            rows = table.find_all("tr")

            for row in rows:
                ths = row.find_all("th")

                # 跳过非剧情行
                if len(ths) < 2:
                    continue

                chapter = ths[0].get_text(strip=True)   # 第一列是章节名
                story_type = ths[1].get_text(strip=True)

                # 只提取存在关卡剧情链接的行
                tds = row.find_all("td")
                if not tds:
                    continue

                story_td = tds[0]

                # 提取关卡剧情标题 + 链接
                stories = []
                for a in story_td.find_all("a"):
                    title = a.get_text(strip=True)
                    href = a.get("href", "")

                    stories.append({
                        "title": title,
                        "url": f"{self.PRTS_ROOT}/{href}"
                    })

                # 保存章节
                self.results.append({
                    "chapter": chapter,
                    "type": story_type,
                    "stories": stories
                })

    def search_by_chapter(self, chapter_name):
        """通过章节名搜索，返回匹配的章节数据"""
        for result in self.results:
            if chapter_name in result["chapter"]:
                return result
        return None

    def search_by_story(self, story_name):
        """通过关卡名搜索，返回匹配的故事数据"""
        for result in self.results:
            for story in result["stories"]:
                if story_name in story["title"]:
                    return {
                        "chapter": result["chapter"],
                        "story": story
                    }
        return None

    def get_all_results(self):
        """获取所有解析结果"""
        return self.results

    def get_story_content_by_name(self, name: str) -> list[Story]:
        """通过章节名搜索并下载该章节下的所有剧情内容"""
        result = self.search_by_chapter(name)
        if not result:
            return []

        stories = []
        # 添加进度条，显示章节名
        chapter_display = f"{name[:12]}" if len(name) > 12 else f"{name:<12}"
        bar_format = f" {chapter_display}  [{{bar:20}}] {{percentage:3.0f}}% ({{n}}/{{total}}) | {{rate_fmt}}"

        with tqdm(
            total=len(result["stories"]),
            desc="",
            unit="",
            ncols=80,
            bar_format=bar_format,
            leave=True,
            position=0
        ) as pbar:
            for story in result["stories"]:
                url = story["url"]
                try:
                    response = self.requester.get(url)
                    html_content = response.text
                    soup = BeautifulSoup(html_content, "html.parser")

                    # 查找剧情内容，通常在特定的标签中
                    content_div = soup.find("div", class_="mw-parser-output")
                    if not content_div:
                        print(f"⚠ 无法在页面中找到剧情内容: {url}")
                        pbar.update(1)
                        continue

                    # 剧情脚本内容在 <pre id="datas_txt"> 中
                    datas_txt = content_div.find("pre", {"id": "datas_txt"})
                    if datas_txt:
                        # 直接使用剧情脚本内容
                        content = datas_txt.get_text()
                    else:
                        # 如果没有找到 datas_txt，则使用旧的清理逻辑
                        # 移除导航和无关部分
                        for unwanted in content_div.find_all("table"):
                            unwanted.decompose()
                        for unwanted in content_div.find_all("div", class_="navbox"):
                            unwanted.decompose()
                        # 移除其他常见的导航元素，包括 navigation-not-searchable
                        for unwanted in content_div.find_all(class_=["mw-editsection", "toc", "noprint", "navigation-not-searchable"]):
                            unwanted.decompose()

                        # 获取文本内容
                        content = content_div.get_text(separator="\n", strip=True)

                    story_obj = Story(name=story["title"], origin_content=content)
                    stories.append(story_obj)

                    # 更新进度条
                    pbar.update(1)
                except Exception as e:
                    print(f"⚠ 获取故事 '{story['title']}' 时出错: {e}")
                    pbar.update(1)
                    continue

        return stories
