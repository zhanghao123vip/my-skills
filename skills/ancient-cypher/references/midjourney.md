# 定妆图

## 清单（8 人版约 26 张）

| 文件名（refs/） | 内容 | 比例 |
| --- | --- | --- |
| `<id>_sheet` | 三视图（正 / 侧 / 背，全身） | 16:9 |
| `<id>_face` | 表情四宫格（只给主唱） | 1:1 |
| `<id>_bust` | 半身，三分之四侧向镜头 | 16:9 |
| `venue` | 场景：正面、对称、平视，**写实** | 16:9 |
| `crowd` | 观众：古人和现代打工人混坐 | 16:9 |
| `dj` | DJ | 16:9 |
| `aud_1…` | 每段主歌一个现代观众（反应镜头） | 16:9 |

顺序：先三视图定人 → 用三视图 `--oref` 出表情和半身 → 场景 → 群众、DJ、现代观众用场景 `--sref` 统一色调（**不要 `--oref`**，会出一堆同一张脸）。快闪只出了三视图时，用 `make_bust.py` 补半身。

## 挑图标准

- 脸原创，不像任何真实人物或演过这个角色的演员
- **场景必须是写实风**：插画 / 动漫风的场景和写实人物放不到一起，重出（提示词带 `--style raw`）
- 场景要和副歌的梗呼应（第一期「这一关」→ 雨夜城关脚下）
- 话筒统一：复古银色话筒 + 黑色落地支架，**放在下巴高度，嘴露出来**
- 8 个人配色、轮廓一眼分得开
- 女主唱：漂亮、自然，不要网红脸；侧脸半身图要配表情四宫格一起当参考，不然脸太小

## 模板

**三视图**
```
cinematic photoreal character turnaround sheet, front view, side view and back view of the same {man|woman} standing full body side by side, plain grey studio background, soft even studio light. {名字}, {朝代、身份、年龄、体型}. {脸、胡须、发型、头饰}. {气质}. {服装、配件、道具}. Holding a vintage silver microphone in his right hand. Original face, not resembling any real actor. realistic skin texture, ultra detailed, 35mm film still --ar 16:9 --style raw
```

**表情四宫格**（`--oref` 三视图）
```
2x2 grid of close-up portraits of the same {man|woman}, cinematic photoreal, plain grey background: top left rapping into a vintage silver microphone, top right {本段情绪 1}, bottom left {眼眶红、忍着不哭}, bottom right {本段情绪 2}. {名字和外形简述} --ar 1:1 --style raw
```

**半身**（`--oref` 三视图）
```
cinematic photoreal waist-up portrait of the same {man|woman} as the reference, facing the camera three-quarters to the {left|right}, plain grey studio background, soft side light. {外形简述}. Singing into a vintage silver microphone on a black stand, the microphone LOW at chin height so the whole mouth stays visible. {表情}. realistic skin texture, ultra detailed, 35mm film still --ar 16:9 --style raw
```

女性角色加：`naturally beautiful face, natural untrimmed eyebrows, barely-there makeup, real skin texture ... --no heavy makeup, contact lenses, V-shaped chin, beauty filter, airbrushed skin, influencer face`

**场景**
```
cinematic photoreal wide shot, symmetrical straight-on front view, camera at eye level facing the stage head-on from behind the audience, centered one-point perspective, the front edge of the stage perfectly horizontal, level horizon, no main characters. {场景：例 a huge ancient Chinese fortress pass gate at night, a wide low wooden stage at its foot, a row of vintage silver microphones on black stands, a DJ booth, red paper lanterns, a soft white spotlight through light rain and haze, wet stone ground, packed audience holding paper lanterns and phone lights}. shallow depth of field, 35mm film grain --ar 16:9 --style raw --no dutch angle, tilted camera, aerial view, text
```

**现代观众**（`--sref` 场景）
```
cinematic photoreal medium close-up of {一个具体的人：a young Chinese woman about 24, glasses, oversized hoodie, hugging a thick exam prep book}, in the rain at night, {情绪}, looking up at a stage, warm lantern light on the face, blurred crowd and phone lights behind, shallow depth of field, 35mm film grain --ar 16:9 --style raw
```

8 人同框的合唱镜头**不在 Midjourney 出**：H3 生成时用 场景 + 前排三人半身 当参考图。
