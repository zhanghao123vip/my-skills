# My Skills · 出图 / 素材 / 视频类 Skill 合集

这里收录我自己整理的 AI Agent Skill（Codex / Claude Code 通用的 `SKILL.md` 格式），主要是出图、素材管理和 AI 视频制作三类。每个 Skill 放在 `skills/` 下的独立文件夹里，复制过去就能用。

| Skill | 作用 | 平台 | 状态 |
|---|---|---|---|
| [qwen-image-local](skills/qwen-image-local/) | 用 stable-diffusion.cpp 在本地运行 Qwen-Image-2.1-Turbo GGUF 文生图 | Windows PowerShell | 只有 Skill 和脚本，生成效果尚未实测 |
| [historical-image-library](skills/historical-image-library/) | 按名称或编号，从本地历史图文库取回图片和对应的提示词原文 | Python 3 | 35 组资料，含提示词，**不含图片** |
| [ancient-cypher](skills/ancient-cypher/) | 古人群像说唱 MV：多人接力唱自己的倒霉事，Suno 做歌 + MiniMax H3 逐句对口型 + 自动剪辑包装 | Python 3 + ffmpeg | 已做成一期（《我也卡过》，8 人 4 分 15 秒），需先装 [ancient-rap-battle](https://github.com/10291124jcjc-dotcom/ancient-rap-battle) |

## 安装

把需要的 Skill 文件夹整个复制到你的技能目录：

- Codex：`~/.codex/skills/`
- Claude Code：`~/.claude/skills/`

```bash
git clone https://github.com/zhanghao123vip/my-skills.git
cp -r my-skills/skills/qwen-image-local ~/.codex/skills/
cp -r my-skills/skills/historical-image-library ~/.codex/skills/
cp -r my-skills/skills/ancient-cypher ~/.claude/skills/
```

复制后重启 Agent，它就会识别到这些 Skill。

## ancient-cypher

一群古人站在同一个舞台上，轮流把自己卡住过的那一关唱给台下的现代人听（考不上、离婚被议论、中年被晾……），副歌全员合唱。在 Claude Code 里说「做一期多人古人说唱」，它会带你走完：

1. 拉片拆参考视频（结构、爆点、共情点）
2. 选人写词（每句一个真实典故 + 一个能照字面演的动作，附史料出处）
3. Suno 分 5 段 Extend 做多声线的歌，Midjourney 定妆
4. 自动分离人声、逐句对齐、在小节线上拼歌
5. MiniMax H3 每 4 句一条、按半句精确到 0.01 秒对口型，批量生成并自动检查口型
6. 按歌曲时间轴剪辑、插观众反应镜头，加金色字幕、名字卡、片名，出封面和发布文案

**依赖**：本 Skill 复用原版 [ancient-rap-battle](https://github.com/10291124jcjc-dotcom/ancient-rap-battle)（MIT）的 H3 提交器、口型检查、节拍网格和字幕样式。复制进技能目录后运行一次环境检查，加 `--install-arb` 会把原版克隆到旁边（国内先设 `HTTPS_PROXY`）：

```bash
python ~/.claude/skills/ancient-cypher/scripts/setup_check.py --install-arb
```

它会逐项列出还缺什么：ffmpeg（7 以上最好，旧版也兼容）、`pip install demucs faster-whisper soundfile scipy numpy pillow`、MiniMax API Key（环境变量 `MINIMAX_API_KEY`；国内 Key 另设 `MINIMAX_API_BASE=https://api.minimaxi.com`）。还要有 Suno 和 Midjourney 账号。

**花费参考**：第一期 8 人、约 4 分钟，H3 768P 总计约 $25.5。每次花钱前都会先报价。

示例设定见 `skills/ancient-cypher/examples/wo-ye-ka-guo/episode.json`。仓库里不放人物定妆图和成片。

## qwen-image-local

封装了一个 PowerShell 脚本 `scripts/generate.ps1`，按发布者推荐的 8 步 Turbo 调度调用 `sd-cli`。运行前要自己准备四个组件：

- Turbo 去噪模型：[AtomicChat/Qwen-Image-2.1-Turbo-GGUF](https://huggingface.co/AtomicChat/Qwen-Image-2.1-Turbo-GGUF)
- 文本编码器：[AtomicChat/Qwen-Image-2.1-Turbo-Uncensored-GGUF](https://huggingface.co/AtomicChat/Qwen-Image-2.1-Turbo-Uncensored-GGUF)
- VAE：[Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1) 里的 `vae/qwen_image_2.1_vae_bf16.safetensors`
- 运行时：[leejet/stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) 的 `sd-cli`

先用 `-DryRun` 检查路径和参数。这一步不加载模型，也不生成图片：

```powershell
& ./skills/qwen-image-local/scripts/generate.ps1 `
  -Executable 'D:\AI\sd-cli.exe' `
  -Denoiser  'D:\AI\models\denoiser.gguf' `
  -Encoder   'D:\AI\models\encoder.gguf' `
  -Vae       'D:\AI\models\vae.safetensors' `
  -Prompt    'A quiet garden in morning light' `
  -Output    'D:\AI\outputs\test.png' `
  -DryRun
```

所有路径都必须是绝对路径，输出目录要事先建好，输出文件必须是还不存在的 `.png`。4 GB 显存的机器能否跑完整流程还没有验证，可以用 `-ExtraArgs` 传入 `sd-cli` 支持的显存卸载参数。

## historical-image-library

这个 Skill 把历史出图作品和当时用的提示词整理成 35 组资料包，按名称或图片编号取用：

```bash
python retrieve.py --name "调用晨光森灵分支"
python retrieve.py --image 122
```

脚本会返回图片和提示词原文的绝对路径，并用 SHA-256 核对文件有没有被改动。它只负责取资料，不会自动出图或上传。

**关于图片：** 公开仓库只放了提示词原文、manifest 和校验信息，**原图没有上传**。要在本地完整使用，把原图按 `manifest.json` 里的 `image_file` 放进对应资料包的 `assets/` 目录即可（这些目录已在 `.gitignore` 中，不会被误提交）。缺图时脚本会提示应该放在哪里。

<details>
<summary>资料包目录（35 组）</summary>

| 名称 | 资料包 | 图数 | 图片编号 |
|---|---|---|---|
| 现代高定九宫格穿装 | `archive-4936cf980522` | 2 | 1, 3 |
| 现代学院风九宫格 | `archive-143857c755d5` | 1 | 2 |
| 会员制超市双图 | `archive-e5c863a02e97` | 2 | 5, 6 |
| 中国超市背面回眸 | `archive-a49208e2835f` | 2 | 7, 20 |
| 中国超市蹲下挑商品 | `archive-ec9219790e09` | 1 | 8 |
| 便利店与超市取货系列 | `archive-d21ecdcfa7a8` | 2 | 9, 10 |
| 冷调自拍换场景 | `archive-70b43e3f8475` | 3 | 11, 12, 51 |
| 夜晚卧室俯拍 | `archive-e97536af11dd` | 2 | 14, 39 |
| 敦煌祈愿人物 | `archive-61e48310f166` | 4 | 15, 23, 24, 25 |
| 人物角色设定板与三视图 | `archive-d924835317bd` | 17 | 16, 28, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77 |
| 海边九宫格自拍 | `archive-43000e0dd32f` | 2 | 17, 46 |
| 东方华宴寝殿美人 | `archive-f3f545250cb2` | 3 | 19, 54, 55 |
| 极简蕾丝近景人像 | `archive-38377fa43c5d` | 3 | 21, 22, 30 |
| 晴空花影巨型牡丹 | `archive-c3f8ef3a7322` | 1 | 29 |
| 夜间街头露营椅 | `archive-9ee9e7f0b36a` | 1 | 31 |
| 粉衬衫湖边抓拍系列 | `archive-1b5b384484cc` | 4 | 32, 45, 52, 53 |
| 俯拍吹手心 | `archive-87e504bea217` | 3 | 34, 37, 38 |
| 盛夏果园清透白裙 | `archive-004c97e6693f` | 2 | 36, 50 |
| 现代高定黑银钻石九宫格 | `archive-2b0d8972e419` | 1 | 40 |
| 私密相册截图氛围 | `archive-3934b2d54d8a` | 2 | 41, 59 |
| 东方古风电影美女 | `archive-e8465b610803` | 4 | 42, 44, 60, 61 |
| 东方古风溪边正脸 | `archive-cc3c8cfb2068` | 1 | 43 |
| 绿荫双马尾森系 | `archive-793ea17ebc63` | 2 | 48, 49 |
| 月桂灵兔仙姬 | `archive-9445edddff2b` | 11 | 56, 57, 96, 97, 98, 99, 100, 101, 102, 103, 104 |
| 极近手机面部自拍 | `archive-051797cdfb44` | 1 | 62 |
| 月华白羽仙姬 | `archive-69bbf15f65b8` | 5 | 78, 79, 80, 81, 82 |
| 古风临窗火锅递碗 | `archive-fa6122bbf170` | 1 | 83 |
| 雪域银凰仙姬 | `archive-89cf06526a21` | 6 | 84, 85, 86, 87, 88, 89 |
| 敦煌飞天高复刻 | `archive-590ecf82cf55` | 5 | 90, 91, 92, 93, 94 |
| 绿调咖啡杯近景 | `archive-68dab92f4585` | 1 | 95 |
| 桃粉胭脂夜园 | `archive-7123c6891a8e` | 1 | 105 |
| 林荫氧气感黑发少女 | `archive-898455c4f7bf` | 8 | 106, 107, 108, 109, 110, 111, 112, 113 |
| 风吹雏菊氧气少女 | `archive-a0d6c188510d` | 4 | 114, 115, 116, 117 |
| 东方古风电影美女｜月华琉璃仙宴分支 | `archive-61384250a3f7` | 4 | 118, 119, 120, 121 |
| 盛夏森林逆光白裙写真｜晨光森灵分支 | `archive-abb440be48ec` | 3 | 122, 123, 124 |

</details>

## 目录结构

```text
skills/
├─ qwen-image-local/
│  ├─ SKILL.md
│  └─ scripts/generate.ps1
└─ historical-image-library/
   ├─ SKILL.md
   ├─ retrieve.py
   ├─ catalog.json
   └─ archives/archive-<id>/
      ├─ SKILL.md · manifest.json · checksums.json
      ├─ references/*.md     # 提示词原文
      └─ assets/             # 原图（本地自备，不进仓库）
```

## 许可

本仓库暂时没有附开源许可证。公开可见不等于允许任意转载或再分发。模型和运行时的许可证请到各自的来源仓库查看。例如 Qwen 去噪模型受 Qwen Research License 约束。
