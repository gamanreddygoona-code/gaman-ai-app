from world_trainer import WorldTrainer
import logging

logging.basicConfig(level=logging.INFO)

def test_single():
    trainer = WorldTrainer()
    topic = "Python Programming"
    print(f"Testing search for: {topic}")
    links = trainer.get_search_links(topic)
    print(f"Found {len(links)} links")
    for l in links[:3]:
        print(f" - {l['title']}: {l['url']}")
        data = trainer.scrape_deep(l['url'])
        if data:
            print(f"   ✅ Scraped {len(data['text'])} chars")
        else:
            print(f"   ❌ Scraping failed")

if __name__ == "__main__":
    test_single()
