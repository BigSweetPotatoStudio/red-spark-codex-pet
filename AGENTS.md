# 项目指导

本仓库用于打包 Red Spark 自定义 Codex 宠物。

## 重要路径

- `assets/action-sheets/`：可编辑的源动作条，每个宠物状态一个 PNG。
- `docs/hatch-pet-skill.md`：`hatch-pet` skill 页面的参考副本。
- `pets/red-spark/`：可安装的 Codex 宠物包。
- `preview/contact-sheet.png`：生成的 QA 联系表。
- `scripts/build.py`：复用本地 Codex `hatch-pet` skill 脚本，从动作条重新构建图集和包。
- `scripts/install.py`：把宠物包安装到本地 Codex home。

## 构建契约

宠物图集固定为 `1536x1872`，包含 `8` 列、`9` 行，每个格子为 `192x208`。

状态顺序和帧数：

1. `idle`：6
2. `running-right`：8
3. `running-left`：8
4. `waving`：4
5. `jumping`：5
6. `failed`：8
7. `waiting`：6
8. `running`：6
9. `review`：6

不要修改这些帧数，除非你同时更新 `scripts/build.py`，并确认 Codex 应用能够接受新的布局。

## 编辑流程

修改某个动画时，只编辑 `assets/action-sheets/` 下对应的文件。
保持品红色背景可移除，并让每个姿势都位于自身不可见的帧槽内。
编辑后运行：

```powershell
python .\scripts\build.py
```

然后检查 `preview/contact-sheet.png`、`preview/validation.json` 和 `preview/review.json`。

除非上游 `hatch-pet` 脚本不可用，否则不要在本仓库重新实现帧提取、图集合成或校验。把 `docs/hatch-pet-skill.md` 作为本地参考页，并优先调用：

- `extract_strip_frames.py`
- `inspect_frames.py`
- `compose_atlas.py`
- `validate_atlas.py`
- `make_contact_sheet.py`
- `package_custom_pet.py`

对于这个可编辑源图仓库，调用 `inspect_frames.py` 时不要传入 `--require-components`。
手动编辑后，生成的动作条可以合法地回退到按槽位切片；验收标准是最终联系表和图集校验结果。

## 视觉约束

- 保持 Red Spark 可识别：红帽、浅色头发、红色服装、背包、吉祥物挂件。
- 避免文字、UI、标签、帧编号、阴影、发光、尘土、速度线和分离的特效。
- 让道具贴近身体，以保持帧提取稳定。
- `running` 行表示工作正在进行，而不是方向性移动。
