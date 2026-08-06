from app.services.playwright import playwright_service

result = playwright_service.scrape(
    "https://docs.langchain.com/oss/python/langgraph/overview?_gl=1*1oyh3vu*_gcl_au*MjY1MDI0OTc2LjE3ODQ5NTM3ODQ.*_ga*MTE4NTY4NjI4NS4xNzg0OTUzNzg1*_ga_47WX3HKKY2*czE3ODQ5NzAwMTgkbzIkZzAkdDE3ODQ5NzAwMTgkajYwJGwwJGgw"
)

print(result["title"])
print(result["text"][:500])