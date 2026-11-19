# resume-initial-review

学生求职简历**初审**技能（Claude Code Skill）——针对技术岗（AI / 算法 / 软件开发）简历，在投递前做第一道硬性检查。

目标不是润色文笔，而是找出会直接导致简历被 HR / 面试官刷掉的**硬伤**，并给出可执行的修改建议。

## 能查什么

- **六大模块**逐项审查：个人信息 / 教育经历 / 专业技能 / 工作经历 / 项目经验 / 自我评价。
- **硬伤识别**：年龄、婚姻状况、qq 邮箱、查不到的公司、技术栈时间错位、只有英文名的技能罗列、空窗期（毕业到首项目、项目间断档、最新项目停在过去太久）。
- 输出结构化 Markdown 审查报告（通过 / 需修改 / 不通过判定 + 逐模块问题清单 + 修改优先级）。

## 目录结构

```
resume-initial-review/
├── SKILL.md              # 技能定义与评审标准
└── scripts/
    └── read_word.py      # 简历文本提取（支持 .docx / .pdf）
```

## 安装到 Claude Code

**方式一：项目级（只在这个项目里生效，推荐）** —— 克隆到项目根目录的 `.claude/skills/` 下：

```bash
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/GSCSD1/resume-initial-review.git
```

**方式二：个人级（所有项目都能用）** —— 克隆到 `~/.claude/skills/` 下：

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/GSCSD1/resume-initial-review.git
```

## 使用方式

上传或粘贴一份简历（.docx / .pdf / 纯文本），或直接说「帮我看看这份简历」「简历初审」，技能即自动触发。

提取文本优先使用自带脚本。注意脚本路径要相对于**当前工作目录**，按安装位置区分：

```bash
# 项目级安装
python .claude/skills/resume-initial-review/scripts/read_word.py /path/to/resume.docx

# 个人级安装
python ~/.claude/skills/resume-initial-review/scripts/read_word.py /path/to/resume.docx
```

`.pdf` 同理，只需把文件名后缀换掉。

## 审查立场

站在**招聘方初审官**视角：
- 硬伤（歧视信息、不可查证、时间错位）→ 标 ❌ 必须改。
- 缺失但重要的项 → 标 ⚠️ 说明原因。
- 写得好 / 符合规范 → 标 ✅ 不过度挑刺。
