import asyncio
from playwright.async_api import async_playwright
import os

# ===== 配置区 =====
TARGET_URL = "http://10.124.3.40:8080/wui/index.html#/main/cube/search?customid=550&_key=gnrc3s&menuIds=-218,-220&menuPathIds=-218,-220&_key=8b86uf"
USERNAME = "sysadmin"
PASSWORD = "Weaver@2026"
# 下载路径（可选）
DOWNLOAD_PATH = "./downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


async def login_if_needed(page):
    print("检测是否需要登录...")
    try:
        # 等待页面加载完成
        await page.wait_for_load_state("networkidle", timeout=200000)
        print("✅ 检测到登录页面，开始使用Tab键导航填写...")

        # === 关键修复：确保焦点在正确位置 ===
        # 先点击页面任意位置，确保页面获得焦点
        # await page.click('body') 
        await asyncio.sleep(5)

        # 1. 第一次 Tab → 用户名输入框
        print("📍 按Tab键定位到用户名输入框...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)
        # 填入用户名
        print(f"⌨️ 填入用户名: {USERNAME}")
        await page.keyboard.type(USERNAME)
        await asyncio.sleep(0.5)

        # 2. 第二次 Tab → 密码输入框
        print("📍 按Tab键定位到密码输入框...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)
        # 填入密码
        print("⌨️ 填入密码...")
        await page.keyboard.type(PASSWORD)
        await asyncio.sleep(0.5)

        # 3. 第三次 Tab → 验证码输入框
        print("📍 按Tab键定位到验证码输入框...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)

        # ⚠️ 验证码需人工输入 —— 暂停并提示用户
        print("\n=== 请在浏览器中手动输入验证码（见页面右上角图片）===")
        print("=== 输入完成后，请在此处按回车继续 ===")
        input()  # 等待用户按回车

        # 4. 第四次 Tab → 登录按钮
        print("📍 按Tab键定位到登录按钮...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)

        # 点击登录按钮（按Enter键）
        print("✅ 按下Enter键执行登录...")
        await page.keyboard.press("Enter")

        # 等待跳转
        await page.wait_for_load_state("networkidle", timeout=10000)
        print("✅ 登录完成，页面已跳转。")
        return True
    except Exception as e:
        print(f"❌ 登录过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main1():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            accept_downloads=True,
            ignore_https_errors=True
        )
        page = await context.new_page()
        
        try:
            await page.goto(TARGET_URL)
            await login_if_needed(page)

            print("Navigating to target page...")
            await asyncio.sleep(2)
            
            # Navigate through menus
            await page.click('text=我的门户', timeout=10000)
            await asyncio.sleep(1)
            await page.click('text=人力外委系统', timeout=10000)
            await asyncio.sleep(1)
            
            # Wait for table data
            print("⏳ Waiting for table data...")
            await page.wait_for_selector("table tr:nth-child(2)", state="visible", timeout=30000)
            print("✅ Table data loaded.")

            # Click on the specific request
            await page.click('text=WW2026040058', timeout=10000)
            
            # === 关键修复：等待详情页内容加载 ===
            # 等待标题出现
            print("⏳ Waiting for detail form content to load...")
            await page.wait_for_selector("div:has-text('外委需求订单创建')", state="visible", timeout=10000)
            print("✅ Detail form content has loaded.")
            
            # === 提取金额 ===
            # 使用正确的ID和更稳健的定位方式
            try:
                # 1. 等待页面加载状态变为 networkidle
                await page.wait_for_load_state("networkidle", timeout=20000)

                # 2. 定位到 "采购需求剩余金额（元）" 这个标签
                label_locator = page.locator("div:has-text('采购需求剩余金额（元）')")
                await label_locator.wait_for(state="visible", timeout=5000)
                
                # 3. 获取其父容器，然后找到下一个兄弟元素（通常是值）
                parent_container = label_locator.locator("..")
                value_element = parent_container.locator("following-sibling::div:not(.card-table-th-break), following-sibling::span")
                
                # 4. 等待值元素出现并获取文本
                await value_element.wait_for(state="visible", timeout=5000)
                remaining_amount_text = await value_element.text_content()
                
                # 5. 清理文本
                remaining_amount = remaining_amount_text.strip()
                
                if remaining_amount:
                    print(f"✅ 成功获取采购需求剩余金额（元）: {remaining_amount}")
                else:
                    print("⚠️ 找到了标签，但未找到对应的值。")
                    
            except Exception as e:
                print(f"❌ 依然无法获取金额: {e}")
                # 调试：打印当前页面的所有文本
                all_text = await page.content()
                print("🔍 Debugging: Page Content Snippet:")
                print(all_text[:500])  # 打印前500字符

        finally:
            print("\n🎉 Script finished!")
            print("💡 Browser will remain open. Press Ctrl+C to exit.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Closing browser...")
                await browser.close()
async def main():
    async with async_playwright() as p:
        # 启动浏览器时忽略证书错误
        browser = await p.chromium.launch(
            headless=False,  # 保持可见，方便你观察和输入验证码
            args=[
                "--start-maximized",
                "--ignore-certificate-errors",
                "--ignore-ssl-errors"
            ]
        )
        # 创建上下文时也忽略HTTPS错误
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            accept_downloads=True,
            ignore_https_errors=True
        )
        page = await context.new_page()
        try:
            await page.goto(TARGET_URL)
            await login_if_needed(page)

            # 后续导航逻辑（保持原样）
            print("开始导航到目标页面...")
            await asyncio.sleep(2)
            await page.click('text=我的门户', timeout=10000)
            await asyncio.sleep(1)
            await page.click('text=人力外委系统', timeout=10000)
            await asyncio.sleep(1)
            # await page.click('text=人力外委需求信息维护', timeout=10000)
            # await asyncio.sleep(2)

            # === 关键修复：智能等待数据加载 ===
            # 等待表格中的第一行数据（不包括表头）出现，最多等待30秒
            print("⏳ 等待表格数据加载...")
            await page.wait_for_selector("table tr:nth-child(2)", state="visible", timeout=30000)
            print("✅ 表格数据已加载。")

            await page.click('text=	WW2026040058', timeout=10000)

            print("⏳ 正在尝试通过输入框提示文字获取金额...")
            
            try:
                # 1. 等待页面加载状态变为 networkidle（网络空闲），确保详情页资源加载完毕
                await page.wait_for_load_state("networkidle", timeout=20000)

                # 2. 定位策略变更：直接定位输入框的 placeholder 属性
                # 这种方式比找标签更稳健，不受布局结构（td/div）影响
                # amount_input = page.locator("input[placeholder='采购需求剩余金额（元）']")
                # amount_input = page.locator("input[type='hidden'][id='field2471']")
                amount_input = page.locator("span[id='field2471lspan']")

                # 3. 等待输入框出现（增加等待时间至 20秒）
                # await amount_input.wait_for(state="visible", timeout=20000)
                # while not await amount_input.wait_for(state="attached", timeout=20000)
                while not (await amount_input.wait_for(state="visible", timeout=20000)):
                    continue

                # 4. 获取值
                # remaining_amount = await amount_input.input_value()
                # remaining_amount = await amount_input.get_attribute("value")
                remaining_amount = await amount_input.text_content()
                
                # 5. 打印结果
                if remaining_amount:
                    print(f"✅ 成功获取采购需求剩余金额（元）: {remaining_amount}")
                else:
                    print("⚠️ 找到输入框，但值为空")

            except Exception as e:
                print(f"❌ 依然无法获取金额: {e}")
                # 调试：打印当前 URL 确认是否在详情页
                current_url = page.url
                print(f"🔍 当前页面 URL: {current_url}")
            

        finally:
            print("\n🎉 脚本执行完成！")
            print("💡 浏览器将保持打开状态，您可以继续操作...")
            print("💡 按 Ctrl+C 可关闭浏览器并退出脚本")
            
            # 保持浏览器打开，等待用户手动关闭
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 检测到退出信号，正在关闭浏览器...")
                await browser.close()

if __name__ == "__main__":
    asyncio.run(main())