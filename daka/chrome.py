import asyncio
from playwright.async_api import async_playwright
import shutil
import os

async def main():
    print("启动浏览器...")
    
    # 删除缓存文件夹
    cache_path = os.path.join(os.path.dirname(__file__), "./playwright-cache")
    try:
        print(f"删除缓存文件夹: {cache_path}")
        shutil.rmtree(cache_path)
    except FileNotFoundError:
        pass

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        print("创建新上下文...")

        # 创建新的浏览器上下文
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            viewport={"width": 1366, "height": 768},
            device_scale_factor=2,
            has_touch=False,
            is_mobile=False,
        )

        # 清空 cookies 和缓存
        await context.clear_cookies()
        await context.clear_permissions()

        # 打开一个新页面
        page = await context.new_page()
        await page.goto("https://www.91porn.com/v.php?category=rf&viewtype=basic&page=1")
        print("页面标题:", await page.title())

        # 关闭浏览器
        await browser.close()

# 运行异步主函数
asyncio.run(main())