# -*- coding: utf-8 -*-
import os
from pathlib import Path
import asyncio
import random
from playwright.async_api import Page
from playwright.async_api import Playwright
from playwright.async_api import async_playwright


desktop_path = str(Path.home() / "Desktop")
path_to_extension = os.path.join(desktop_path, "1040Scripts", "Bytenova Daily", "client", "MetaMask")
user_data_dir = "/tmp/test-user-data-dir"

async def human_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    """Случайная задержка для имитации человеческого поведения"""
    delay = random.uniform(min_seconds, max_seconds)
    await asyncio.sleep(delay)

async def phantom_scroll(page: Page, scroll_count: int = 3):
    """Фантомные прокруты страницы для имитации человеческого поведения (только для веб-страниц)"""
    # Проверяем, что это веб-страница, а не расширение
    if page.url.startswith('chrome-extension://'):
        return  # Пропускаем прокрутки для расширений
    
    for _ in range(scroll_count):
        # Случайная прокрутка вверх или вниз
        scroll_direction = random.choice([-1, 1])
        scroll_amount = random.randint(100, 500) * scroll_direction
        
        # Используем нативный метод Playwright вместо JavaScript
        await page.mouse.wheel(0, scroll_amount)
        await human_delay(0.3, 1.0)
    
    # Возвращаемся к началу страницы
    await page.keyboard.press("Home")
    await human_delay(0.5, 1.5)

async def human_click(page: Page, selector: str, wait_time: float = 1.0):
    """Человеческий клик с задержкой и случайным поведением"""
    await human_delay(0.5, 1.5)
    
    element = await page.query_selector(selector)
    if element:
        await element.click()
        await human_delay(wait_time, wait_time + 1.0)
    else:
        print(f"Элемент {selector} не найден")

async def human_fill(page: Page, selector: str, text: str, typing_speed: float = 0.05):
    """Человеческий ввод текста с случайными задержками между символами"""
    await human_delay(0.3, 0.8)
    
    element = await page.query_selector(selector)
    if element:
        # Очищаем поле
        await element.click()
        await element.fill("")
        await human_delay(0.2, 0.5)
        
        # Вводим текст посимвольно с случайными задержками
        for char in text:
            await element.type(char)
            await asyncio.sleep(random.uniform(typing_speed * 0.5, typing_speed * 1.5))
        
        await human_delay(0.5, 1.0)
    else:
        print(f"Элемент {selector} не найден")

async def get_extension_id(page: Page) -> str:
    """Получает ID расширения MetaMask"""
    await page.goto('chrome://extensions')
    
    extension_id_by_name: dict[str, str] = {}
    
    card_elements = await page.query_selector_all(selector='div#card')
    for card in card_elements:
        name_element = await card.query_selector(selector='div#name')
        name: str = await name_element.text_content()
        
        details_element = await card.query_selector(selector='cr-button#detailsButton')
        
        async with page.expect_navigation():
            await details_element.click()
        
        url: str = page.url
        extension_id: str = url.split('?id=')[-1]
        print(str(name).replace("\n", "").replace(" ", ""), str(extension_id).replace(" ", ""))
        
        extension_id_by_name[str(name).replace("\n", "").replace(" ", "")] = str(extension_id).replace(" ", "")
        
        back_button = await page.query_selector(selector='cr-icon-button#closeButton')
        async with page.expect_navigation():
            await back_button.click()
    
    return extension_id_by_name['MetaMask']

