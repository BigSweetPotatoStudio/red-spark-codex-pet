---
name: hatch-pet
description: 从角色图、截图、生成图或视觉参考创建、修复、校验、预览并打包兼容 Codex 的动态宠物和宠物精灵图集。适用于用户想孵化 Codex 宠物、创建自定义动态宠物，或构建内置宠物资源的场景；输出为 8x9 图集、未使用格透明、逐行动画提示词、QA 联系表、预览视频和 pet.json 包。本 skill 会组合已安装的 $imagegen 系统 skill 进行视觉生成，并使用内置脚本完成确定性的精灵图集组装。
---

# Hatch Pet（孵化宠物）

## 概览

从概念、一张或多张参考图，或两者结合，创建兼容 Codex 的动态宠物。本 skill 负责宠物专用提示词规划、动画行、帧提取、图集几何、QA、预览和打包。视觉生成委托给 `$imagegen`。

面向用户的输入都是可选的。如果用户没有给出宠物名称，就从概念或参考文件名推断；如果无法推断，选择一个简短合适的名称。如果用户没有给出描述，就从概念或参考图推断。如果用户没有提供参考图，先从文字生成基础宠物，再把这张基础图作为每个动画行的规范参考。

## 生成委托

所有常规视觉生成都使用 `$imagegen`。

在生成基础图、行动作条或修复行之前，先加载并遵循已安装的图像生成 skill：

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

常规路径不要直接调用 Image API。让 `$imagegen` 自行选择内置优先路径和 CLI fallback 规则。如果 `$imagegen` 表示某个 fallback 需要确认，继续前先询问用户。

从本 skill 调用 `$imagegen` 时，把生成出的宠物提示词作为权威视觉规格。不要把它包装进通用的 `$imagegen` 共享提示词 schema，也不要额外添加精修、hero art、照片、产品图或插画风格增强。宠物提示词应保持简洁、面向 sprite、面向 digital pet；只添加输入图片的角色标签和必要的用户约束。

本 skill 的脚本只用于确定性工作：准备提示词和清单、导入选中的 `$imagegen` 输出、提取帧、校验行、合成最终图集、创建 QA 媒体和打包。

硬性边界：不要用本地 Python/Pillow 脚本、SVG、canvas、HTML/CSS 或其他代码原生绘图方式创建、绘制、平铺、变形、镜像或合成宠物视觉，来替代 `$imagegen`。常规宠物流程最多会有 10 个视觉生成任务：1 张基础宠物图加 9 个行动作条。唯一例外是 `running-left`：只有在已生成 `running-right`、完成视觉检查，并明确确认适合镜像后，才可以由 `running-right` 镜像派生。如果镜像不合适，就把 `running-left` 当作普通的、带参考图的 `$imagegen` 行来生成。如果这些调用成本过高、被阻塞或不可用，停止并解释阻塞原因，不要在本地伪造行动作条。

不要通过编辑 `imagegen-jobs.json`、向 `decoded/` 复制文件，或写辅助脚本填充行输出，来标记视觉任务完成。对选中的内置 `$imagegen` 输出使用 `record_imagegen_result.py`；只有在文档规定的次级 fallback 中才使用 `generate_pet_images.py`。确定性脚本只能处理已经生成好的视觉输出。

只有基础任务可以仅使用提示词。所有通过 `$imagegen` 生成的行动作条任务，都必须使用 `imagegen-jobs.json` 中列出的输入图片，包括记录基础任务后创建的规范基础参考图。任何没有附带 grounding 图片的行生成都视为无效。

## Codex 数字宠物风格

默认宠物美术应匹配 Codex 应用内置数字宠物：小型、接近像素画的吉祥物，紧凑 Q 版比例，轮廓厚实易读，1-2 px 深色描边，明显的阶梯状/像素边缘，有限调色板，平面赛璐璐阴影，简单有表情的脸和小巧四肢。即使参考图更精细、复杂或写实，生成的宠物也应简化为这种内部风格。

不要生成精致插画、绘画式渲染、动画主视觉、3D 渲染、光滑 app 图标效果、写实毛发或材质纹理、柔和渐变、高细节抗锯齿，以及复杂的微小配件。比这个风格更复杂的参考图，应在行生成前被简化为内部风格。

## 透明背景和特效

宠物行会被处理成透明的 `192x208` 格子，因此生成的每个像素要么属于宠物 sprite，要么必须是干净可移除的 chroma-key 背景。优先使用姿势、表情和轮廓变化，而不是装饰性特效。

