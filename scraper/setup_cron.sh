#!/bin/bash
# 设置每日凌晨3点执行爬虫的cron任务

# 获取脚本所在的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# 检查是否已安装依赖
echo "检查Python依赖..."
pip install -r "$SCRIPT_DIR/requirements.txt" > /dev/null

# 设置日志文件路径
LOG_FILE="$SCRIPT_DIR/cron_log.txt"

# 创建cron任务内容
# 使用simple_scraper.py作为主要更新脚本
CRON_JOB="0 3 * * * cd $SCRIPT_DIR && /usr/bin/python $SCRIPT_DIR/simple_scraper.py >> $LOG_FILE 2>&1"

# 检查是否已存在相同的cron任务
EXISTING_CRON=$(crontab -l 2>/dev/null | grep -F "$SCRIPT_DIR/simple_scraper.py")

if [ -z "$EXISTING_CRON" ]; then
    # 添加新的cron任务
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "已设置cron任务，每天凌晨3:00自动执行爬虫更新数据。"
    echo "任务详情: $CRON_JOB"
    echo "日志将保存在: $LOG_FILE"
else
    echo "cron任务已存在，无需重复添加。"
    echo "现有任务: $EXISTING_CRON"
    echo "日志将保存在: $LOG_FILE"
fi

# 创建一个立即执行的脚本
echo "#!/bin/bash" > "$SCRIPT_DIR/run_now.sh"
echo "cd $SCRIPT_DIR && python $SCRIPT_DIR/simple_scraper.py" >> "$SCRIPT_DIR/run_now.sh"
chmod +x "$SCRIPT_DIR/run_now.sh"

echo ""
echo "设置完成！"
echo "如需立即执行爬虫，请运行: $SCRIPT_DIR/run_now.sh"
echo ""

# 提示如何查看和删除cron任务
echo "===== 管理cron任务的常用命令 ====="
echo "查看所有cron任务: crontab -l"
echo "编辑cron任务: crontab -e"
echo "删除所有cron任务: crontab -r (谨慎使用)" 