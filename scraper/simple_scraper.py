"""
简化版数据更新脚本 - 复制已存在的JSON文件到public/data目录
此脚本不会重新爬取数据，而是将已存在的metrograph_movies.json复制到public/data/films.json
"""

import os
import sys
import json
import shutil
import logging
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # 输出到控制台
    ]
)

def setup_paths():
    """设置文件路径"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    # 确保public/data目录存在
    public_data_dir = project_root / 'public' / 'data'
    public_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 定义文件路径
    scraper_json_path = current_dir / 'metrograph_movies.json'
    public_json_path = public_data_dir / 'films.json'
    
    return scraper_json_path, public_json_path

def copy_json_file():
    """复制JSON文件到public/data目录"""
    logging.info("开始更新数据文件...")
    print("开始更新数据文件...")
    
    try:
        # 获取文件路径
        scraper_json_path, public_json_path = setup_paths()
        
        # 检查源文件是否存在
        if not scraper_json_path.exists():
            logging.error(f"源文件不存在: {scraper_json_path}")
            print(f"源文件不存在: {scraper_json_path}")
            return False
        
        # 复制到public/data目录
        shutil.copy2(scraper_json_path, public_json_path)
        
        # 记录更新时间
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 检查文件是否包含有效的JSON数据
        try:
            with open(public_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                movie_count = len(data)
                logging.info(f"数据更新成功！时间: {update_time}, 电影数量: {movie_count}")
                print(f"数据更新成功！时间: {update_time}, 电影数量: {movie_count}")
        except json.JSONDecodeError:
            logging.warning("JSON文件已复制，但可能不是有效的JSON格式")
            print("JSON文件已复制，但可能不是有效的JSON格式")
        
        return True
    
    except Exception as e:
        logging.error(f"更新数据时发生错误: {str(e)}")
        print(f"更新数据时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("简化版数据更新脚本开始运行...")
    logging.info("简化版数据更新脚本开始运行...")
    
    success = copy_json_file()
    
    if success:
        print("数据更新完成！")
        logging.info("数据更新完成！")
        sys.exit(0)
    else:
        print("数据更新失败")
        logging.error("数据更新失败")
        sys.exit(1) 