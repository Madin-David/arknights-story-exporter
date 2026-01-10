#!/usr/bin/env python3
"""
extract_characters.py

从游戏脚本样式的文本文件中提取所有角色名。

用法:
    python extract_characters.py [输入文件]

示例:
    python extract_characters.py story_凯尔希_1.txt

输出:
    将提取到的角色名列表输出到控制台，每行一个角色名。
"""
import re
import sys
from collections import OrderedDict


def extract_characters(text):
    """从文本中提取所有角色名。
    
    Args:
        text: 待解析的文本字符串
        
    Returns:
        去重后的角色名列表（保持出现顺序）
    """
    characters = OrderedDict()  # 使用 OrderedDict 保持顺序并去重
    
    # 模式1: [name="角色名"]对话内容
    pattern1 = r'\[name\s*=\s*"([^"]+)"\]'
    
    # 模式2: name="角色名"]对话内容 (缺少开括号)
    pattern2 = r'name\s*=\s*"([^"]+)"\]'
    
    # 匹配所有角色名
    for pattern in [pattern1, pattern2]:
        matches = re.findall(pattern, text)
        for match in matches:
            character = match.strip()
            if character:  # 忽略空字符串
                characters[character] = True
    
    return list(characters.keys())


def extract_characters_from_file(filepath):
    """从文件中读取文本并提取角色名。
    
    Args:
        filepath: 输入文件路径
        
    Returns:
        角色名列表
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        return extract_characters(text)
    except FileNotFoundError:
        print(f'错误: 文件 "{filepath}" 不存在', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'错误: 读取文件时出错: {e}', file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print('用法: python extract_characters.py [输入文件]', file=sys.stderr)
        print('示例: python extract_characters.py story_凯尔希_1.txt', file=sys.stderr)
        sys.exit(1)
    
    filepath = sys.argv[1]
    characters = extract_characters_from_file(filepath)
    
    if characters:
        print(f'找到 {len(characters)} 个角色:')
        for char in characters:
            print(char)
    else:
        print('未找到任何角色名')


if __name__ == '__main__':
    main()

