# DIVASP Merger 工具

DIVASP Merger 用于批量分析《Project DIVA Mega Mix+》的 Mod，自动扫描 `mod_pv_db.txt`，生成冲突报告，并根据优先级移除冲突歌曲。

## 功能概览

- 自动检测两类冲突：
	- **ID 冲突**：同一 PV ID 被多个来源占用。
	- **歌曲冲突**：同名歌曲（基于中英名称归一化）出现在多个来源。
- 生成包含歌曲列表、冲突详情与计划摘要的 Excel 报告。
- 按mod优先级挑选保留曲目，并移除其余mod中冲突歌曲。
- 执行计划时自动备份 `mod_pv_db.txt`，并将冲突 PV 的相关行注释为 `#@DIVASPMerger ...`，可通过 `--dry-run` 预览。
- 支持配置忽略某些 Mod（不参与扫描）与豁免 Mod（不自动修改）。
- 提供 `--restore-backup` 将备份恢复回原始 pv_db。

## 环境要求

- Python 3.12+
- 依赖：`openpyxl`, `toml`（`uv sync` 或 `pip install -r requirements.txt`）

## 快速使用

1. 配好python环境
2. 运行`python cli.py --game "path/to/DivaMegaMix.exe" --export-path .\reports --dry-run`
3. 检查生成的报告，确认`ignore_mods`和`exempt_mods`都有哪些。
3. 若报告和计划符合预期，再去掉 `--dry-run` 让工具实际注释冲突歌曲。

## 配置文件

位置：默认为仓库根目录，可通过 `--config-path` 指定。

```toml
ignore_mods = ["Another Song Merge Tool"]   # 跳过这些 Mod
exempt_mods = ["Reboot Songs Core"]          # 参与冲突查询，但不会自动注释
```

- **ignore_mods** 主要用来指定一些功能性mod，例如`Another Song Merger`，本身虽有pvdb文件但是不含曲目信息。
- **exempt_mods** 主要用来指定一些cover曲包，这些冲突留给`Another Song Merger`自动合并。

需要注意的是，cover曲包需要手动确认，建议先用`--dry-run + --export-path`生成报告确认cover曲包以后再决定。

## 详细使用方法

```bash
python cli.py --game "C:/.../DivaMegaMix.exe" \
							--export-path .\reports \
							[--dry-run] [--verbose-conflict] \
							[--config-path .\config.toml] \
							[--backup-dir .\pvdb_backup] \
							[--restore-backup]
```

- `--game`：必需，指向原版游戏 `DivaMegaMix.exe`。
- `--export-path`：导出 Excel 报告的目录或文件，缺省生成 `reports/conflict_report.xlsx`。
- `--dry-run`：仅打印计划，不修改任何文件。
- `--verbose-conflict`：在控制台输出每个冲突的详情列表。
- `--config-path`：指定工具配置（忽略/豁免列表）。
- `--backup-dir`：备份 `mod_pv_db.txt` 的目录，默认 `pvdb_backup/`。
- `--restore-backup`：在执行前先从备份还原所有 `mod_pv_db.txt`，常用于回滚。指定这个参数时不会执行任何注释工作。

如需更多功能或碰到问题，欢迎提交 Issue/PR。愿你拥有一个干净无冲突的歌单！
