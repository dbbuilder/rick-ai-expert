"""
Knowledge Base Builder Script
Loads scraped Anterix data into Rick's knowledge base
"""

import os
import sys
import asyncio
from loguru import logger

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from knowledge.knowledge_base import AnterixKnowledgeBase

async def build_knowledge_base():
    """Build Rick's knowledge base from scraped data"""
    logger.info("Building Rick's Anterix Knowledge Base")

    # Initialize knowledge base
    kb = AnterixKnowledgeBase()

    # Spider database paths to check
    spider_paths = [
        "/mnt/d/dev2/clients/anterix/scraper/spider_anterix.db",
        "/mnt/d/dev2/clients/anterix/scraper/spider_anterix_full.db",
        "../scraper/spider_anterix.db",
        "../scraper/spider_anterix_full.db"
    ]

    spider_db_found = False

    for path in spider_paths:
        if os.path.exists(path):
            logger.info(f"Found spider database: {path}")
            kb.load_from_spider_data(path)
            spider_db_found = True
            break

    if not spider_db_found:
        logger.warning("No spider database found. Rick will have limited knowledge.")
        logger.info("Available paths checked:")
        for path in spider_paths:
            logger.info(f"  - {path}")

    # Get knowledge base statistics
    stats = kb.get_knowledge_stats()
    logger.info(f"Knowledge Base Statistics:")
    logger.info(f"  Total items: {stats['total_items']}")
    logger.info(f"  Categories: {stats['categories']}")
    logger.info(f"  Vector collection count: {stats['vector_collection_count']}")

    # Get categories
    categories = kb.get_categories()
    logger.info(f"Available categories:")
    for cat in categories:
        logger.info(f"  - {cat['name']}: {cat['description']}")

    # Test search functionality
    logger.info("\nTesting search functionality...")
    test_queries = [
        "private lte",
        "900 MHz spectrum",
        "grid modernization",
        "utility communications"
    ]

    for query in test_queries:
        results = kb.search(query, limit=2)
        logger.info(f"Search '{query}': {len(results)} results")
        for i, result in enumerate(results[:1]):
            logger.info(f"  {i+1}. {result['title']} (relevance: {result['relevance_score']:.2f})")

    logger.success("Knowledge base build complete!")

if __name__ == "__main__":
    asyncio.run(build_knowledge_base())