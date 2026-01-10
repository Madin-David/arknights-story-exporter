#!/usr/bin/env python3
"""公共模块，包含共享的类和工具函数。"""
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests


class Requester:
    """HTTP 请求器，带延迟控制"""
    
    def __init__(self, delay: float = 0.5):
        self.session = requests.Session()
        self.delay = delay

    def get(self, *args, **kwargs):
        """发送 GET 请求，并在请求后延迟指定时间"""
        resp = self.session.get(*args, **kwargs)
        time.sleep(self.delay)
        return resp


@dataclass
class Story:
    """故事/密录数据类"""
    
    name: str = ""
    intro: str = ""
    origin_content: str = ""


def _normalize_names(names: Iterable[str]) -> List[str]:
    """去除空白并保持去重顺序"""
    seen = set()
    normalized: List[str] = []
    for raw in names or []:
        cleaned = raw.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)
    return normalized


def read_names_from_file(path: str) -> List[str]:
    """从文件读取名称列表"""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return _normalize_names(file.readlines())
    except OSError as exc:
        raise RuntimeError(f"读取名字文件失败: {exc}") from exc


def load_names(cli_names: Iterable[str], names_file: Optional[str] = None, *, entity_label: str = "名称") -> List[str]:
    """统一的名字收集入口，支持命令行与文件输入"""
    collected: List[str] = []
    if names_file:
        collected.extend(read_names_from_file(names_file))
    collected.extend(_normalize_names(cli_names))
    if not collected:
        raise ValueError(f"需要至少指定一个{entity_label}（命令行或通过 -f 文件）")
    return collected


