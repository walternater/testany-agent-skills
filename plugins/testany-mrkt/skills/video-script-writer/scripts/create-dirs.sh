#!/bin/bash
# 初始化 video-script-writer 工作流目录结构
# Usage: bash create-dirs.sh [project-root]

PROJECT_ROOT="${1:-.}"

echo "🎬 正在创建 video-script-writer 工作流目录..."

mkdir -p "$PROJECT_ROOT/workflow/01-research"
mkdir -p "$PROJECT_ROOT/workflow/02-hooks"
mkdir -p "$PROJECT_ROOT/workflow/03-scripts"
mkdir -p "$PROJECT_ROOT/workflow/04-voiceover"
mkdir -p "$PROJECT_ROOT/workflow/05-storyboard"
mkdir -p "$PROJECT_ROOT/workflow/06-finals"

echo "✅ 目录结构创建完成："
echo ""
find "$PROJECT_ROOT/workflow" -type d | sort | sed 's/^/  /'
echo ""
echo "可以开始工作流了。"