允许的特效必须同时满足以下条件：

- 特效与状态相关，并有助于解释动画。
- 特效在物理上连接、接触或重叠宠物轮廓，而不是漂浮在附近。
- 特效位于和宠物相同的帧槽内，不形成独立 sprite 组件。
- 特效是不透明、硬边、像素风，并使用非 chroma-key 颜色。
- 特效足够小，在 `192x208` 下仍可读且不杂乱。

允许特效示例：贴在脸上的眼泪、接触箱子或头部的小烟团，或失败/眩晕反应中和宠物重叠的小星星。

默认避免以下内容，因为它们通常会破坏透明背景清理或组件提取：

- 波浪标记、运动弧、速度线、动作拖尾、残影、模糊或涂抹痕迹
- 分离星星、散落闪光、漂浮标点、漂浮图标、下落泪滴、分离烟云或散落尘土
- 投影、接触阴影、下落阴影、椭圆地面影、地面斑块、落地痕迹、冲击爆发、发光、光环、气场或柔软透明特效
- 文字、标签、帧编号、可见网格、引导标记、对话框、思考泡泡、UI 面板、代码片段、棋盘格透明背景、白底、黑底或场景背景
- 宠物、道具、特效、高光或阴影中出现接近 chroma-key 的颜色
- 杂散像素、断开的描边碎片、斑点/噪声、身体部位裁切、姿势重叠，或任何跨入相邻帧槽的姿势

状态专用指导：

- `idle`：保持安静、低干扰。只使用细微呼吸、小眨眼、轻微头部/身体上下浮动、很小的材质摆动，或其他保留人格的安静动作。不要表现挥手、走路、跑步、跳跃、说话、工作、审阅、情绪反应、大幅手势、物品互动或新道具。
- `waving`：只通过爪/手的姿势表现挥手。不要在爪/手周围绘制波浪标记、运动弧、线条、闪光或符号。
- `jumping`：只通过身体位置表现垂直运动。不要绘制阴影、尘土、落地痕迹、冲击爆发、弹跳垫或地面提示。
- `failed`：如果符合允许特效规则，可以使用眼泪、连接的烟团或连接的星星；不要使用红色 X、漂浮符号、分离烟雾、分离星星或独立泪滴。
- `review`：通过前倾、眨眼、眼神、头部倾斜或爪/手的位置表现专注。不要添加放大镜、纸张、代码、UI、标点或符号，除非该道具已经属于基础宠物身份。
- `running-right` 和 `running-left`：只通过身体、四肢和道具动作表现方向移动。不要绘制速度线、尘云、地面阴影或运动轨迹。
- `running`：表现一个忙于执行任务的工作/进行中循环。不要表现字面意义的脚步奔跑、慢跑、冲刺、跑步机动作、抬膝大步、摆臂或方向性移动。

## 宠物命名

当用户没有提供宠物名，并且对话自然允许时，询问用户宠物名称。如果询问会拖慢直接执行请求，就从宠物概念、参考图或性格中选择一个简短合适的名称，并持续用作展示名和包目录 slug。

优秀内置风格示例：

- Codex - 原始 Codex 伙伴。
- Dewey - 适合安静工作日的整洁小鸭。
- Fireball - 为快速迭代提供热路径能量。
- Rocky - diff 变大时仍然稳定的石头。
- Seedy - 代表新想法的小绿芽。
- Stacky - 适合深度工作的平衡堆叠。
- BSOD - 小小蓝屏吉祥物。
- Null Signal - 来自虚空的安静信号。

## 可见进度计划

每次宠物流程都要保留一个可见 checklist，让用户看到进度。开始前创建 checklist，一次只保持一个步骤 active，并在每个步骤完成时更新。

创建 checklist 前，尽可能确定宠物名称。用户提供名称时使用用户名称；否则从概念或参考图推断简短合适的名称。如果名称太长、未确定或不适合友好的 checklist，就使用 `your pet`。

常规宠物流程使用以下 checklist，把 `<Pet>` 替换为宠物名称或 `你的宠物`：

1. 准备 `<Pet>`。
2. 构思 `<Pet>` 的主外观。
3. 生成 `<Pet>` 的动作姿势。
4. 孵化 `<Pet>`。

每个步骤含义：

