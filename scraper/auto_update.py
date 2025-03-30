#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import requests
import asyncio
from datetime import datetime
import subprocess
import shutil
from pathlib import Path

# 添加scraper目录到路径，以便导入scraper模块
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# 导入爬虫模块
try:
    from metrograph import MetrographScraper
except ImportError:
    print("无法导入爬虫模块，请确保metrograph.py文件存在")
    sys.exit(1)

# 设置日志
logging.basicConfig(
    filename=str(current_dir / 'scraper_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_paths():
    """设置文件路径"""
    scraper_dir = current_dir
    project_root = scraper_dir.parent
    
    # 确保public/data目录存在
    public_data_dir = project_root / 'public' / 'data'
    public_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 定义文件路径
    scraper_json_path = scraper_dir / 'metrograph_movies.json'
    public_json_path = public_data_dir / 'films.json'
    
    return scraper_json_path, public_json_path

async def update_json_files():
    """爬取数据并更新JSON文件"""
    logging.info("开始爬取电影数据...")
    print("开始爬取电影数据...")
    
    try:
        # 创建爬虫实例并爬取电影数据
        scraper = MetrographScraper()
        movies = await scraper.scrape_movie_details()
        
        if not movies:
            logging.error("爬取数据失败，未获取到电影信息")
            print("爬取数据失败，未获取到电影信息")
            return False
        
        # 获取文件路径
        scraper_json_path, public_json_path = setup_paths()
        
        # 保存到爬虫目录
        with open(scraper_json_path, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        # 复制到public/data目录
        shutil.copy2(scraper_json_path, public_json_path)
        
        # 记录更新时间和数据量
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"数据更新成功！时间: {update_time}, 电影数量: {len(movies)}")
        print(f"数据更新成功！时间: {update_time}, 电影数量: {len(movies)}")
        
        return True
    
    except Exception as e:
        logging.error(f"更新数据时发生错误: {str(e)}")
        print(f"更新数据时发生错误: {str(e)}")
        return False

def upload_to_render(json_file="metrograph_movies.json"):
    """
    将JSON文件上传到Render.com。
    
    注意：这需要您在Render.com有一个可写入的服务。
    这里使用的是模拟方法，实际使用时需要替换为您的服务上传方法。
    """
    logger.info(f"准备上传JSON文件到服务器: {json_file}")
    
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 这里应替换为您实际的API端点和密钥
        upload_url = "YOUR_RENDER_API_ENDPOINT"
        api_key = "YOUR_API_KEY"
        
        logger.info(f"上传到: {upload_url}")
        logger.info(f"数据大小: {len(str(data))} 字符")
        
        # 模拟上传 - 实际使用时取消注释下面的代码
        """
        response = requests.post(
            upload_url,
            json=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            logger.info("JSON文件成功上传到服务器")
            return True
        else:
            logger.error(f"上传失败，状态码: {response.status_code}")
            logger.error(f"错误信息: {response.text}")
            return False
        """
        
        # 模拟成功上传 - 实际使用时删除此行
        logger.info("模拟上传成功 (请替换为实际上传代码)")
        return True
        
    except Exception as e:
        logger.error(f"上传数据时发生错误: {e}")
        return False

def copy_to_public_folder(json_file="metrograph_movies.json"):
    """将JSON文件复制到前端项目的public目录下"""
    try:
        # 源文件路径
        source_path = os.path.abspath(json_file)
        
        # 目标路径 (假设前端项目在上一级目录)
        target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "data"))
        target_path = os.path.join(target_dir, "films.json")
        
        # 确保目标目录存在
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件
        with open(source_path, 'r', encoding='utf-8') as source:
            with open(target_path, 'w', encoding='utf-8') as target:
                target.write(source.read())
                
        logger.info(f"已将JSON文件复制到前端项目目录: {target_path}")
        return True
    except Exception as e:
        logger.error(f"复制文件时发生错误: {e}")
        return False

def main():
    """主函数，协调各个步骤的执行"""
    logger.info("=== 开始自动更新流程 ===")
    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 第一步：更新JSON文件
    if not asyncio.run(update_json_files()):
        logger.error("更新JSON文件失败，终止更新流程")
        return False
    
    # 第二步：将JSON复制到前端项目的public目录
    if not copy_to_public_folder():
        logger.warning("无法复制文件到前端目录，但将继续上传")
    
    # 第三步：上传到服务器
    if not upload_to_render():
        logger.error("上传到服务器失败")
        return False
    
    logger.info("=== 自动更新流程成功完成 ===")
    return True

if __name__ == "__main__":
    print("自动更新脚本开始运行...")
    logging.info("自动更新脚本开始运行...")
    
    success = main()
    
    if success:
        print("自动更新完成！")
        logging.info("自动更新完成！")
        sys.exit(0)
    else:
        print("自动更新失败，请查看日志文件获取详细信息")
        logging.error("自动更新失败")
        sys.exit(1) 