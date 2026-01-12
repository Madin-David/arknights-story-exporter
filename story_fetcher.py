#!/usr/bin/env python3
"""
story_fetcher.py

支持：
 - 传入多个章节名或故事名（命令行多个参数或通过文件）
 - 为每个章节/故事分别输出 docx 或合并为一个 docx

用法示例:
    python story_fetcher.py 反常光谱
    python story_fetcher.py -f names.txt --combined -o all_stories.docx
    python story_fetcher.py 反常光谱 -o outputs/  # 默认按章节/故事输出
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from typing import List, Set

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from tqdm import tqdm
from common import Requester, Story, load_names
from parse_text_to_docx import DocumentAssembler
from search_memory import PRTSClient
from search_story import StoryParser


# ============================================
# 终端输出格式化工具
# ============================================

class Colors:
    """ANSI 颜色代码"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # 亮色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


def print_separator(width=60):
    """打印分隔线"""
    print(f"{Colors.DIM}{'─' * width}{Colors.RESET}")


def print_timestamp_log(emoji, message, color=Colors.CYAN):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {emoji} {color}{message}{Colors.RESET}")


def print_task_header(names: List[str], mode: str, output: str):
    """打印任务开始横幅"""
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}🔄 故事下载任务开始{Colors.RESET}")
    print_separator()
    print(f"{Colors.BOLD}任务配置:{Colors.RESET}")

    # 故事列表
    stories_display = ", ".join(names) if len(names) <= 3 else f"{', '.join(names[:3])}, ... (共{len(names)}个)"
    print(f"  {Colors.DIM}·{Colors.RESET} 故事: {Colors.YELLOW}{stories_display}{Colors.RESET}")
    print(f"  {Colors.DIM}·{Colors.RESET} 模式: {Colors.YELLOW}{mode}{Colors.RESET}")
    print(f"  {Colors.DIM}·{Colors.RESET} 目标: {Colors.YELLOW}{output}{Colors.RESET}")
    print_separator()


def print_task_summary(total_stories: int, elapsed_time: float, output_path: str):
    """打印任务总结"""
    print_separator()
    print(f"{Colors.BOLD}{Colors.GREEN}✅ 所有任务完成！{Colors.RESET}")

    # 格式化耗时
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_str = f"{minutes}分{seconds}秒" if minutes > 0 else f"{seconds}秒"

    print(f" {Colors.DIM}总计:{Colors.RESET} {Colors.CYAN}{total_stories}{Colors.RESET} 个故事 | "
          f"{Colors.DIM}总耗时:{Colors.RESET} {Colors.CYAN}{time_str}{Colors.RESET}")
    print(f" {Colors.DIM}输出文件:{Colors.RESET} {Colors.GREEN}{output_path}{Colors.RESET} (已保存)")
    print()


class StoryPRTSClient:
    """故事客户端，封装 StoryParser 的功能，提供缓存和便捷接口"""
    
    CACHE_FILE = "story_cache.json"

    def __init__(self, use_cache=True, requester=None):
        self.requester = requester or Requester()
        self.use_cache = use_cache
        self.initialized = False
        
        self.story_cache = None  # 全量故事缓存
        self.parser = None       # StoryParser 实例
        
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

            # 故事数据
            if "stories" in data:
                self.story_cache = data["stories"]
                print_timestamp_log("🔍", f"已加载 {len(self.story_cache)} 条缓存记录")
                self.initialized = True

        except Exception as e:
            print_timestamp_log("⚠️", f"无法读取缓存: {e}", Colors.YELLOW)
    
    def _save_cache(self):
        """保存缓存文件"""
        data = {}
        
        # 保存故事
        if self.story_cache is not None:
            data["stories"] = self.story_cache
        
        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("💾 缓存已保存。")
    
    # ------------------------------------------------------
    # 初始化解析器
    # ------------------------------------------------------
    def _init_parser(self):
        """初始化 StoryParser，如果已初始化则跳过"""
        if self.parser is not None:
            return

        print_timestamp_log("⚙️", "故事解析器初始化成功")
        self.parser = StoryParser(requester=self.requester)
    
    # ------------------------------------------------------
    # 全量故事数据
    # ------------------------------------------------------
    def get_all_story(self):
        """返回全量故事数据，优先使用本地缓存"""
        if self.story_cache is not None:
            return self.story_cache
        
        print("⬇ 正在从服务器加载全量故事数据 ...")
        
        self._init_parser()
        results = self.parser.get_all_results()
        
        print(f"✔ 已获取 {len(results)} 条故事记录")
        
        # 保存缓存
        self.story_cache = results
        self._save_cache()
        
        return results
    
    # ------------------------------------------------------
    # 搜索故事（完全本地，不请求服务器）
    # ------------------------------------------------------
    def search_story(self, name):
        """在缓存中搜索包含指定名称的故事"""
        results = self.get_all_story()  # 保证已经加载缓存或从服务器获得
        
        matches = []
        for result in results:
            # 检查章节名
            if name in result["chapter"]:
                matches.append({
                    "type": "chapter",
                    "chapter": result["chapter"],
                    "type_name": result["type"],
                    "stories": result["stories"]
                })
            # 检查故事标题
            for story in result["stories"]:
                if name in story["title"]:
                    matches.append({
                        "type": "story",
                        "chapter": result["chapter"],
                        "type_name": result["type"],
                        "story": story
                    })
        
        return matches
    
    def get_story_content_by_name(self, name: str) -> list[Story]:
        """获取指定名称的故事内容（通过章节名或故事名）
        
        如果找到章节，返回该章节下的所有故事
        如果找到故事，返回该故事所在章节下的所有故事
        """
        self._init_parser()
        
        # 先尝试通过章节名搜索
        chapter_result = self.parser.search_by_chapter(name)
        if chapter_result:
            return self.parser.get_story_content_by_name(name)
        
        # 如果章节名没找到，尝试通过故事名搜索
        story_result = self.parser.search_by_story(name)
        if story_result:
            # 找到故事后，获取该故事所在章节的所有故事
            chapter_name = story_result["chapter"]
            return self.parser.get_story_content_by_name(chapter_name)
        
        # 都没找到
        return []