async def full_wallet_setup(page: Page, metamask_extension_id: str, seed_phrase: list):
    len_seed = len(seed_phrase)
    """Полная настройка кошелька с импортом seed phrase"""
    await page.goto(
        url=f'chrome-extension://{metamask_extension_id}/home.html#onboarding/welcome',
    )
    
    # Принимаем условия
    terms_checkbox = page.get_by_test_id('onboarding-terms-checkbox')
    await terms_checkbox.click()
    
    # Импортируем кошелек
    import_wallet_button = page.get_by_test_id('onboarding-import-wallet')
    await import_wallet_button.click()
    
    # Отказываемся от метрик
    no_thanks_button = page.get_by_test_id('metametrics-no-thanks')
    await no_thanks_button.click()
    
    if len_seed == 12:
        pass
    else:
        dropdown = page.locator('.dropdown__select').nth(1)
        await dropdown.select_option(value=f"{len_seed}")
    print(len_seed)
    
    # Вводим seed phrase
    for idx in range(len_seed):
        input_element = page.get_by_test_id(f'import-srp__srp-word-{idx}')
        await input_element.fill(value=seed_phrase[idx])
    
    # Подтверждаем импорт
    confirm_button = page.get_by_test_id('import-srp-confirm')
    await confirm_button.click()
    
    # Создаем пароль
    password = '12345678'
    for test_id in ('create-password-new', 'create-password-confirm'):
        input_element = page.get_by_test_id(test_id)
        await input_element.fill(value=password)
    
    confirm_button = page.get_by_test_id('create-password-terms')
    await confirm_button.click()
    
    import_button = page.get_by_test_id('create-password-import')
    await import_button.click()
    
    # Завершаем настройку
    done_button = page.get_by_test_id('onboarding-complete-done')
    await done_button.click()
    
    next_button = page.get_by_test_id('pin-extension-next')
    await next_button.click()
    
    done_button = page.get_by_test_id('pin-extension-done')
    await done_button.click()
    
    print("Кошелек успешно настроен")

async def wallet_login(page: Page, metamask_extension_id: str):
    """Вторичный вход в кошелек по паролю"""
    await page.goto(
        url=f'chrome-extension://{metamask_extension_id}/home.html',
    )
    
    # Ждем появления поля для ввода пароля
    await page.wait_for_selector('input[type="password"]', timeout=10000)
    
    # Вводим пароль
    password = '12345678'
    password_input = page.locator('input[type="password"]')
    await password_input.fill(value=password)
    
    # Нажимаем кнопку "Разблокировать"
    unlock_button = page.get_by_text('Разблокировать')
    await unlock_button.click()
    
    # Ждем успешной разблокировки (появления главной страницы кошелька)
    await page.wait_for_selector('[data-testid="account-menu-icon"]', timeout=10000)
    
    print("Кошелек разблокирован")

async def connect_to_bytenova(context, metamask_extension_id: str):
    """Подключение к Bytenova и создание аккаунта"""
    bytenova_page = await context.new_page()
    await bytenova_page.goto('https://bytenova.ai/')
    await human_delay(3.0, 5.0)
    
    # Делаем фантомные прокрутки по странице
    await phantom_scroll(bytenova_page, 3)
    
    try:
        connect_wallet_button = bytenova_page.get_by_text('Connect Wallet').first
        await human_delay(1.0, 2.0)
        await connect_wallet_button.click()
        await human_delay(2.0, 3.0)
        
        metamask_button = bytenova_page.get_by_text('MetaMask', exact=True).first
        await metamask_button.click()
        await human_delay(2.0, 3.0)
    except Exception as e:
        pass
    
    # Ждем окно подтверждения MetaMask
    await asyncio.sleep(3)
    metamask_page: Page | None = None
    
    for _page in context.pages:
        url: str = _page.url
        if f'{metamask_extension_id}/notification.html' in url:
            print(url)
            metamask_page = _page
            break
    
    if metamask_page is None:
        pass#raise RuntimeError('Не найдено окно подтверждения MetaMask')
    
    # Подтверждаем подключение
    try:
        btn1_selector = '[data-testid="confirmation-submit-button"]'
        btn2_selector = '[data-testid="confirm-btn"]'
        btn3_selector = '[data-testid="confirm-footer-button"]'
        found = None
        for _ in range(20):
            if await metamask_page.query_selector(btn1_selector):
                found = btn1_selector
                break
            if await metamask_page.query_selector(btn2_selector):
                found = btn2_selector
                break
            if await metamask_page.query_selector(btn3_selector):
                found = btn3_selector
                break
            await asyncio.sleep(0.5)
        btn = await metamask_page.query_selector(found)
        if btn:
            await btn.click()
            print(f"Клик по {found} выполнен")
        else:
            pass#raise RuntimeError(f"Кнопка {found} найдена, но не кликается")
    except:pass    
    
    # Дополнительные подтверждения
    try:
        await metamask_page.get_by_test_id('confirmation-submit-button').click()
        await metamask_page.get_by_test_id('confirm-footer-button').click()
    except:pass    
    # Создаем новый аккаунт
    try:
        create_btn = bytenova_page.get_by_text('Create a new account').first
        if await create_btn.is_visible():
            await human_delay(1.0, 2.0)
            await create_btn.click()
            print("Кнопка 'Create a new account' найдена и нажата")
        else:
            print("Кнопка 'Create a new account' не найдена")
    except Exception as e:
        print(f"Ошибка при поиске/клике по кнопке: {e}")
    
    await human_delay(2.0, 3.0)
    print("Подключение к Bytenova завершено")

