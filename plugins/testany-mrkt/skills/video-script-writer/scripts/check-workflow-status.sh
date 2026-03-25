#!/bin/bash
# 检查 video-script-writer 工作流进度
# Usage: bash check-workflow-status.sh [project-root]

PROJECT_ROOT="${1:-.}"
WORKFLOW_DIR="$PROJECT_ROOT/workflow"

echo "🎬 Video Script Writer 工作流状态"
echo "================================="
echo ""

stages=("01-research" "02-hooks" "03-scripts" "04-voiceover" "05-storyboard" "06-finals")
names=("选题调研" "Hook 创作" "完整脚本" "配音稿" "分镜设计" "审核终稿")

for i in "${!stages[@]}"; do
    stage="${stages[$i]}"
    name="${names[$i]}"
    dir="$WORKFLOW_DIR/$stage"

    if [ -d "$dir" ]; then
        count=$(find "$dir" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -gt 0 ]; then
            echo "  ✅ Stage $((i+1)): $name ($count 个文件)"
            find "$dir" -name "*.md" -type f 2>/dev/null | sort | sed 's/^/     📄 /'
        else
            echo "  ⬜ Stage $((i+1)): $name (未开始)"
        fi
    else
        echo "  ⬜ Stage $((i+1)): $name (目录不存在)"
    fi
done

echo ""
echo "================================="