# ------------------------------------------------------
# 角色名称提取和秘录获取
# ------------------------------------------------------
def extract_character_names(story_content: str) -> Set[str]:
    """从故事文本中提取角色名称
    
    支持两种格式:
    1. Markdown 格式: **角色名:** 或 **角色名：**
    2. 游戏脚本格式: [name="角色名"] 或 name="角色名"]
    """
    names = set()
    
    # 模式1: Markdown 格式 **角色名:** 或 **角色名：**
    pattern1 = r'\*\*([^*:：]+?)[:：]\*\*'
    matches1 = re.findall(pattern1, story_content)
    names.update(name.strip() for name in matches1 if name.strip())
    
    # 模式2: 游戏脚本格式 [name="角色名"]对话内容
    pattern2 = r'\[name\s*=\s*"([^"]+)"\]'
    matches2 = re.findall(pattern2, story_content)
    names.update(name.strip() for name in matches2 if name.strip())
    
    # 模式3: 游戏脚本格式 name="角色名"]对话内容 (缺少开括号)
    pattern3 = r'name\s*=\s*"([^"]+)"\]'
    matches3 = re.findall(pattern3, story_content)
    names.update(name.strip() for name in matches3 if name.strip())
    
    # 过滤掉一些明显不是角色名的内容（如音效、场景描述等）
    filtered_names = set()
    for name in names:
        # 跳过太短的名字（可能是标点符号）
        if len(name) < 2:
            continue
        # 跳过包含特殊符号的（可能是音效标记），但允许游戏脚本格式中的引号
        if any(c in name for c in ['<', '>', '(', ')', '[', ']']):
            continue
        filtered_names.add(name)
    
    return filtered_names


def get_characters_memory(memory_client: PRTSClient, character_names: Set[str], verbose: bool = False) -> dict:
    """获取多个角色的秘录

    返回: {角色名: [Story对象列表]}
    """
    result = {}
    # 添加进度条
    desc = f"{'秘录':<6} [获取中...]"
    with tqdm(
        total=len(character_names),
        desc=desc,
        unit="个",
        ncols=100,
        disable=not verbose,
        leave=True,
        position=0
    ) as pbar:
        for char_name in character_names:
            try:
                memories = memory_client.get_story_content_by_name(char_name)
                if memories:
                    result[char_name] = memories
                pbar.update(1)
            except Exception as e:
                if verbose:
                    print(f"  ✗ 获取角色 '{char_name}' 的秘录时出错: {e}")
                pbar.update(1)
    return result


