# DIVASP Merger 工具

这个脚本会扫描每一个 Mod 目录下的 `pv_db` 文本，整理其中的歌曲 PV ID 与标题，并与原版游戏的曲目清单对比，找出以下两类冲突：

- **ID 冲突**：同一个 PV ID 被多个 Mod（或与游戏本体）占用。
- **曲目冲突**：同一首歌（基于歌曲名模糊匹配）在多个来源中重复出现。

目前尚未完成，仅实现检查冲突并export冲突报告的功能。

TODO：
- 搞出来一个pack info代替pri_lookup，在pack info中存储pack信息，包括内含的歌曲(song info)，曲包优先级，曲包的pvdb位置
- 从pvdb读取歌曲信息的时候，在读取歌曲的同时也构建曲包信息。
- 不要动load_mod_config相关逻辑，这时候先读取优先级，然后在后面parse_pvdb_file的时候传入pri_lookup，一同构建曲包pack info
- 把export逻辑改了，不要用id conflict和name conflict来输出，改成pack info和conflict records