async def complete_daily_quest(context, metamask_extension_id: str, day_num: int):
    """Выполнение ежедневного квеста"""
    bytenova_page = await context.new_page()
    await bytenova_page.goto("https://bytenova.ai/rewards/quests")
    await human_delay(3.0, 5.0)
    
    # Делаем фантомные прокрутки по странице квестов
    await phantom_scroll(bytenova_page, 4)
    
    daily_btn = bytenova_page.get_by_text('DAILY').first
    await human_delay(1.0, 2.0)
    await daily_btn.click()
    await human_delay(2.0, 3.0)
    
    btn_text = f"Day {day_num} Check-In"
    daily_btn = bytenova_page.get_by_text(btn_text).first
    await human_delay(1.0, 2.0)
    await daily_btn.click()
    await human_delay(2.0, 3.0)
    
    # Ждем окно подтверждения MetaMask
    await asyncio.sleep(3)
    mt_page: Page | None = None
    
    for _page in context.pages:
        url: str = _page.url
        print(url)
        if f'{metamask_extension_id}/notification.html' in url:
            mt_page = _page
            break
    
    
    if mt_page:
        print("MetaMask page найден")
        await mt_page.get_by_test_id("edit-gas-fee-icon").click()
        print("Смена типа газа")
        await mt_page.get_by_test_id("edit-gas-fee-item-medium").click()
        try:
            await mt_page.get_by_test_id("confirm-footer-button").click()
        except:
            try:
                await mt_page.get_by_text("Подтвердить").click()
            except:
                pass
    else:
        print("MetaMask page не найден")
    print(f"Ежедневный квест Day {day_num} выполнен")

async def run(playwright: Playwright, day_num_bytenova: int, seed_phrase: list, is_first_run: bool = True):
    """Основная функция запуска"""
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        args=[
            f"--disable-extensions-except={path_to_extension}",
            f"--load-extension={path_to_extension}",
        ]
    )
    
    page: Page = await context.new_page()
    metamask_extension_id = await get_extension_id(page)
    
    if is_first_run:
        # Полная настройка кошелька
        await full_wallet_setup(page, metamask_extension_id, seed_phrase)
    else:
        await wallet_login(page, metamask_extension_id)
    
    await connect_to_bytenova(context, metamask_extension_id)
    
    await complete_daily_quest(context, metamask_extension_id, day_num_bytenova)
    
    await context.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright, day_num_bytenova = 2, seed_phrase=["blush", "catalog", "act", "cage", "memory", "leader", "raven", "ask", "cart", "goat", "noodle", "home"], is_first_run=False)

if __name__ == '__main__':
    asyncio.run(main())