def append_memory_to_content(asm: DocumentAssembler, memory_dict: dict, verbose: bool = False):
    """将秘录内容附加到文档中"""
    if not memory_dict:
        return

    # 添加分页符，使"相关角色秘录"另起一页
    asm.add_page_break()

    # 添加分隔标题（仅标题，不解析文本）
    asm.add_title("相关角色秘录")

    for char_name, memories in memory_dict.items():
        for memory in memories:
            title = getattr(memory, 'name', None) or f"{char_name}的秘录"
            # 格式: 角色名：秘录标题
            full_title = f"{char_name}：{title}"
            content = getattr(memory, 'origin_content', None)
            if content and content.strip():
                asm.parse_text(content, title=full_title)
                if verbose:
                    print(f"    已附加秘录: {full_title}")


def save_per_chapter(client: StoryPRTSClient, name: str, out_dir: str, verbose: bool,
                     with_memory: bool = False, memory_client: PRTSClient = None):
    """为每个章节/故事单独生成 docx 文件"""
    stories = client.get_story_content_by_name(name)
    if not stories:
        if verbose:
            print(f"未找到 `{name}` 的故事，跳过")
        return 0

    # ensure output dir
    os.makedirs(out_dir, exist_ok=True)
    # 使用安全的文件名（移除特殊字符）
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    outpath = os.path.join(out_dir, f"{safe_name}_story.docx")

    asm = DocumentAssembler()
    included = 0
    all_character_names = set()  # 收集所有故事中的角色名

    # 添加大标题（章节名）
    asm.add_main_title(name)

    # 添加进度条，显示章节名
    chapter_display = f"{name[:18]}" if len(name) > 18 else name
    desc = f"{'解析':<6} [{chapter_display}]"
    with tqdm(
        total=len(stories),
        desc=desc,
        unit="个",
        ncols=100,
        disable=not verbose,
        leave=True,
        position=0
    ) as pbar:
        for idx, s in enumerate(stories, start=1):
            title = getattr(s, 'name', None) or f"{name} #{idx}"
            origin = getattr(s, 'origin_content', None)
            image_map = getattr(s, 'image_map', {})
            if origin and origin.strip():
                asm.parse_text(origin, title=title, image_map=image_map)
                included += 1

                # 如果启用了秘录功能，提取角色名
                if with_memory and memory_client:
                    char_names = extract_character_names(origin)
                    all_character_names.update(char_names)

                pbar.update(1)
            else:
                if verbose:
                    print(f"{name} 的条目 `{title}` 内容为空，已跳过")
                pbar.update(1)

    # 附加秘录
    if with_memory and memory_client and all_character_names:
        if verbose:
            print(f"  正在提取角色名称并获取秘录...")
            print(f"  找到 {len(all_character_names)} 个角色: {', '.join(sorted(all_character_names))}")
        memory_dict = get_characters_memory(memory_client, all_character_names, verbose)
        if memory_dict:
            append_memory_to_content(asm, memory_dict, verbose)

    if included > 0:
        try:
            asm.save(outpath)
            if verbose:
                memory_info = f"，包含 {len(all_character_names)} 个角色的秘录" if with_memory and all_character_names else ""
                print(f"已为 `{name}` 生成: {outpath} （包含 {included} 条故事{memory_info}）")
        except PermissionError as e:
            error_msg = f"无法保存文件 `{outpath}`: 权限被拒绝"
            if os.path.exists(outpath):
                error_msg += f"\n提示: 文件可能正在被其他程序打开（如 Word），请关闭该文件后重试"
            else:
                error_msg += f"\n提示: 请检查目录写入权限或文件路径是否正确"
            raise PermissionError(error_msg) from e
    return included