- `准备 <Pet>。` 选择或确认宠物名称、描述、源图片和工作目录。
- `构思 <Pet> 的主外观。` 生成宠物的主参考图。新宠物必须完成这一步，即使用户没有提供图片，因为它会成为视觉事实来源。
- `生成 <Pet> 的动作姿势。` 创建姿势行，从 `idle` 和 `running-right` 开始确认宠物仍然一致。只有当 `running-right` 翻转后明显可用时，才镜像 `running-left`。
- `孵化 <Pet>。` 把通过的姿势转为最终宠物文件，审查联系表、预览和校验结果，修复坏掉的部分，把 `pet.json` 和 `spritesheet.webp` 保存到宠物目录，然后告诉用户宠物和 QA 文件保存在哪里。

只有真实文件、图片或决策已经存在时，才能把步骤标为完成。如果只是修复流程，从第一个相关步骤开始，而不是重启整个 checklist。

## 默认工作流

1. 准备宠物运行目录和 imagegen 任务清单：

```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/hatch-pet"
python "$SKILL_DIR/scripts/prepare_pet_run.py" \
  --pet-name "<Name>" \
  --description "<一句描述>" \
  --reference /absolute/path/to/reference.png \
  --output-dir /absolute/path/to/run \
  --pet-notes "<稳定的宠物描述>" \
  --style-notes "<风格说明>" \
  --force
```

上面所有参数都是可选的，但用于表达用户约束的 flag 除外。对于纯文字请求，通过 `--pet-notes` 传入概念并省略 `--reference`；`prepare_pet_run.py` 会按需推断名称、描述、chroma key 和输出目录。

2. 检查下一个可执行的 `$imagegen` 任务：

```bash
python "$SKILL_DIR/scripts/pet_job_status.py" --run-dir /absolute/path/to/run
```

3. 对每个 ready 任务，使用以下内容调用 `$imagegen`：

- `imagegen-jobs.json` 中列出的提示词文件
- 该任务列出的每张输入图，并带上角色标签
- 默认内置 `image_gen` 路径，除非 `$imagegen` 自行路由到其他路径

基础任务必须先完成。如果存在用户参考图，基础任务使用它们。如果没有参考图，基础任务可以只使用提示词。记录基础任务后，`record_imagegen_result.py` 会写入 `decoded/base.png` 和 `references/canonical-base.png`；所有行任务会使用原始参考图（如有）以及这些规范基础图。

`prepare_pet_run.py` 还会在 `references/layout-guides/` 下为 9 个动画状态分别创建行布局引导图。每个行任务都要附带对应的引导图作为仅布局参考，让模型遵循正确的帧数、间距、居中和安全留白。把这些引导图视为不可见的构造参考：生成出的动作条不能包含可见方框、边框、中心标记、标签、引导颜色或引导背景。

生成行动作条时，行提示词中的身份锁定是权威规则：不要重新设计宠物，必须保留相同的头形、脸、标记、调色板、道具、描边粗细、身体比例和轮廓。即使确定性几何 QA 通过，如果某一行看起来像相关但不同的宠物，也算失败。

先生成并记录 `running-right`，再决定如何完成 `running-left`。对照基础图和参考图检查 `running-right`。如果宠物足够对称，水平镜像仍能保留身份、道具位置、惯用手、标记、光照、无文字细节和方向语义，可以用以下命令派生 `running-left`：

```bash
python "$SKILL_DIR/scripts/derive_running_left_from_running_right.py" \
  --run-dir /absolute/path/to/run \
  --confirm-appropriate-mirror \
  --decision-note "<为什么镜像仍能保留此宠物的身份>"
```

如果存在不对称的侧面标记、可读文字、不可镜像 logo、单手道具、单侧配件、光照线索，或镜像后会错误的方向专用姿势，就不要镜像。使用 `$imagegen` 按 `running-left` 的行提示词和所有列出的 grounding 图片生成，其中包括作为步态参考的 `decoded/running-right.png`。

对内置路径，记录从 `$CODEX_HOME/generated_images/.../ig_*.png` 选中的源图。不要把运行目录、`tmp/`、手工 fixture、确定性行目录或后处理副本中的文件记录为视觉任务来源。

4. 选定某个任务的生成输出后，导入它：

```bash
python "$SKILL_DIR/scripts/record_imagegen_result.py" \
  --run-dir /absolute/path/to/run \
  --job-id <job-id> \
  --source /absolute/path/to/generated-output.png
```

这会把图片复制到确定性流水线期望的精确 decoded 路径，并在 `imagegen-jobs.json` 中记录来源元数据。

5. 所有任务完成后，最终化：

```bash
python "$SKILL_DIR/scripts/finalize_pet_run.py" \
  --run-dir /absolute/path/to/run
```

