---
name: ancient-cypher
description: 古人群像说唱（多人接力 cypher）：一群历史人物轮流上台，把自己真实的倒霉事翻成当代人的处境唱出来（考不上、离婚被议论、中年被晾……），副歌全员合唱，做成 3–4 分钟的 AI 说唱 MV。从拉片拆参考视频、选人写词、Suno 分段 Extend 做多声线歌、Midjourney 定妆，到逐句对齐、拼歌、MiniMax H3 按 4 句一条对口型批量生成、剪辑包装、封面文案一条龙。用户说「做一期多人古人说唱」「古人群像 / 接力说唱」「仿这条古人合唱视频」「把 battle 改成多人模式」时使用。基于 ancient-rap-battle skill（必须先装）。Make a multi-singer AI rap MV where historical figures take turns telling their life stories as modern struggles, with H3 lip-sync.
---

# 古人群像说唱 · ancient-cypher

一群古人站在同一个舞台上，轮流唱自己卡住过的那一关，台下坐的是现代打工人。成片 3–4 分钟、16:9、1080P：冷开场副歌 → 三段长主歌（每段 16 句）→ 快闪轮唱（每人 2 句）→ 桥段 → 最终副歌。

和 `ancient-rap-battle` 的区别：那边是两人对唱 diss、约 90 秒；这里是多人接力、共情向，`episode.json` 支持任意人数。这里的脚本复用那个 skill 的 H3 提交器、口型检查、节拍网格和字幕样式，**必须先装 ancient-rap-battle**（或用 `ARB_SKILL_DIR` 指向它）。

## 0. 先说清楚

- **用户要有**：Suno 账号、Midjourney 账号、MiniMax API Key（开放平台余额，**不是**网页版会员积分），环境变量 `MINIMAX_API_KEY`；国内 Key 还要设 `MINIMAX_API_BASE=https://api.minimaxi.com`
- **视频模型**：默认 MiniMax H3。用 Seedance 之前先问用户
- **红线**：不用近现代政治人物、不用在世真人；脸不能像任何真实的人或演过这个角色的演员
- **人声只用 Suno 做的歌**。edge-tts 之类的 TTS 口型对不上，也不好听，只能拿来做一次性的接口测试，而且要先说明
- **花钱的步骤一律先报价、等用户点头**：H3 每次提交、重抽、image-01 出图
- 全程用中文和用户说话；API Key 只走环境变量，绝不写进文件或记忆

开工先跑 `python S/setup_check.py`（`S/` = 本 skill 的 `scripts/`）。没装 ancient-rap-battle 就加 `--install-arb`，它会把原版（MIT）克隆到本 skill 旁边；国内先设好 `HTTPS_PROXY`。

## 工作区

```
EP/
  episode.json          ← 本期全部设定（从 examples/wo-ye-ka-guo/episode.json 复制改）
  00_拉片分析.md  01_歌词.md  02_Suno填写栏.md  03_定妆提示词.md  04_分镜表.md
  refs/  1.mp3 … 5.mp3（Suno 各段）、<id>_sheet/_bust/_face.png、venue、crowd、dj、aud_1…
  定妆图/               ← 用户存 Midjourney 原图（中文名就行），Claude 改名复制到 refs/
  work/  clips/  preview/  final/   cover-3x4.jpg  cover-4x3.jpg  发布文案.md
```

## 流程

### 1. 拉片（有参考视频时）

按 `references/remake.md`：每 2 秒抽一帧拼成联系表看结构，whisper 转写歌词看节奏；写 `00_拉片分析.md`（结构时间轴、爆点、共情点、视觉）。参考片的人物、原句、梗**一律不用**，只学结构和情绪曲线。

### 2. 选人写词（Claude 写，用户确认）

按 `references/lyrics.md`：3 位长主歌（至少 1 位女性）+ 4–6 位快闪，每人对应一种当代处境；副歌原创；每句一个真实典故 + 一个能照字面演的动作；文末列史料出处。先给阵容表，再给歌词，再给预估时长（Suno 实际约 2.65 秒一句，比 95 BPM 慢）。用户改人数、改句子就改，定稿写进 `episode.json` 的 `singers`、`lyrics`。

### 3. 做歌（用户在 Suno）

按 `references/suno.md` 出 `02_Suno填写栏.md`：5 段 Extend 接力，伴奏风格词一字不改、只换声线词和 Vocal Gender。用户把每段下载成 `refs/1.mp3 … 5.mp3`（哪段是哪个文件，转写一下就知道）。

### 4. 定妆（用户在 Midjourney）

