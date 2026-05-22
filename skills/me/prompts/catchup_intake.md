# 补录引导

多日补录模式。**严格逐天进行，一天聊完再聊下一天。**

所有提问必须使用 AskUserQuestion 工具。用户通过选项或 Other 输入自由文本回答。

## 流程

对每一天重复以下步骤，处理完一天再进入下一天：

### Step 1: 开始当天

调用 AskUserQuestion：

```json
{
  "questions": [{
    "question": "{date}（{weekday}）那天工作上最值得记的是什么？",
    "header": "{date}",
    "options": [
      {"label": "让我说说...", "description": "选择此项后输入你的内容"},
      {"label": "没啥特别的", "description": "普通的一天"},
      {"label": "不太记得了", "description": "回忆不起来"}
    ],
    "multiSelect": false
  }]
}
```

用户选择 "让我说说..." 时会在 Other 里输入具体内容。提取用户的回答作为 summary。

### Step 2: 追问（可选）

如果 Step 1 用户选了 "没啥特别的" 或 "不太记得了"，跳过追问直接确认。

如果用户提供了具体内容，且信息不够丰富，调用 AskUserQuestion 追问 1 个方向：

```json
{
  "questions": [{
    "question": "那天最大的进展或卡点是什么？",
    "header": "追问",
    "options": [
      {"label": "让我补充...", "description": "选择后输入详情"},
      {"label": "就这些了", "description": "不用追问了"}
    ],
    "multiSelect": false
  }]
}
```

### Step 3: 确认当天

调用 AskUserQuestion 展示整理后的记录：

```json
{
  "questions": [{
    "question": "{date} 的记录：\n📋 {summary}\n🏗️ 项目：{project}  📂 类型：{category}  ⭐ 重要度：{impact}/5  🏷️ {tags}\n\n确认没问题就写入。",
    "header": "确认",
    "options": [
      {"label": "确认写入", "description": "记录没问题"},
      {"label": "要改一下", "description": "选择后说明要改什么"}
    ],
    "multiSelect": false
  }]
}
```

用户确认后，立即调用 csv_manager 写入 CSV，然后进入下一天的 Step 1。

## 规则

- 所有提问用 AskUserQuestion，不要输出纯文本问题
- 一天一天来，不要批量问多天
- category/impact/tags 自动推断，信息不足时留空
- 用户说 "都一样"/"没啥" 也要记录，不能跳过
