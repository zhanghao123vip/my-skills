# Suno：5 段 Extend 接力做多声线

多个声音不能一次生成。先生成第 1 段，挑好后在它的结尾 Extend 出第 2 段……一共约 5 段。**每段只换声线词和 Vocal Gender，伴奏风格词一字不改**，接口才听不出来。

## 分段（8 人版）

| 段 | 内容 | Vocal Gender |
| --- | --- | --- |
| 1 | 前奏 + 开场副歌 + 主唱 1 + 短副歌 | Male |
| 2 | 主唱 2（女）+ 短副歌 | **Female** |
| 3 | 主唱 3 | Male |
| 4 | 快闪 3 人 | Male |
| 5 | 快闪 2 人 + 桥段 + 最终副歌 + 片尾 | Male |

## 设置（每段一样）

Advanced 模式 · `+ Voice` 不选 · Duration Auto · Max Mode Off · Weirdness 35% · Style Influence 70% · **Variety 0** · Personalize Off · 弹出 Overwrite Styles 选 Keep Current · 5 段同一个模型。

Extend：在上一段挑中的那首上 … → Remix/Edit → Extend，**Extend from 拖到上一段最后一句刚唱完**（Lyrics 栏自动带出的旧歌词全部消失才对）。

## 伴奏风格词（共用）

```
Chinese melodic rap, emotional hip hop ballad, 88 BPM, warm piano chords, soft strings, guzheng and dizi accents, laid-back boom bap drums, deep 808 bass, soft rain ambience, live crowd ambience, anthemic group chorus, clear Mandarin diction
```

后面接这一段的声线，例：

| 人设 | 声线词 |
| --- | --- |
| 清瘦书生、自嘲 | solo male rapper for the verse, thin scholarly mid-high voice, gentle self-mocking flow, slightly tired |
| 女主唱 | solo female rapper, clear mature alto voice, restrained and calm at first then firm and strong, half-sung melodic flow |
| 中年武将、压着火 | solo male rapper, husky raspy middle-aged baritone, held-back anger building to a powerful climax, heavy weighted flow |
| 快闪三人 | three different male rappers taking turns, first a deep slow goofy bass voice, then a lazy relaxed laid-back voice, then a smooth charming playful tenor |
| 快闪收尾 + 合唱 | first a low heavy slow male voice, then a very old gentle hoarse male voice, then a soft whispered group bridge, then a huge warm group chorus with crowd singing along, short ending |

## 歌词栏标签

```
[Intro: soft piano, 1 bar]
[Chorus: group of male voices singing together, warm]
[Verse 1: Pu Songling, solo male rap]
[Verse 4: Sha Wujing, deep goofy bass voice]
[Bridge: all voices, soft, almost spoken]
[Final Chorus: everyone singing together, male and female, crowd singing along]
[Outro: crowd cheering, rain, soft piano]
[End]
```

## 拿到歌以后

- 用户把 5 段分别下载成 `refs/1.mp3 … 5.mp3`，编号不一定按顺序：转写一遍就知道哪段是哪个
- Suno 常见毛病：短副歌多唱一两遍、前奏 10 秒、结尾拖即兴。不用重做，`build_song.py` 的 cuts 把它们留在切点外
- 某段 whisper 一个字也听不出来（快闪开头常见），整段混音转写一次拿秒数，写进 `manual_starts`
- **版权**：Suno 免费版生成的歌不能商用