按 `references/midjourney.md` 出 `03_定妆提示词.md`：主唱三视图 + 表情四宫格 + 半身，快闪三视图（+ 半身），场景、观众、DJ、每段一个现代观众。**逐张看图**：场景必须是写实风（插画风要重出），脸不能像明星，话筒要在下巴高度、嘴露出来。快闪缺半身图时：

```
python S/make_bust.py EP sha tao liu      # image-01 照三视图各出 2 张，挑一张复制成 refs/<id>_bust.png
```

### 5. 对齐与拼歌

在 `episode.json` 的 `song.files` 写清每个文件里按顺序有哪些段落，然后：

```
python S/align.py EP          # 分离人声 + 词时间 + 每段定位，逐句打印「歌词 | 听到的」
python S/build_song.py EP     # 按 song.cuts 在小节线上拼：音乐_最终.wav + 人声 + 句时间
```

看 align 的打印：每段开头那几句「听到的」要和歌词对得上。whisper 听不到的段落（常见于快闪开头）在该段加 `manual_starts`（用整段混音转写出的秒数）。一人两句唱了四小节的（比如唱得慢的快闪），在 `song.line_overrides` 里改时间。`cuts` 起点放在第一句前一小节，Suno 多唱的副歌、即兴、长前奏都留在切点外。**把 `音乐_最终_试听.mp3` 发给用户听接口。**

### 6. 先测，再报价

正式批量前测两条（各 10 秒、约 0.8 美元，先告诉用户价格）：一条单人主歌、一条三人合唱。合唱是最大风险（串脸、分身）。都过了再出 `04_分镜表.md`：每条素材的时间、歌词、镜头、动作、参考图，加 H3 报价（每秒 768P $0.08 / 2K $0.13，留 30% 重抽余量）。

### 7. 分镜写进 episode.json → 生成

`shots.sing`：每条 4 句、10 秒（快闪 2 句、6 秒）；`actions` 用 `"句.半句"` 指定动作（`"2.1"` = 第 3 句后半句）。`shots.stills`：观众反应、DJ、片尾（无声）。

```
python S/make_shots.py EP                                   # → work/clips.json
python ARB/scripts/h3run.py EP --all --estimate             # 报价，用户点头后：
python ARB/scripts/h3run.py EP --all                        # 并行提交，每条自动口型检查
```

批量要 20–40 分钟，放后台跑，完成会自动通知。跑完逐条抽帧看（`references/h3.md` 的检查清单），列出要重抽的和价格，用户同意后改 `episode.json` → `make_shots.py EP 某ID` → `h3run.py EP 某ID`。

### 8. 剪辑与包装

`edit.cutaways` 里排观众反应镜头，盖住相邻两条素材之间的缝（`[片段, 入点, 歌曲时间, 长度]`），开头 0 秒处必须有一条（片名叠在上面）。

```
python S/assemble.py EP                    # preview/成片_拼接.mp4，打印每个「hold」（定格）
python S/package_film.py EP --test 0:30    # 先看一小段字幕和名字卡
python S/package_film.py EP --phone        # final/<标题>_成片.mp4 + 720p 手机预览版
```

hold 超过 0.3 秒会看出定格，在那里补一条 cutaway。

### 9. 封面与文案（每期都做，不用等用户要）

```
python S/make_cover.py EP --clip CHFB --t 9      # cover-3x4.jpg + cover-4x3.jpg
```

挑一帧前排笑着看镜头的。`发布文案.md`：3 个标题（推荐一个）、正文（钩子开头、✅ 每人一句真事、金句、评论区提问、收藏转发、话题、AI 声明和史实说明）、短版、置顶评论投票下期。

### 发布前提醒（每期都说）

- 平台勾选「AI 生成内容」，片头的「AI 生成 仅供娱乐」不要去掉
- Suno 免费版的歌不能商用，开收益要用付费版重新生成最终那首
- 史料出处定稿前对一遍原文
- 要不要加账号水印，问用户账号名

## 参考

- `references/remake.md`：拉片方法、结构模板、爆点与共情点清单
- `references/lyrics.md`：阵容设计、歌词结构、处境映射、查重、史料表
- `references/suno.md`：5 段 Extend 模板、设置、声线表、同音字
- `references/midjourney.md`：定妆图清单和提示词模板、挑图标准
- `references/h3.md`：分镜规则、成本公式、检查清单、踩过的坑
- `examples/wo-ye-ka-guo/`：第一期《我也卡过》的完整 `episode.json`（8 人，4 分 15 秒，H3 共约 $25.5）
