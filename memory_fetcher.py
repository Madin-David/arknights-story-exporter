#!/usr/bin/env python3
"""
main.py

支持：
 - 传入多个角色名（命令行多个参数或通过文件）
 - 为每个角色分别输出 docx 或合并为一个 docx

用法示例:
    python main.py 阿米娅 德克萨斯
    python main.py -f names.txt --combined -o all_chars.docx
    python main.py 阿米娅 -o outputs/  # 默认按角色单独输出
"""
import argparse
import os
import sys
from typing import List

from common import load_names
from search_memory import PRTSClient
from parse_text_to_docx import DocumentAssembler


def save_per_character(client: PRTSClient, name: str, out_dir: str, verbose: bool):
    stories = client.get_story_content_by_name(name)
    if not stories:
        if verbose:
            print(f"未找到 `{name}` 的密录，跳过")
        return 0

    # ensure output dir
    os.makedirs(out_dir, exist_ok=True)
    outpath = os.path.join(out_dir, f"{name}_memory.docx")

    asm = DocumentAssembler()
    included = 0
    for idx, s in enumerate(stories, start=1):
        title = getattr(s, 'name', None) or f"{name} #{idx}"
        origin = getattr(s, 'origin_content', None)
        if origin and origin.strip():
            asm.parse_text(origin, title=title)
            included += 1
        else:
            if verbose:
                print(f"{name} 的条目 `{title}` 内容为空，已跳过")

    if included > 0:
        asm.save(outpath)
        if verbose:
            print(f"已为 `{name}` 生成: {outpath} （包含 {included} 条密录）")
    return included


def save_combined(client: PRTSClient, names: List[str], outpath: str, verbose: bool):
    asm = DocumentAssembler()
    total_included = 0
    for name in names:
        stories = client.get_story_content_by_name(name)
        if not stories:
            if verbose:
                print(f"未找到 `{name}` 的密录，跳过")
            continue

        for idx, s in enumerate(stories, start=1):
            title = getattr(s, 'name', None) or f"{name} #{idx}"
            # 格式: 角色名：秘录标题（无空格，每条秘录都包含角色名）
            full_title = f"{name}：{title}"
            origin = getattr(s, 'origin_content', None)
            if origin and origin.strip():
                asm.parse_text(origin, title=full_title)
                total_included += 1
            else:
                if verbose:
                    print(f"{name} 的条目 `{title}` 内容为空，已跳过")

    if total_included == 0:
        if verbose:
            print("未找到任何可写入的密录，未生成文件。")
        return 0

    # ensure parent dir
    outdir = os.path.dirname(outpath)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    asm.save(outpath)
    if verbose:
        print(f"已生成合并文件: {outpath} （包含 {total_included} 条密录）")
    return total_included


def main():
    parser = argparse.ArgumentParser(description="搜索密录并导出为 Word 文档（支持多角色、多秘录）")
    parser.add_argument("names", nargs="*", help="角色名（可以指定多个），若使用 -f 则可省略此项")
    parser.add_argument("-f", "--names-file", help="从文件读取角色名，每行一个")
    parser.add_argument("--combined", action="store_true", help="将所有角色的密录合并到一个 docx 文件（默认按角色单独生成）")
    parser.add_argument("-o", "--out", help="输出文件或目录。若 --combined 则为输出文件路径，否则为输出目录（默认: 当前目录）")
    parser.add_argument("--no-cache", action="store_true", help="不使用本地缓存，强制从服务器拉取")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示更多调试信息")
    args = parser.parse_args()

    try:
        names = load_names(args.names, args.names_file, entity_label="角色名")
    except (RuntimeError, ValueError) as exc:
        parser.error(str(exc))

    client = PRTSClient(use_cache=not args.no_cache)

    # 如果用户请求合并输出
    if args.combined:
        outpath = args.out if args.out else "combined_memory.docx"
        try:
            count = save_combined(client, names, outpath, verbose=args.verbose)
            if count == 0:
                sys.exit(3)
        except Exception as e:
            print("生成合并文件出错:", e)
            sys.exit(4)
        return

    # per-character 输出（默认）
    out_dir = args.out if args.out else os.getcwd()
    total = 0
    for name in names:
        try:
            c = save_per_character(client, name, out_dir, verbose=args.verbose)
            total += c
        except Exception as e:
            print(f"为 `{name}` 生成文件出错:", e)

    if total == 0:
        print("未生成任何文件（可能未找到匹配的密录）。")
        sys.exit(3)


if __name__ == '__main__':
    main()