预期输出：

```text
run/
  pet_request.json
  imagegen-jobs.json
  prompts/
  decoded/
  frames/frames-manifest.json
  final/spritesheet.png
  final/spritesheet.webp
  final/validation.json
  qa/contact-sheet.png
  qa/review.json
  qa/run-summary.json
  qa/videos/*.mp4
```

默认情况下，包输出会写在运行目录之外。如果设置了 `CODEX_HOME` 就使用它，否则使用 `$HOME/.codex`。

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/
  pet.json
  spritesheet.webp
```

接受宠物前，审查 `qa/contact-sheet.png`、`qa/review.json`、`final/validation.json` 和 `qa/videos/`。

确定性校验是必要条件，但不是充分条件。在宣布宠物完成前，必须目视检查联系表中的身份一致性。如果任何一行改变了物种/身体类型、脸、标记、调色板、道具设计、道具侧向，或整体轮廓，就阻止验收。

## 子代理行生成

基础任务记录完成并且 `references/canonical-base.png` 存在后，行动作条视觉生成必须使用 subagents，除非用户明确表示本次会话不要使用 subagents。行生成前，说明正在使用 subagents 以及委托了哪些行任务。如果当前环境或工具策略阻止生成 subagents，在行动作条生成前停止，解释阻塞原因，并询问用户是否明确继续顺序执行。

父 agent 必须负责清单和包写入。

默认流程：

1. 父 agent 运行 `prepare_pet_run.py`。
2. 父 agent 生成并记录 `base`。
3. 父 agent 运行 `pet_job_status.py`。
4. 父 agent 先为 `idle` 和 `running-right` 生成 subagents，作为身份和步态检查。
5. 父 agent 记录 subagents 返回的、被选中的 `idle` 和 `running-right` 结果。
6. 父 agent 判断 `running-left` 是否适合镜像派生；如果不适合，就把它当作普通 grounding 行任务委托给 subagent。
7. 父 agent 为剩余所有非派生的行图像生成任务生成 subagents。
8. 每个 subagent 接收行提示词和 `imagegen-jobs.json` 中列出的全部输入图路径，调用 `$imagegen`，并只返回选中的 `$CODEX_HOME/generated_images/.../ig_*.png` 源路径。
9. 只有父 agent 可以运行 `record_imagegen_result.py`、`derive_running_left_from_running_right.py`、修复排队、最终化、QA 和打包。

Subagent 写入边界：不要让 subagents 编辑 `imagegen-jobs.json`、复制文件到 `decoded/`、运行 `record_imagegen_result.py`、运行 `derive_running_left_from_running_right.py`、运行 `finalize_pet_run.py` 或打包宠物。这能避免清单竞争，并让来源检查保持集中。

Subagent 交接契约：

- 除非有意批量处理相邻简单行，否则每个 subagent 只分配一个行任务。
- 包含行 ID、绝对提示词文件路径、完整提示词文本或要求读取该精确提示词文件的指令，以及每张输入图路径和它在 `imagegen-jobs.json` 中的角色标签。
- 明确提醒 subagent：提示词中的透明背景和 artifact 规则是强制的。`waving` 禁止分离特效和挥手线；方向性 running 行禁止速度线和尘土；非方向性 `running` 行禁止字面脚步奔跑；只有状态提示词允许时，才能使用连接到主体、不透明、sprite 风的眼泪/烟雾/星星。
- 告诉 subagent 返回前检查生成候选的帧数、身份一致性、干净平面 chroma-key 背景、安全间距和禁止的分离特效。
- 告诉 subagent 只返回选中的原始 `$CODEX_HOME/generated_images/.../ig_*.png` 源路径和一句 QA 说明。是否记录或修复由父 agent 决定。

给每个 subagent 使用以下模板：

```text
为这次 hatch-pet 运行生成 `<row-id>` 行。

运行目录：<绝对运行目录>
提示词文件：<绝对提示词文件>
输入图片：
- <绝对路径> — <角色>
- <绝对路径> — <角色>

严格读取并遵循行提示词，包括透明背景和 artifact 规则。只使用 `$imagegen`；不要用本地脚本绘制、平铺、编辑或合成 sprite。

返回前目视检查：
- 帧数必须完全符合要求
- 宠物身份必须和规范基础图一致
- 背景必须是干净平面的 chroma-key
- 姿势必须完整、彼此分离、没有裁切
- 不能有禁止的分离特效或跨槽 artifact

