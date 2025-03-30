#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "========================================"
echo "Metrograph 电影爬虫"
echo "========================================"

# 检查是否安装了 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未安装 Python 3。请安装 Python 3 后继续。"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip3 install -r requirements.txt

# 安装 Playwright 浏览器
echo "正在安装 Playwright 浏览器..."
python3 -m playwright install firefox

# 运行爬虫
echo "正在运行 Metrograph 爬虫..."
python3 metrograph.py

# 检查爬取是否成功
if [ ! -f "metrograph_movies.json" ]; then
    echo "错误: 爬取失败。未生成输出文件。"
    exit 1
fi

# 处理数据用于 React 应用
echo "正在处理数据用于 React 应用..."
python3 data_processor.py

echo "========================================"
echo "爬取完成!"
echo "处理后的数据现已可用于 React 应用。"
echo "======================================== 