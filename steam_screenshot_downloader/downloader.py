import aiohttp
import asyncio
import platform
import re
import os

mime_to_extention = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}

async def main():
    steam_id = input("Enter your Steam ID: ").strip()
    
    if re.fullmatch('[a-zA-Z0-9]+', steam_id) is None:
        print('Invalid Steam ID')
        return
    
    download_path = input("Enter the path to download the screenshots to: ").strip()
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)
        
    await download_screenshots(steam_id, download_path)
    
    print('Done')
        
async def download_screenshots(steam_id: str, download_path: str):
    """Downloads all screenshots from a Steam profile"""
    
    page = 1
    misses = 0
    url = f'https://steamcommunity.com/id/{steam_id}/screenshots?p={page}&browsefilter=myfiles&view=grid#scrollTop=0'
    
    while misses < 5:
        if not await get_screenshots_from_page(url, download_path):
            misses += 1
        page += 1
        url = f'https://steamcommunity.com/id/{steam_id}/screenshots?p={page}&browsefilter=myfiles&view=grid#scrollTop=0'
    

async def get_screenshots_from_page(url: str, download_path: str):
    print(f'Getting screenshots from {url}')
    
    async with aiohttp.ClientSession() as session:
        screenshots = None
        async with session.get(url) as response:
            screenshots = re.findall('steamcommunity\\.com/sharedfiles/filedetails/\\?id\\=(\d+)', await response.text())

            if len(screenshots) == 0:
                print('No screenshots found')
                return False
            
            print(f'Found {len(screenshots)} screenshots')
            
        for screenshot in screenshots:
            await download_screenshot(screenshot, download_path, session)
    return True
    
async def download_screenshot(screenshot: str, download_path: str, session: aiohttp.ClientSession):
    print(f'Downloading screenshot {screenshot}')
    
    async with session.get(f'https://steamcommunity.com/sharedfiles/filedetails/?id={screenshot}') as response:
        screenshot_url = re.findall('https\\://steamuserimages-a.akamaihd.net/ugc/[A-Z0-9/].+?\"', await response.text())[0]
        async with session.get(screenshot_url) as response:
            try:
                extention = mime_to_extention[response.headers['Content-Type']]
                filename = f'{screenshot}.{extention}'
                with open(os.path.join(download_path, filename), 'wb') as f:
                    f.write(await response.read())
                    print(f'Downloaded {filename}')
            except KeyError:
                print(f'Unknown mime type {response.headers["Content-Type"]}')
                
if __name__=="__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())