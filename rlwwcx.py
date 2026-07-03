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
        await page.wait_for_load_state("networkidle", timeout=200000)
        print("✅ 检测到登录页面，开始使用Tab键导航填写...")
        await asyncio.sleep(5)

        print("📍 按Tab键定位到用户名输入框...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)
        print(f"⌨️ 填入用户名: {USERNAME}")
        await page.keyboard.type(USERNAME)
        await asyncio.sleep(0.5)

        print("📍 按Tab键定位到密码输入框...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)
        print("⌨️ 填入密码...")
        await page.keyboard.type(PASSWORD)
        await asyncio.sleep(0.5)

        print("📍 按Tab键定位到验证码输入框...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)

        print("\n=== 请在浏览器中手动输入验证码 ===")
        print("=== 输入完成后，请在此处按回车继续 ===")
        input()

        print("📍 按Tab键定位到登录按钮...")
        await page.keyboard.press("Tab")
        await asyncio.sleep(0.5)
        print("✅ 按下Enter键执行登录...")
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle", timeout=10000)
        print("✅ 登录完成，页面已跳转。")
        return True
    except Exception as e:
        print(f"❌ 登录过程异常: {e}")
        return False

async def main():
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
        
        # --- 核心逻辑开始 ---
        try:
            await page.goto(TARGET_URL)
            await login_if_needed(page)
            
            print("开始导航到目标页面...")
            await asyncio.sleep(2)
            await page.click('text=我的门户', timeout=10000)
            await asyncio.sleep(1)
            await page.click('text=人力外委系统', timeout=10000)
            await asyncio.sleep(1)

            print("⏳ 等待表格数据加载...")
            await page.wait_for_selector("table tr:nth-child(2)", state="visible", timeout=30000)
            print("✅ 表格数据已加载。")

            # --- 处理新打开的页面 ---
            print("监听页面打开并切换上下文...")
            
            # 1. 监听新页面
            async with page.expect_popup() as new_page_info:
                # 注意：这里点击的是表格里的单号
                await page.click('text=WWDD2026050087', timeout=10000)
            
            # 2. 获取新页面对象
            new_page = await new_page_info.value
            await new_page.wait_for_load_state("networkidle", timeout=20000)
            print(f"✅ 新页面已加载: {new_page.url}")

            # --- 在新页面中查找 Frame 和元素 ---
            final_amount = None
            all_frames = new_page.frames
            print(f"🔍 在新页面中发现 {len(all_frames)} 个 Frame...")

            target_frame = None
            for frame in all_frames:
                if await frame.locator("text=采购需求剩余金额").count() > 0:
                    target_frame = frame
                    print(f"✅ 锁定目标 Frame")
                    break
            
            if target_frame:
                locator = target_frame.locator("span#field24711span")
                try:
                    await locator.wait_for(state="visible", timeout=10000)
                    final_amount = await locator.inner_text()
                    print(f"🎉 成功获取金额: {final_amount}")
                except Exception as e:
                    print(f"❌ 未找到元素: {e}")
                # 獲取含稅總金額
                hszje_locator = target_frame.locator('span#field24707span')
                await hszje_locator.wait_for(state="visible", timeout=10000);
                hszje = await hszje_locator.inner_text()
                print(f"🎉 成功获取含税总金额: {hszje}")
                if (float(final_amount) > float(hszje)):
                    print("外委采购需求剩余金额大于含税总金额！检测通過！")
                else:
                    print("外委采购需求剩余金额小于含税总金额！检测不通过！")
                await get_expected_procurement_amounts(target_frame);
                await get_contract_details_and_compare(target_frame);

        # --- 修复点：except 和 finally 必须与 try 对齐 ---
        except Exception as e:
            print(f"❌ 脚本执行出错: {e}")
        finally:
            print("\n🎉 脚本执行完成！")
            print("💡 浏览器保持打开，按 Ctrl+C 退出...")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 正在关闭浏览器...")
                await browser.close()

async def get_contract_details_and_compare(frame):
    """
    获取合同信息表中每行的'本单执行金额'和'合同剩余金额'并进行比较
    """
    print("\n--- 开始检查合同明细 ---")
    
    # 1. 定位到合同信息表的 tbody (ID: oTable2)
    table_body = frame.locator("table#oTable2 tbody.detailtbody")
    
    # 2. 获取所有数据行
    rows = await table_body.locator("tr").all()
    row_count = len(rows)
    print(f"🔍 发现 {row_count} 行合同数据")

    if row_count == 0:
        print("⚠️ 未找到合同明细数据")
        return

    for i in range(row_count):
        # 定义选择器
        # 本单执行金额: field24764_{i}span
        # 合同剩余金额: field24736_{i}span
        
        exec_price_locator = frame.locator(f"span#field24764_{i}span")
        remaining_amt_locator = frame.locator(f"span#field24736_{i}span")
        
        try:
            # 等待元素可见 (即使列隐藏，span通常也存在，如果超时说明数据未加载或ID变化)
            # 注意：如果列被 display:none 隐藏，wait_for visible 可能会失败。
            # 对于隐藏列，建议直接使用 inner_text 或 text_content，不加 wait_for visible，或者等待父容器加载
            
            # 尝试获取文本，设置较短超时，因为元素可能在隐藏列中
            exec_price_text = await exec_price_locator.inner_text(timeout=5000)
            remaining_amt_text = await remaining_amt_locator.inner_text(timeout=5000)
            
            # 清理数据
            exec_price_str = exec_price_text.strip()
            remaining_amt_str = remaining_amt_text.strip()
            
            print(f"第 {i+1} 行:")
            print(f"  - 本单执行金额: {exec_price_str}")
            print(f"  - 合同剩余金额: {remaining_amt_str}")
            
            # 数据校验与比较
            if exec_price_str and remaining_amt_str:
                try:
                    exec_price_val = float(exec_price_str)
                    remaining_amt_val = float(remaining_amt_str)
                    
                    if exec_price_val > remaining_amt_val:
                        print(f"  ❌ 警告: 本单执行金额 ({exec_price_val}) > 合同剩余金额 ({remaining_amt_val})")
                    else:
                        print(f"  ✅ 正常: 本单执行金额 ({exec_price_val}) <= 合同剩余金额 ({remaining_amt_val})")
                        
                except ValueError:
                    print(f"  ⚠️ 数值转换失败，无法比较")
            else:
                print(f"  ⚠️ 数据为空，跳过比较")

        except Exception as e:
            print(f"  ❌ 第 {i+1} 行获取数据失败: {e}")

# await get_contract_details_and_compare(target_frame)
async def get_expected_procurement_amounts(page):
    """
    获取预计采购金额（含税，元）列的所有行值
    """
    
    # 1. 定位到包含数据的 tbody
    # 根据 HTML，表格 ID 为 oTable1，数据在 class="detailtbody" 中
    table_body = page.locator("table#oTable1 tbody.detailtbody")
    
    # 2. 获取所有数据行 (tr)
    rows = await table_body.locator("tr").all()
    
    print(f"发现 {len(rows)} 行数据")

    for i, row in enumerate(rows):
        # 3. 在每一行中定位特定的 span
        # ID 规律: field24721_{i}span
        locator = row.locator(f"span#field24721_{i}span")
        
        try:
            # 等待元素可见并获取文本
            await locator.wait_for(state="visible", timeout=5000)
            text = await locator.inner_text()
            
            # 清理空白字符
            clean_text = text.strip()
            if clean_text:
                print(f"第 {i+1} 行 - 预计采购金额: {clean_text}")
            else:
                print(f"第 {i+1} 行 - 金额为空")
                
        except Exception as e:
            print(f"第 {i+1} 行获取失败: {e}")

# 使用示例：
# expected_amounts = await get_expected_procurement_amounts(new_page)

if __name__ == "__main__":
    asyncio.run(main())