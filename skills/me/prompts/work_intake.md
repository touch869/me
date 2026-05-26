# 工作日志采录引导

通过 AskUserQuestion 逐项采集工作日志。用户先给概述，agent 追问补全细节，最后确认写入。

**所有提问必须使用 AskUserQuestion 工具。**

## Step 1: 概述

```json
{
  "questions": [{
    "question": "来，聊聊 {date} 的工作，随便说，想到什么说什么。",
    "header": "概述",
    "options": [
      {"label": "今天就摸鱼了", "description": "没什么实质性工作"}
    ],
    "multiSelect": false
  }]
}
```

用户回答后，将原文保留作为基础材料，**不要精简、不要压缩、不要丢失任何细节**。后面追问得到的补充信息也一并保留。

## Step 2: 追问

根据用户的概述内容，agent 主动提出 2-4 个有针对性的追问，帮助补全细节、丰富记录。

追问原则：
- 基于概述中有价值但不够清晰的方向深入
- 关注：具体做了什么、解决了什么问题、用了什么方法/工具、遇到了什么困难、和谁协作、花了多长时间
- 不要问已有明确答案的内容
- 追问要自然、有针对性，不要模板化

每次用 AskUserQuestion 提 1-2 个问题（multiSelect 不适用时分开问），可以多轮追问直到信息足够丰富。用户说"没了"/"就这些"时停止追问。

```json
{
  "questions": [{
    "question": "{根据概述生成的针对性追问}",
    "header": "追问",
    "options": [
      {"label": "就这些了", "description": "没有更多要补充的"}
    ],
    "multiSelect": false
  }]
}
```

## Step 3: 整理 summary

将用户的原始概述 + 追问回答整理为结构化的 summary：
- **保留所有原始信息**，不要精简、不要压缩、不要丢掉任何用户提到的细节
- 只做组织整理：按时间线或逻辑顺序排列，让条理更清晰
- 用户提到的具体数字、人名、工具名、技术细节必须原样保留

## Step 4: 项目

```json
{
  "questions": [{
    "question": "哪个项目？",
    "header": "项目",
    "options": [
      {"label": "跳过", "description": "不填这个"}
    ],
    "multiSelect": false
  }]
}
```

## Step 5: 心情

```json
{
  "questions": [{
    "question": "今天工作的心情怎么样？",
    "header": "心情",
    "options": [
      {"label": "不错", "description": "开心、有成就感"},
      {"label": "一般", "description": "平平淡淡"},
      {"label": "有点累", "description": "疲惫、烦躁、压力大"},
      {"label": "跳过", "description": "不想填"}
    ],
    "multiSelect": false
  }]
}
```

## Step 6: 确认写入

汇总所有已填的列，展示给用户确认：

```json
{
  "questions": [{
    "question": "整理好了，确认写入？\n\n📋 {summary}\n🏗️ 项目：{project}\n📂 类型：{category}\n⭐ 重要度：{impact}/5\n🎯 产出：{key_result}\n💼 心情：{mood}\n🏷️ 标签：{tags}",
    "header": "确认",
    "options": [
      {"label": "确认写入", "description": "没问题"},
      {"label": "要改一下", "description": "选择后说明要改什么"}
    ],
    "multiSelect": false
  }]
}
```

## 规则

- summary 必须保留用户原始描述的所有信息，只做整理不做精简
- category、impact、key_result、tags 从对话内容自动推断，不单独问
- 用户选"跳过"的列留空
- 所有提问用 AskUserQuestion
