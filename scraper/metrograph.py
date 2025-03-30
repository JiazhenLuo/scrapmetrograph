import json
import re
import os
import time
import asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class MetrographScraper:
    def __init__(self, concurrency=5):
        self.base_url = "https://metrograph.com"
        self.calendar_url = "https://metrograph.com/calendar/"
        self.movies = []
        self.concurrency = concurrency  # 并发数量
        self.semaphore = None  # 初始化时创建信号量
        
    async def initialize_browser(self):
        """初始化 Playwright 浏览器"""
        self.playwright = await async_playwright().start()
        
        # 使用 Firefox 浏览器，减少被识别为爬虫的可能性
        self.browser = await self.playwright.firefox.launch(
            headless=True,
            # 添加性能相关参数
            args=['--disable-gpu', '--disable-dev-shm-usage', '--disable-setuid-sandbox', '--no-sandbox']
        )
        
        # 创建一个具有自定义特性的上下文
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},  # 减小视窗大小，减少资源消耗
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            bypass_csp=True,
            permissions=["geolocation"],
        )
        
        # 创建一个新页面
        self.page = await self.context.new_page()
        
        # 初始化信号量，控制并发
        self.semaphore = asyncio.Semaphore(self.concurrency)
        
        # 添加一个更小的随机延迟
        await self.page.route("**/*", self.add_minimal_delay)
        
    async def add_minimal_delay(self, route):
        """添加最小必要的随机延迟"""
        # 使用更小的延迟
        await asyncio.sleep(0.05 + 0.1 * (0.5 - 0.5 * (time.time() % 2)))
        await route.continue_()
    
    async def close(self):
        """关闭浏览器和 Playwright"""
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        
    async def scrape_calendar(self):
        """使用 Playwright 抓取日历页面，获取电影基本信息和链接"""
        print("正在抓取日历页面...")
        
        # 访问日历页面，减少等待条件
        await self.page.goto(self.calendar_url, wait_until="domcontentloaded")
        
        # 等待页面加载完成关键元素
        await self.page.wait_for_selector(".calendar-list-day", timeout=10000)
        
        # 获取页面内容并解析
        content = await self.page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # 查找所有日历日期区块
        calendar_days = soup.find_all('div', class_='calendar-list-day')
        
        for day in calendar_days:
            # 获取日期
            date_elem = day.find('div', class_='date')
            if not date_elem:
                continue
                
            date_text = date_elem.text.strip()
            
            # 查找当天的所有电影条目
            movie_items = day.find_all('div', class_='item')
            
            for item in movie_items:
                # 提取电影标题和链接
                title_elem = item.find('a', class_='title')
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                detail_url = title_elem.get('href')
                
                if not detail_url:
                    continue
                    
                # 确保 URL 是绝对路径
                if not detail_url.startswith('http'):
                    detail_url = urljoin(self.base_url, detail_url)
                
                # 提取放映时间
                showtimes = []
                for time_link in item.find_all('a'):
                    if 'title' not in time_link.attrs or time_link.attrs.get('class') == ['title']:
                        continue
                    
                    time_text = time_link.text.strip()
                    ticket_status = "Available"
                    
                    if time_link.get('class') and 'sold_out' in time_link.get('class'):
                        ticket_status = "Sold Out"
                        
                    showtimes.append({
                        "time": time_text,
                        "status": ticket_status
                    })
                
                # 创建电影基本信息
                movie_info = {
                    "title": title,
                    "detail_url": detail_url,
                    "date": date_text,
                    "showtimes": showtimes,
                    "vista_film_id": self.extract_film_id(detail_url)
                }
                
                self.movies.append(movie_info)
                
        print(f"找到 {len(self.movies)} 个电影放映场次")
        return True
    
    def extract_film_id(self, url):
        """从 URL 中提取电影 ID"""
        match = re.search(r'vista_film_id=(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    async def scrape_single_movie(self, movie, scraped_ids):
        """抓取单个电影详情页的方法，用于并发执行"""
        async with self.semaphore:  # 使用信号量控制并发
            film_id = movie.get("vista_film_id")
            
            # 如果已经抓取过或没有 ID，则跳过
            if not film_id or film_id in scraped_ids:
                return None
                
            print(f"正在抓取 {movie['title']} 的详情")
            
            # 创建新的页面用于此次请求
            page = await self.context.new_page()
            details = {}
            
            try:
                # 访问电影详情页，减少等待条件
                await page.goto(movie["detail_url"], wait_until="domcontentloaded", timeout=15000)
                
                # 等待页面加载完成关键元素
                await page.wait_for_selector(".movie-info", timeout=10000)
                
                # 简化滚动行为
                await page.evaluate("window.scrollBy(0, 200)")
                
                # 获取页面内容并解析
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 提取电影详情
                # 获取海报图片 URL
                poster_elem = soup.select_one('.movie-image img')
                if poster_elem and 'src' in poster_elem.attrs:
                    details["poster_url"] = poster_elem['src']
                    
                # 获取导演
                director_elem = soup.select_one('.movie-info h5:-soup-contains("Director:")')
                if director_elem:
                    director_text = director_elem.text.strip()
                    if "Director:" in director_text:
                        details["director"] = director_text.replace("Director:", "").strip()
                
                # 获取年份、时长等信息
                info_elem = soup.select_one('.movie-info h5:nth-of-type(2)')
                if info_elem:
                    info_text = info_elem.text.strip()
                    # 尝试分离年份和时长
                    info_parts = info_text.split('/')
                    if len(info_parts) >= 2:
                        details["year"] = info_parts[0].strip()
                        runtime_part = info_parts[1].strip()
                        if "min" in runtime_part:
                            details["runtime"] = runtime_part
                
                # 获取简介 - 完全重写以更好地处理HTML结构
                synopsis = ""
                
                # 方法1: 尝试从 .movie-info > p > p 结构获取简介
                synopsis_container = soup.select_one('.movie-info > p')
                if synopsis_container:
                    # 首先尝试找到嵌套的p标签
                    nested_ps = synopsis_container.find_all('p', recursive=True)
                    
                    if nested_ps and len(nested_ps) > 0:
                        # 使用第一个非空p标签的内容作为简介
                        for p in nested_ps:
                            if p.text.strip() and not p.find('a', class_='back-link'):
                                synopsis = p.text.strip()
                                break
                    
                    # 如果通过嵌套p标签没找到，尝试直接使用内容
                    if not synopsis and synopsis_container.text.strip():
                        text = synopsis_container.text.strip()
                        if "Back to films" in text:
                            text = text.replace("Back to films", "").strip()
                        synopsis = text
                
                # 方法2: 尝试从 .fl-module-content p 获取简介
                if not synopsis:
                    module_content = soup.select_one('.fl-module-content')
                    if module_content:
                        paragraphs = module_content.select('p')
                        for p in paragraphs:
                            if p.text.strip() and 'back-link' not in str(p):
                                synopsis = p.text.strip()
                                break
                
                # 方法3: 尝试广泛搜索任何可能包含简介的元素
                if not synopsis:
                    all_paras = soup.select('p')
                    for p in all_paras:
                        # 排除菜单、链接等明显不是简介的元素
                        if len(p.text.strip()) > 100 and not p.find('a', class_='back-link'):
                            synopsis = p.text.strip()
                            break
                
                if synopsis:
                    details["synopsis"] = synopsis
                
                # 保存详情页链接
                details["detail_url"] = movie["detail_url"]
                
                # 获取所有放映日期
                screening_days = []
                
                # 尝试从日期选择器中获取日期
                day_selector = soup.select('.film_day_chooser li a')
                if day_selector:
                    # 有日期选择器的情况
                    for day_elem in day_selector:
                        if 'data-day' in day_elem.attrs:
                            day_text = day_elem.text.strip()
                            day_id = day_elem['data-day']
                            
                            # 查找对应日期的放映时间
                            day_div = soup.select_one(f'#day_{day_id}')
                            if day_div:
                                showtimes = []
                                # 查找所有链接（包括已售罄的场次）
                                time_links = day_div.select('a')
                                for time_link in time_links:
                                    time_text = time_link.text.strip()
                                    ticket_status = "Available"
                                    
                                    # 检查是否已售罄
                                    if 'sold_out' in time_link.get('class', []):
                                        ticket_status = "Sold Out"
                                    
                                    # 确保时间文本不为空且不包含不相关的文本
                                    if time_text and ":" in time_text and "Buy" not in time_text:
                                        showtimes.append({
                                            "time": time_text,
                                            "status": ticket_status
                                        })
                                
                                if showtimes:  # 只添加有放映时间的日期
                                    screening_days.append({
                                        "date": day_text,
                                        "showtimes": showtimes
                                    })
                else:
                    # 处理没有日期选择器的情况（例如 Titane 案例）
                    # 尝试从 date_picker_holder 直接获取日期
                    date_holder = soup.select_one('.date_picker_holder')
                    if date_holder:
                        day_text = date_holder.text.strip()
                        if not day_text and date_holder.select_one('a'):
                            day_text = date_holder.select_one('a').text.strip()
                        
                        if day_text:
                            # 尝试找到对应的放映时间容器
                            # 查找所有 film_day 类的 div
                            day_divs = soup.select('.film_day')
                            for day_div in day_divs:
                                # 检查 day_div 是否有标识日期的元素
                                day_title = day_div.select_one('h5.sr-only')
                                current_day_text = day_title.text.strip() if day_title else ""
                                
                                # 如果找到匹配的日期或只有一个放映日 div
                                if not current_day_text or current_day_text == day_text or len(day_divs) == 1:
                                    showtimes = []
                                    
                                    # 处理所有链接，包括已售罄的
                                    time_links = day_div.select('a')
                                    for time_link in time_links:
                                        time_text = time_link.text.strip()
                                        ticket_status = "Available"
                                        
                                        # 检查是否已售罄
                                        if 'sold_out' in time_link.get('class', []):
                                            ticket_status = "Sold Out"
                                        
                                        # 确保时间文本是有效的
                                        if time_text and ":" in time_text and "Buy" not in time_text:
                                            showtimes.append({
                                                "time": time_text,
                                                "status": ticket_status
                                            })
                                    
                                    if showtimes:  # 只添加有放映时间的日期
                                        screening_days.append({
                                            "date": day_text,
                                            "showtimes": showtimes
                                        })
                    
                    # 如果仍然没有找到放映时间，尝试直接从 film_day div 中获取
                    if not screening_days:
                        day_divs = soup.select('.film_day')
                        for day_div in day_divs:
                            day_title = day_div.select_one('h5.sr-only')
                            if day_title and day_title.text.strip():
                                day_text = day_title.text.strip()
                                showtimes = []
                                
                                # 处理所有链接，包括已售罄的
                                time_links = day_div.select('a')
                                for time_link in time_links:
                                    time_text = time_link.text.strip()
                                    ticket_status = "Available"
                                    
                                    if 'sold_out' in time_link.get('class', []):
                                        ticket_status = "Sold Out"
                                    
                                    if time_text and ":" in time_text and "Buy" not in time_text:
                                        showtimes.append({
                                            "time": time_text,
                                            "status": ticket_status
                                        })
                                
                                if showtimes:
                                    screening_days.append({
                                        "date": day_text,
                                        "showtimes": showtimes
                                    })
                
                if screening_days:
                    details["all_screenings"] = screening_days
                
                # 标记为已抓取并返回结果
                scraped_ids.add(film_id)
                details["vista_film_id"] = film_id
                details["title"] = movie["title"]
                
                return details
                
            except Exception as e:
                print(f"抓取 {movie['title']} 详情失败: {e}")
                return None
            finally:
                # 关闭此次请求使用的页面
                await page.close()
        
    async def scrape_movie_details(self):
        """并发访问每部电影的详情页，获取更多信息"""
        print("正在抓取电影详情...")
        
        # 跟踪已经抓取过的电影 ID，使用集合以避免重复
        scraped_ids = set()
        
        # 准备要抓取的电影列表 (去重)
        films_to_scrape = {}
        for movie in self.movies:
            film_id = movie.get("vista_film_id")
            if film_id and film_id not in films_to_scrape:
                films_to_scrape[film_id] = movie
        
        print(f"需要抓取 {len(films_to_scrape)} 部独特电影的详情")
        
        # 创建并发任务
        tasks = [
            self.scrape_single_movie(movie, scraped_ids) 
            for movie in films_to_scrape.values()
        ]
        
        # 并发执行所有任务并收集结果
        results = await asyncio.gather(*tasks)
        
        # 处理结果
        for result in results:
            if result:
                film_id = result.get("vista_film_id")
                # 更新所有该电影的条目
                for m in self.movies:
                    if m.get("vista_film_id") == film_id:
                        # 保留原始数据如日期和放映时间
                        original_date = m.get("date")
                        original_showtimes = m.get("showtimes")
                        
                        # 更新详细信息
                        m.update(result)
                        
                        # 恢复原始日期和放映时间数据（如果 all_screenings 不存在）
                        if "all_screenings" not in result:
                            m["date"] = original_date
                            m["showtimes"] = original_showtimes
        
        print(f"成功抓取了 {len(scraped_ids)} 部电影的详情")
            
    def save_data(self, filename="metrograph_movies.json"):
        """将抓取的数据保存为 JSON 文件，按电影整合所有放映场次"""
        # 按电影 ID 整合数据
        unique_films = {}
        
        # 按电影 ID 分组
        for movie in self.movies:
            film_id = movie.get("vista_film_id")
            if not film_id:
                continue
                
            # 如果这是第一次遇到这部电影
            if film_id not in unique_films:
                # 初始化基本信息
                unique_films[film_id] = {
                    "id": film_id,
                    "title": movie.get("title", ""),
                    "director": movie.get("director", ""),
                    "year": movie.get("year", ""),
                    "runtime": movie.get("runtime", ""),
                    "synopsis": movie.get("synopsis", ""),
                    "poster_url": movie.get("poster_url", ""),
                    "detail_url": movie.get("detail_url", ""),  # 添加详情页链接
                    "screenings": []  # 使用列表存储所有放映场次
                }
                
                # 如果有 all_screenings 字段，直接使用
                if "all_screenings" in movie:
                    unique_films[film_id]["screenings"] = movie["all_screenings"]
                    continue
            
            # 更新电影信息（如果之前没有）
            if not unique_films[film_id]["synopsis"] and movie.get("synopsis"):
                unique_films[film_id]["synopsis"] = movie.get("synopsis")
            
            if not unique_films[film_id]["director"] and movie.get("director"):
                unique_films[film_id]["director"] = movie.get("director")
                
            if not unique_films[film_id]["year"] and movie.get("year"):
                unique_films[film_id]["year"] = movie.get("year")
                
            if not unique_films[film_id]["runtime"] and movie.get("runtime"):
                unique_films[film_id]["runtime"] = movie.get("runtime")
                
            if not unique_films[film_id]["poster_url"] and movie.get("poster_url"):
                unique_films[film_id]["poster_url"] = movie.get("poster_url")
                
            if not unique_films[film_id]["detail_url"] and movie.get("detail_url"):
                unique_films[film_id]["detail_url"] = movie.get("detail_url")
            
            # 添加放映时间信息（如果有的话）
            date = movie.get("date", "")
            showtimes = movie.get("showtimes", [])
            
            if date and showtimes:
                # 检查这个日期是否已经存在
                date_exists = False
                for screening in unique_films[film_id]["screenings"]:
                    if screening["date"] == date:
                        # 如果日期已存在，添加新的放映时间（避免重复）
                        for showtime in showtimes:
                            if not any(st["time"] == showtime["time"] for st in screening["showtimes"]):
                                screening["showtimes"].append(showtime)
                        date_exists = True
                        break
                
                # 如果是新的放映日期，添加到列表中
                if not date_exists:
                    unique_films[film_id]["screenings"].append({
                        "date": date,
                        "showtimes": showtimes
                    })
        
        # 对每部电影的放映信息进行排序
        for film_id, film in unique_films.items():
            # 按日期排序放映信息
            film["screenings"].sort(key=lambda x: x["date"])
            # 按时间排序每个日期的放映场次
            for screening in film["screenings"]:
                screening["showtimes"].sort(key=lambda x: x["time"])
        
        # 转换为列表并过滤掉没有足够信息的电影
        films_list = []
        for film in unique_films.values():
            # 确保至少有标题和放映场次
            if film.get("title") and film.get("screenings"):
                films_list.append(film)
        
        # 按标题排序
        films_list.sort(key=lambda x: x["title"])
        
        # 保存整合后的数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(films_list, f, indent=2, ensure_ascii=False)
        print(f"整合后的电影数据已保存到 {filename} （共 {len(films_list)} 部电影）")
        
    async def run(self):
        """运行完整的抓取过程"""
        try:
            start_time = time.time()
            await self.initialize_browser()
            await self.scrape_calendar()
            await self.scrape_movie_details()
            self.save_data()
            end_time = time.time()
            print(f"总耗时: {end_time - start_time:.2f} 秒")
            return True
        except Exception as e:
            print(f"抓取过程中出错: {e}")
            return False
        finally:
            await self.close()
            
async def main():
    # 可以调整并发数量，默认是 5
    scraper = MetrographScraper(concurrency=8)
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
