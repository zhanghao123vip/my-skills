# My Skills · 出图 / 素材类 Skill 合集

这里收录我自己整理的 AI Agent Skill（Codex / Claude Code 通用的 `SKILL.md` 格式），主要是出图和素材管理两类。每个 Skill 放在 `skills/` 下的独立文件夹里，复制过去就能用。

| Skill | 作用 | 平台 | 状态 |
|---|---|---|---|
| [qwen-image-local](skills/qwen-image-local/) | 用 stable-diffusion.cpp 在本地运行 Qwen-Image-2.1-Turbo GGUF 文生图 | Windows PowerShell | 只有 Skill 和脚本，生成效果尚未实测 |
| [historical-image-library](skills/historical-image-library/) | 按名称或编号，从本地历史图文库取回图片和对应的提示词原文 | Python 3 | 35 组资料，含提示词，**不含图片** |

## 安装

把需要的 Skill 文件夹整个复制到你的技能目录：

- Codex：`~/.codex/skills/`
- Claude Code：`~/.claude/skills/`

```bash
git clone https://github.com/zhanghao123vip/my-skills.git
cp -r my-skills/skills/qwen-image-local ~/.codex/skills/
cp -r my-skills/skills/historical-image-library ~/.codex/skills/
```

复制后重启 Agent，它就会识别到这些 Skill。

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
| �ִ��߶��Ź���װ | `archive-4936cf980522` | 2 | 1, 3 |
| �ִ�ѧԺ��Ź��� | `archive-143857c755d5` | 1 | 2 |
| ��Ա�Ƴ���˫ͼ | `archive-e5c863a02e97` | 2 | 5, 6 |
| �й����б������ | `archive-a49208e2835f` | 2 | 7, 20 |
| �й����ж�������Ʒ | `archive-ec9219790e09` | 1 | 8 |
| �������볬��ȡ��ϵ�� | `archive-d21ecdcfa7a8` | 2 | 9, 10 |
| ������Ļ����� | `archive-70b43e3f8475` | 3 | 11, 12, 51 |
| ҹ�����Ҹ��� | `archive-e97536af11dd` | 2 | 14, 39 |
| �ػ���Ը���� | `archive-61e48310f166` | 4 | 15, 23, 24, 25 |
| �����ɫ�趨��������ͼ | `archive-d924835317bd` | 17 | 16, 28, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77 |
| ���߾Ź������� | `archive-43000e0dd32f` | 2 | 17, 46 |
| ���������޵����� | `archive-f3f545250cb2` | 3 | 19, 54, 55 |
| ������˿�������� | `archive-38377fa43c5d` | 3 | 21, 22, 30 |
| ��ջ�Ӱ����ĵ�� | `archive-c3f8ef3a7322` | 1 | 29 |
| ҹ���ͷ¶Ӫ�� | `archive-9ee9e7f0b36a` | 1 | 31 |
| �۳�������ץ��ϵ�� | `archive-1b5b384484cc` | 4 | 32, 45, 52, 53 |
| ���Ĵ����� | `archive-87e504bea217` | 3 | 34, 37, 38 |
| ʢ�Ĺ�԰��͸��ȹ | `archive-004c97e6693f` | 2 | 36, 50 |
| �ִ��߶�������ʯ�Ź��� | `archive-2b0d8972e419` | 1 | 40 |
| ˽������ͼ��Χ | `archive-3934b2d54d8a` | 2 | 41, 59 |
| �����ŷ��Ӱ��Ů | `archive-e8465b610803` | 4 | 42, 44, 60, 61 |
| �����ŷ�Ϫ������ | `archive-cc3c8cfb2068` | 1 | 43 |
| ����˫��βɭϵ | `archive-793ea17ebc63` | 2 | 48, 49 |
| �¹������ɼ� | `archive-9445edddff2b` | 11 | 56, 57, 96, 97, 98, 99, 100, 101, 102, 103, 104 |
| �����ֻ��沿���� | `archive-051797cdfb44` | 1 | 62 |
| �»������ɼ� | `archive-69bbf15f65b8` | 5 | 78, 79, 80, 81, 82 |
| �ŷ��ٴ�������� | `archive-fa6122bbf170` | 1 | 83 |
| ѩ�������ɼ� | `archive-89cf06526a21` | 6 | 84, 85, 86, 87, 88, 89 |
| �ػͷ���߸��� | `archive-590ecf82cf55` | 5 | 90, 91, 92, 93, 94 |
| �̵����ȱ����� | `archive-68dab92f4585` | 1 | 95 |
| �ҷ���֬ҹ԰ | `archive-7123c6891a8e` | 1 | 105 |
| ���������кڷ���Ů | `archive-898455c4f7bf` | 8 | 106, 107, 108, 109, 110, 111, 112, 113 |
| �紵����������Ů | `archive-a0d6c188510d` | 4 | 114, 115, 116, 117 |
| �����ŷ��Ӱ��Ů���»����������֧ | `archive-61384250a3f7` | 4 | 118, 119, 120, 121 |
| ʢ��ɭ������ȹд�������ɭ���֧ | `archive-abb440be48ec` | 3 | 122, 123, 124 |

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