不要编辑清单，不要复制到 decoded，不要记录结果，不要镜像行，不要最终化、修复或打包。只返回：
selected_source=/absolute/path/to/$CODEX_HOME/generated_images/.../ig_*.png
qa_note=<一句 QA 说明>
```

不允许静默顺序 fallback：如果行动作条视觉生成不能使用 subagents，停止并询问用户是否明确允许不用 subagents 继续。只有用户明确说出类似 "do not use subagents" 或 "run this sequentially" 的指令，才授权普通顺序行生成路径。最终答复必须报告哪些行任务委托给了 subagents，哪些行（如有）由父 agent 镜像或修复。

## 修复流程

如果最终化因为行 QA 失败而停止，排队定向修复任务：

```bash
python "$SKILL_DIR/scripts/queue_pet_repairs.py" \
  --run-dir /absolute/path/to/run
```

然后对每个重新打开的行任务，重复 `$imagegen` 生成和 `record_imagegen_result.py` 导入循环。只重新生成最小失败范围：失败的行，而不是整张表。

对于身份修复，使用规范基础图、原始参考图、联系表和精确行失败说明作为 grounding 上下文。只修复失败行，同时保留规范宠物身份。

## 次级图像生成 fallback

`scripts/generate_pet_images.py` 是本 skill 的次级 fallback。

只有在已安装的 `$imagegen` 系统 skill 不可用，或当前环境无法调用它时，才使用该 fallback。常规宠物创建应委托给 `$imagegen` 进行视觉生成，因为 `$imagegen` 负责内置优先的图像生成策略和自身 CLI fallback 行为。

只有在说明为什么不能使用 `$imagegen` 后，才运行次级 fallback：

```bash
python "$SKILL_DIR/scripts/generate_pet_images.py" \
  --run-dir /absolute/path/to/run \
  --model gpt-image-2 \
  --states all
```

次级 fallback 需要 `OPENAI_API_KEY`。

## 规则

- 保持 `$imagegen` 为主要生成层。
- 只要所选路径支持参考图，就保持参考图对 `$imagegen` 可见/已附加。
- 给每个行动作条任务附加该行的 `references/layout-guides/<state>.png` 图片作为仅布局引导，并且不要接受复制了引导像素的输出。
- 父 agent 记录基础图后，使用 subagents 生成行动作条视觉。父 agent 可以生成基础图，但行任务属于 subagents，除非用户明确表示本次会话不要使用 subagents。
- 每个常规视觉任务都用 `$imagegen` 生成：基础图，以及所有没有明确批准为 `running-left` 镜像派生的行动作条。
- 只有基础任务可以仅使用提示词；每个行任务都必须附加其列出的 grounding 图片。
- 先委托 `running-right`，只有在视觉检查确认镜像能保留身份和语义时才镜像 `running-left`；否则把 `running-left` 当作普通 grounding `$imagegen` 行委托。
- 永远不要用本地绘制、平铺、变换或代码生成的行动作条替代缺失的 `$imagegen` 输出。
- 永远不要手动修改 `imagegen-jobs.json` 来声称视觉任务已完成。
- 不要依赖生成图获得精确图集几何；使用本 skill 的确定性脚本。
- 使用 `pet_request.json` 中保存的 chroma key；不要强制固定绿幕。
- 保持宠物轮廓、脸、材质、调色板和道具在所有行中一致。
- 在每个基础图、行动作条和修复提示词中执行上面的透明背景和特效规则。
- 即使 `qa/review.json` 和 `final/validation.json` 没有错误，也要把视觉身份漂移视为阻塞项。
- 如果联系表显示裁切的参考图、重复 tile、白色格子背景或非 sprite 碎片，视为失败。
- 如果存在禁止的分离特效、接近 chroma-key 的 artifact、阴影、发光、涂抹、尘土、落地痕迹、挥手标记、速度线或运动轨迹，视为行失败。
- `qa/review.json` 错误是阻塞项。警告需要目视检查。

## 验收标准

- 最终图集是 PNG 或 WebP，尺寸为 `1536x1872`，支持透明，并基于 `192x208` 格子。
- 已使用格子非空，未使用格子完全透明。
- 图集遵循 `references/animation-rows.md` 中的行/帧数。
- 已生成联系表和预览视频，除非明确跳过。
- `qa/review.json` 没有错误。
- 逐行审查确认动画循环足以在 Codex 应用中使用。
- 对于自定义宠物，`${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/pet.json` 和 `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/spritesheet.webp` 已一起准备好。
