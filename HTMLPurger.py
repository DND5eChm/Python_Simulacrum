from bs4 import BeautifulSoup

# 清除html中的所有标签并保留“有效换行”
def purge_html(content: str) -> str:
    #先用美丽肥皂，找个时间我写一套
    output = BeautifulSoup(content, 'html.parser').get_text()
    return output