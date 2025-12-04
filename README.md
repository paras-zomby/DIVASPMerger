# DIVASP Merger 工具

这个脚本会扫描每一个 Mod 目录下的 `pv_db` 文本，整理其中的歌曲 PV ID 与标题，并与原版游戏的曲目清单对比，找出以下两类冲突：

- **ID 冲突**：同一个 PV ID 被多个 Mod（或与游戏本体）占用。
- **曲目冲突**：同一首歌（基于歌曲名模糊匹配）在多个来源中重复出现。

## 数据准备

1. 在 `data/data.xlsx` 中维护原版曲目的清单。
	- 第一行被视为表头，需要至少包含一个带有 `id` 字样的列（如 `pv_id`）和一个带有 `name`/`title` 的列（如 `song_name`）。
	- 可选列：`song_name_en` 或其它说明字段。
2. 将所有 Mod 放进一个总目录，例如 `D:\DIVA_MODS`，每个 Mod 内部保持自己的文件结构。
	- 只要在 Mod 任意子目录中存在 `pv_db*.txt`（或没有扩展名的 `pv_db`），工具就会尝试解析。

## 安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 运行方式

```powershell
python main.py --mods "D:\DIVA_MODS" --base-catalog data/data.xlsx --output reports/conflict_report.xlsx
```

主要参数：

- `--mods`：包含多个 Mod 的目录（必填）。
- `--base-catalog`：原版清单，默认为 `data/data.xlsx`。
- `--output`：输出报表（xlsx 文件）的路径，默认为 `reports/conflict_report.xlsx`。

## 输出说明

- 终端会打印每个 Mod 的曲目数量、冲突概览以及生成报表的位置。
- 报表包含三个工作表：
  - `songs`：所有收集到的曲目信息。
  - `id_conflicts`：PV ID 冲突详情。
  - `song_conflicts`：歌曲名称冲突详情。

将报表发给 Mod 制作者或用于自检，就能快速定位需要调整的 PV ID 或曲目。祝制作顺利！
