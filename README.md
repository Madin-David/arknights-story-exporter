# PRTS 故事与密录导出工具

一个用于从 PRTS Wiki（明日方舟中文 Wiki）爬取游戏剧情、角色密录并导出为格式化 Word 文档的 Python 工具集。

## 功能特性

- 🎮 **主线剧情导出**: 按章节名搜索并导出主线故事到 Word 文档
- 👤 **角色密录导出**: 按角色名搜索并导出角色密录到 Word 文档
- 📝 **智能格式化**: 自动解析游戏脚本并按照专业排版规范生成文档
- 💾 **本地缓存**: 智能缓存机制，减少重复网络请求
- 🔗 **关联秘录**: 自动提取剧情中的角色并附加相关秘录（可选）
- 📦 **批量处理**: 支持处理多个章节/角色，支持从文件读取列表
- 🎯 **灵活输出**: 可按角色/章节单独输出或合并为一个文档
- 🎨 **美观终端**: 彩色输出、实时进度条、时间戳日志、任务总结

## 安装

### 环境要求

- Python 3.7+

### 安装依赖

```bash
pip install -r requirements.txt
```

依赖包包括：
- `python-docx`: Word 文档生成
- `beautifulsoup4`: HTML 解析
- `requests`: HTTP 请求
- `tqdm`: 进度条显示

## 使用方法

### 1. 导出角色密录 (memory_fetcher.py)

#### 基本用法

```bash
# 导出单个角色的密录
python memory_fetcher.py 阿米娅

# 导出多个角色的密录（按角色分别输出）
python memory_fetcher.py 阿米娅 德克萨斯 能天使

# 从文件读取角色名（每行一个）
python memory_fetcher.py -f names.txt

# 合并所有角色密录到一个文件
python memory_fetcher.py 阿米娅 德克萨斯 --combined -o all_memory.docx

# 指定输出目录
python memory_fetcher.py 阿米娅 -o outputs/

# 强制从服务器重新拉取（不使用缓存）
python memory_fetcher.py 阿米娅 --no-cache

# 显示详细信息和进度
python memory_fetcher.py 阿米娅 -v
```

#### 输出文件

- 单独输出: `{角色名}_memory.docx`
- 合并输出: 用户指定的文件名（默认 `combined_memory.docx`）

### 2. 导出主线剧情 (story_fetcher.py)

#### 基本用法

```bash
# 导出单个章节的故事
python story_fetcher.py 反常光谱

# 导出多个章节的故事
python story_fetcher.py 反常光谱 孤岛风云

# 从文件读取章节名
python story_fetcher.py -f chapters.txt

# 合并所有章节到一个文件
python story_fetcher.py 反常光谱 --combined -o all_stories.docx

# 自动提取角色并附加相关密录
python story_fetcher.py 反常光谱 --with-memory

# 指定输出目录
python story_fetcher.py 反常光谱 -o outputs/

# 强制从服务器重新拉取
python story_fetcher.py 反常光谱 --no-cache

# 显示详细信息和进度
python story_fetcher.py 反常光谱 -v --with-memory
```

#### 终端输出示例

工具提供专业的彩色终端输出，包括任务横幅、实时进度条和完成总结：

```
🔄 故事下载任务开始
────────────────────────────────────────────────────────
任务配置:
  · 故事: 反常光谱
  · 模式: 合并输出
  · 目标: all_stories.docx
────────────────────────────────────────────────────────

下载进度:
────────────────────────────────────────────────────────
 反常光谱      [████████████████████] 100% (27/27) | 1.2it/s

────────────────────────────────────────────────────────
✅ 所有任务完成！
 总计: 27 个故事 | 总耗时: 1分23秒
 输出文件: all_stories.docx (已保存)
```

#### 输出文件

- 单独输出: `{章节名}_story.docx`
- 合并输出: 用户指定的文件名（默认 `combined_story.docx`）

### 3. 解析游戏脚本到 Word (parse_text_to_docx.py)

```bash
# 将游戏脚本文本文件转换为格式化的 Word 文档
python parse_text_to_docx.py input.txt output.docx

# 显示详细信息（包括跳过的行）
python parse_text_to_docx.py input.txt output.docx -v
```

### 4. 提取角色名 (extract_characters.py)

```bash
# 从脚本文件中提取所有出现的角色名
python extract_characters.py story_凯尔希_1.txt
```

## 命令行参数详解

### 通用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `names` | 位置参数，角色名/章节名列表 | `阿米娅 德克萨斯` |
| `-f`, `--names-file` | 从文件读取名称列表（每行一个） | `-f names.txt` |
| `-o`, `--out` | 输出文件或目录 | `-o output.docx` 或 `-o outputs/` |
| `--combined` | 合并所有内容到一个文件 | `--combined` |
| `--no-cache` | 不使用缓存，强制重新拉取 | `--no-cache` |
| `-v`, `--verbose` | 显示详细调试信息和进度条 | `-v` |

### story_fetcher.py 特有参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--with-memory` | 自动提取角色并附加相关密录 | `--with-memory` |

## 文档格式说明

### 页面设置