def save_combined(client: StoryPRTSClient, names: List[str], outpath: str, verbose: bool,
                  with_memory: bool = False, memory_client: PRTSClient = None):
    """将所有章节/故事合并到一个 docx 文件"""
    # 记录开始时间
    start_time = time.time()

    # 打印任务横幅
    print_task_header(names, "合并输出", outpath)

    asm = DocumentAssembler()
    total_included = 0
    all_character_names = set()  # 收集所有故事中的角色名
    first_section = True  # 标记是否为第一个章节

    # 计算总故事数并预先获取所有故事
    print()
    print(f"{Colors.BOLD}下载进度:{Colors.RESET}")
    chapters_data = []
    for name in names:
        stories = client.get_story_content_by_name(name)
        if stories:
            chapters_data.append((name, stories))

    # 计算总故事数
    total_stories = sum(len(stories) for _, stories in chapters_data)

    # 解析阶段 - 不显示进度条，静默处理
    print_separator()
    for chapter_idx, (name, stories) in enumerate(chapters_data, 1):
        # 如果是第一个章节，添加大标题
        if first_section and names:
            # 使用第一个章节名作为大标题，如果有多个章节则显示合并标题
            if len(names) == 1:
                asm.add_main_title(name)
            else:
                # 多个章节合并时，使用第一个章节名作为大标题
                asm.add_main_title(name)
            first_section = False

        for idx, s in enumerate(stories, start=1):
            title = getattr(s, 'name', None) or f"{name} #{idx}"
            # 格式: 章节名：故事标题（每条故事都包含章节名）
            full_title = f"{name}：{title}"
            origin = getattr(s, 'origin_content', None)
            image_map = getattr(s, 'image_map', {})
            if origin and origin.strip():
                asm.parse_text(origin, title=full_title, image_map=image_map)
                total_included += 1

                # 如果启用了秘录功能，提取角色名
                if with_memory and memory_client:
                    char_names = extract_character_names(origin)
                    all_character_names.update(char_names)
            else:
                if verbose:
                    print(f"{name} 的条目 `{title}` 内容为空，已跳过")

    # 附加秘录
    if with_memory and memory_client and all_character_names:
        if verbose:
            print(f"  正在提取角色名称并获取秘录...")
            print(f"  找到 {len(all_character_names)} 个角色: {', '.join(sorted(all_character_names))}")
        memory_dict = get_characters_memory(memory_client, all_character_names, verbose)
        if memory_dict:
            append_memory_to_content(asm, memory_dict, verbose)

    if total_included == 0:
        if verbose:
            print("未找到任何可写入的故事，未生成文件。")
        return 0

    # ensure parent dir
    outdir = os.path.dirname(outpath)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    try:
        asm.save(outpath)
        # 计算总耗时
        elapsed_time = time.time() - start_time
        # 打印任务总结
        print_task_summary(total_included, elapsed_time, outpath)
    except PermissionError as e:
        error_msg = f"无法保存文件 `{outpath}`: 权限被拒绝"
        if os.path.exists(outpath):
            error_msg += f"\n提示: 文件可能正在被其他程序打开（如 Word），请关闭该文件后重试"
        else:
            error_msg += f"\n提示: 请检查目录写入权限或文件路径是否正确"
        raise PermissionError(error_msg) from e
    return total_included


def main():
    """主函数，处理命令行参数并执行相应的操作"""
    parser = argparse.ArgumentParser(description="搜索故事并导出为 Word 文档（支持多章节、多故事）")
    parser.add_argument("names", nargs="*", help="章节名或故事名（可以指定多个），若使用 -f 则可省略此项")
    parser.add_argument("-f", "--names-file", help="从文件读取章节名或故事名，每行一个")
    parser.add_argument("--combined", action="store_true", help="将所有章节/故事合并到一个 docx 文件（默认按章节输出）")
    parser.add_argument("-o", "--out", help="输出文件或目录。若 --combined 则为输出文件路径，否则为输出目录（默认: 当前目录）")
    parser.add_argument("--no-cache", action="store_true", help="不使用本地缓存，强制从服务器拉取")
    parser.add_argument("--with-memory", action="store_true", help="提取剧情中的角色名并附加相关角色的秘录")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示更多调试信息")
    args = parser.parse_args()

    try:
        names = load_names(args.names, args.names_file, entity_label="章节名或故事名")
    except (RuntimeError, ValueError) as exc:
        parser.error(str(exc))

    client = StoryPRTSClient(use_cache=not args.no_cache)
    
    # 如果启用了秘录功能，初始化秘录客户端
    memory_client = None
    if args.with_memory:
        try:
            memory_client = PRTSClient()
            if args.verbose:
                print("✓ 秘录客户端已初始化")
        except Exception as e:
            print(f"⚠ 初始化秘录客户端失败: {e}，将跳过秘录功能")
            args.with_memory = False

    # 如果用户请求合并输出
    if args.combined:
        outpath = args.out if args.out else "combined_story.docx"
        try:
            count = save_combined(client, names, outpath, verbose=args.verbose,
                                 with_memory=args.with_memory, memory_client=memory_client)
            if count == 0:
                sys.exit(3)
        except Exception as e:
            print("生成合并文件出错:", e)
            sys.exit(4)
        return

    # per-chapter 输出（默认）
    out_dir = args.out if args.out else os.getcwd()
    total = 0
    for name in names:
        try:
            c = save_per_chapter(client, name, out_dir, verbose=args.verbose,
                               with_memory=args.with_memory, memory_client=memory_client)
            total += c
        except Exception as e:
            print(f"为 `{name}` 生成文件出错:", e)

    if total == 0:
        print("未生成任何文件（可能未找到匹配的故事）。")
        sys.exit(3)


if __name__ == '__main__':
    main()