- **页面大小**: A4 (210mm × 297mm / 8.27" × 11.69")
- **页边距**: 窄边距 (1.27cm / 0.5") - 默认设置
  - 可选: 标准边距 (2cm) 或 宽边距 (2.54cm)
- **页码**: 底部居中自动显示
- **行距**: 1.5 倍行距
- **字体**: 默认中文字体 宋体 12pt

### 内容格式

- **大标题**: 黑体 22pt，左对齐（章节/故事主标题）
- **小标题**: 黑体 18pt，左对齐（秘录标题）
- **场景标题**: 黑体 14pt，粗体
- **时间戳**: 黑体 12pt，粗体
- **角色对话**: 宋体 8.5pt，角色名粗体，无首行缩进
- **旁白**: 楷体 8.5pt，首行缩进 0.28"
- **音效**: 楷体 8.5pt，尖括号包裹

### 自定义文档格式

如需修改文档格式，可在代码中调整 `DocumentAssembler` 的参数：

```python
# 在 story_fetcher.py 或 memory_fetcher.py 中
asm = DocumentAssembler(
    spacer_lines=2,           # 章节间空行数
    page_size='A4',           # 'A4' 或 'Letter'
    margin_size='narrow',     # 'narrow'(窄), 'normal'(标准), 'wide'(宽)
    add_page_numbers=True     # 是否添加页码
)
```

**边距对比**:
- 窄边距 (默认): 比标准边距增加约 40% 的内容空间
- 标准边距: Word 默认边距
- 宽边距: 适合打印装订

## 缓存机制

### 密录缓存 (prts_cache.json)

存储内容：
- Cookie 信息
- 全量角色密录数据

清除缓存：删除 `prts_cache.json` 或使用 `--no-cache` 参数

### 故事缓存 (story_cache.json)

存储内容：
- 剧情一览页面解析结果
- 章节和故事列表

清除缓存：删除 `story_cache.json` 或使用 `--no-cache` 参数

**缓存加载提示**:
```
[2026-01-01 10:30:15] 🔍 已加载 247 条缓存记录
```

## 高级功能

### 自动关联秘录

使用 `--with-memory` 参数，`story_fetcher.py` 会：

1. 自动从故事文本中提取角色名
2. 为每个角色获取相关密录
3. 在文档末尾添加分页符和"相关角色秘录"章节
4. 按角色附加密录内容

示例：

```bash
python story_fetcher.py 反常光谱 --with-memory -v
```

输出示例：
```
[2026-01-01 10:30:16] ⚙️ 故事解析器初始化成功
[2026-01-01 10:30:17] 🔍 已加载 247 条缓存记录

解析      [反常光谱               ] [████████████████████] 100% (27/27)

  正在提取角色名称并获取秘录...
  找到 8 个角色: 凯尔希, 博士, 阿米娅, 德克萨斯, 能天使, 陈, 泰拉瑞亚, W

秘录      [获取中...]             [████████████████████] 100% (8/8)

已为 `反常光谱` 生成: 反常光谱_story.docx （包含 27 条故事，包含 8 个角色的秘录）
```

### 批量处理

创建一个文本文件（如 `chapters.txt`）：

```
反常光谱
孤岛风云
骑兵与猎人
```

然后执行：

```bash
python story_fetcher.py -f chapters.txt --with-memory
```

## 错误处理

项目已实现完善的错误处理机制：

- **网络请求失败**: 打印警告并跳过该条目，继续处理其他条目
- **页面结构变化**: 捕获异常并提示用户
- **文件权限问题**: 提供友好的错误提示（如文件被占用）
- **缓存损坏**: 自动忽略并重新获取数据
- **资源路径过滤**: 自动识别并跳过 JSON 配置数据和资源文件路径

## 常见问题

### Q: 提示"文件可能正在被其他程序打开"

A: 请关闭 Word 中打开的同名文件，或更改输出文件名。Windows 会锁定正在使用的文件。

### Q: 如何更新数据？

A: 使用 `--no-cache` 参数强制从服务器重新拉取最新数据：
```bash
python story_fetcher.py 反常光谱 --no-cache
```

### Q: 支持哪些章节名？

A: 所有 PRTS Wiki "剧情一览" 页面中列出的章节名，如：
- 反常光谱
- 孤岛风云
- 骑兵与猎人
- 将进酒
- 沃伦姆德的薄暮
- 等...

完整列表请查看: https://prts.wiki/w/剧情一览

### Q: 为什么某些角色找不到密录？

A: 可能是：
1. 角色名拼写错误（需要完全匹配）
2. 该角色尚无密录
3. PRTS Wiki 数据未更新

使用 `-v` 参数查看详细错误信息。

### Q: 文档中没有出现音效或 JSON 数据？

A: 这是正常的。工具会自动过滤：
- JSON 配置数据（如 `"eb_068cg_rain": "AVG_V068_rain_01"`）
- 资源文件路径（如 `Sound_Beta_2/AVG/d_avg_devicebeep`）
- 纯资源 ID（如 `$bgm_m_bat_awaken`）

只保留中文描述性音效（如 `<雷声>`）。

### Q: 进度条不显示或显示异常？

A: 确保：
1. 使用支持 ANSI 颜色码的终端（Windows Terminal、PowerShell 7+）
2. 使用 `-v` 参数启用详细输出
3. 终端窗口宽度足够（建议至少 100 字符宽）

### Q: 如何自定义文档格式？

A: 修改代码中 `DocumentAssembler` 的初始化参数：
```python
asm = DocumentAssembler(
    page_size='Letter',      # 改为 Letter 页面
    margin_size='wide',      # 改为宽边距
    add_page_numbers=False   # 不添加页码
)
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目仅供学习和个人使用。所有游戏数据版权归 Hypergryph（鹰角网络）所有。

## 致谢

- 数据来源：[PRTS Wiki](https://prts.wiki)
- 游戏：明日方舟 (Arknights) by Hypergryph
- 依赖库：python-docx, beautifulsoup4, requests, tqdm

---

**注意**: 本工具仅用于学习和个人使用，请勿用于商业目的。请尊重 PRTS Wiki 的使用规则，不要频繁请求造成服务器压力。
