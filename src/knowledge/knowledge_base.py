"""
Knowledge Base Management for Rick AI Expert
Integrates scraped Anterix data into searchable knowledge base
"""

import json
import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np
from loguru import logger

@dataclass
class KnowledgeItem:
    """Represents a piece of knowledge in Rick's knowledge base"""
    id: str
    title: str
    content: str
    url: str
    category: str
    keywords: List[str]
    importance_score: float = 1.0
    last_updated: str = ""

class AnterixKnowledgeBase:
    """Manages Rick's knowledge base with vector search capabilities"""

    def __init__(self, db_path: str = "data/rick_knowledge.db",
                 vector_db_path: str = "data/chroma_db"):
        self.db_path = db_path
        self.vector_db_path = vector_db_path

        # Initialize components
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path=vector_db_path)

        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="anterix_knowledge",
            metadata={"description": "Anterix technical and business knowledge"}
        )

        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for knowledge management"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                url TEXT,
                category TEXT,
                keywords TEXT,
                importance_score REAL DEFAULT 1.0,
                last_updated TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_categories (
                category TEXT PRIMARY KEY,
                description TEXT,
                priority INTEGER DEFAULT 1
            )
        """)

        # Initialize default categories
        categories = [
            ("Technology", "Private LTE technology and technical specifications", 1),
            ("Solutions", "Anterix solutions and applications", 1),
            ("Industry", "Industry-specific use cases and verticals", 2),
            ("Business", "Business value, ROI, and case studies", 2),
            ("Regulatory", "Spectrum licensing and regulatory information", 3),
            ("Partners", "Ecosystem partners and integrations", 3),
            ("Resources", "Whitepapers, webinars, and educational content", 4)
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO knowledge_categories (category, description, priority)
            VALUES (?, ?, ?)
        """, categories)

        conn.commit()
        conn.close()

    def load_from_spider_data(self, spider_db_path: str):
        """Load knowledge from spider-scraped Anterix data"""
        logger.info(f"Loading knowledge from spider database: {spider_db_path}")

        if not os.path.exists(spider_db_path):
            logger.error(f"Spider database not found: {spider_db_path}")
            return

        conn = sqlite3.connect(spider_db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT url, title, content, meta_description, headings,
                   word_count, reading_time, created_at
            FROM pages
            WHERE content IS NOT NULL AND content != ''
            ORDER BY created_at DESC
        """)

        pages = cursor.fetchall()
        logger.info(f"Found {len(pages)} pages to process")

        knowledge_items = []

        for page in pages:
            url, title, content, meta_desc, headings_json, word_count, reading_time, created_at = page

            # Parse headings
            try:
                headings = json.loads(headings_json) if headings_json else []
            except:
                headings = []

            # Determine category based on URL patterns
            category = self._categorize_content(url, title, content)

            # Extract keywords
            keywords = self._extract_keywords(title, content, headings)

            # Calculate importance score
            importance = self._calculate_importance(url, title, content, word_count)

            # Create knowledge item
            item = KnowledgeItem(
                id=self._generate_id(url),
                title=title or "Untitled",
                content=self._clean_content(content),
                url=url,
                category=category,
                keywords=keywords,
                importance_score=importance,
                last_updated=created_at or ""
            )

            knowledge_items.append(item)

        conn.close()

        # Store knowledge items
        self._store_knowledge_items(knowledge_items)
        logger.info(f"Successfully loaded {len(knowledge_items)} knowledge items")

    def _categorize_content(self, url: str, title: str, content: str) -> str:
        """Categorize content based on URL patterns and content analysis"""
        url_lower = url.lower()
        title_lower = (title or "").lower()
        content_lower = content.lower() if content else ""

        # Technology-focused content
        if any(term in url_lower for term in ['900-mhz', 'lte', 'spectrum', 'technology', 'plte']):
            return "Technology"

        # Solutions and applications
        if any(term in url_lower for term in ['solution', 'application', 'utility', 'grid']):
            return "Solutions"

        # Industry verticals
        if any(term in url_lower for term in ['utility', 'energy', 'gas', 'electric', 'water']):
            return "Industry"

        # Business and ROI content
        if any(term in title_lower for term in ['roi', 'business', 'cost', 'benefit', 'value']):
            return "Business"

        # Regulatory content
        if any(term in content_lower for term in ['fcc', 'regulation', 'licensing', 'compliance']):
            return "Regulatory"

        # Partner ecosystem
        if any(term in url_lower for term in ['partner', 'ecosystem', 'active-ecosystem']):
            return "Partners"

        # Resources (whitepapers, webinars, etc.)
        if any(term in url_lower for term in ['whitepaper', 'webinar', 'resource', 'download']):
            return "Resources"

        return "Solutions"  # Default category

    def _extract_keywords(self, title: str, content: str, headings: List[str]) -> List[str]:
        """Extract relevant keywords from content"""
        keywords = set()

        # Key Anterix terms
        anterix_terms = [
            "private lte", "900 mhz", "critical infrastructure", "grid modernization",
            "utility communications", "spectrum", "broadband", "wireless", "plte",
            "anterix active ecosystem", "security", "resilience", "cybersecurity"
        ]

        text = f"{title} {content} {' '.join(headings)}".lower()

        for term in anterix_terms:
            if term in text:
                keywords.add(term)

        return list(keywords)

    def _calculate_importance(self, url: str, title: str, content: str, word_count: int) -> float:
        """Calculate importance score for content prioritization"""
        score = 1.0

        # Main pages get higher scores
        if url.count('/') <= 3:
            score += 0.5

        # Solution and technology pages are more important
        if any(term in url.lower() for term in ['solution', 'technology', 'plte']):
            score += 0.3

        # Longer content generally more comprehensive
        if word_count and word_count > 500:
            score += 0.2

        # About and main pages
        if any(term in url.lower() for term in ['about', 'home', 'solutions']):
            score += 0.4

        return min(score, 3.0)  # Cap at 3.0

    def _clean_content(self, content: str) -> str:
        """Clean and prepare content for knowledge base"""
        if not content:
            return ""

        # Remove excessive whitespace
        content = ' '.join(content.split())

        # Truncate if too long (for efficiency)
        if len(content) > 10000:
            content = content[:10000] + "..."

        return content

    def _generate_id(self, url: str) -> str:
        """Generate unique ID for knowledge item"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()

    def _store_knowledge_items(self, items: List[KnowledgeItem]):
        """Store knowledge items in both SQLite and vector database"""
        logger.info(f"Storing {len(items)} knowledge items")

        # Store in SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for item in items:
            cursor.execute("""
                INSERT OR REPLACE INTO knowledge_items
                (id, title, content, url, category, keywords, importance_score, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.title,
                item.content,
                item.url,
                item.category,
                json.dumps(item.keywords),
                item.importance_score,
                item.last_updated
            ))

        conn.commit()
        conn.close()

        # Store in vector database
        documents = [item.content for item in items]
        metadatas = [
            {
                "id": item.id,
                "title": item.title,
                "url": item.url,
                "category": item.category,
                "importance": item.importance_score
            }
            for item in items
        ]
        ids = [item.id for item in items]

        # Generate embeddings and store
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, query: str, category: Optional[str] = None,
               limit: int = 5) -> List[Dict]:
        """Search knowledge base for relevant information"""
        logger.info(f"Searching for: {query} (category: {category})")

        # Prepare where clause for category filtering
        where_clause = {"category": category} if category else None

        # Search vector database
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where_clause
        )

        # Format results
        search_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i] if results["distances"] else 0

                search_results.append({
                    "content": doc,
                    "title": metadata.get("title", ""),
                    "url": metadata.get("url", ""),
                    "category": metadata.get("category", ""),
                    "importance": metadata.get("importance", 1.0),
                    "relevance_score": 1 - distance,  # Convert distance to similarity
                    "metadata": metadata
                })

        # Sort by importance and relevance
        search_results.sort(
            key=lambda x: (x["importance"], x["relevance_score"]),
            reverse=True
        )

        return search_results

    def get_categories(self) -> List[Dict[str, str]]:
        """Get all available knowledge categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, description, priority
            FROM knowledge_categories
            ORDER BY priority, category
        """)

        categories = [
            {"name": row[0], "description": row[1], "priority": row[2]}
            for row in cursor.fetchall()
        ]

        conn.close()
        return categories

    def get_knowledge_stats(self) -> Dict[str, any]:
        """Get statistics about the knowledge base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM knowledge_items")
        total_items = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category, COUNT(*)
            FROM knowledge_items
            GROUP BY category
            ORDER BY COUNT(*) DESC
        """)
        category_counts = dict(cursor.fetchall())

        cursor.execute("""
            SELECT AVG(importance_score), MAX(importance_score)
            FROM knowledge_items
        """)
        avg_importance, max_importance = cursor.fetchone()

        conn.close()

        return {
            "total_items": total_items,
            "categories": category_counts,
            "avg_importance": avg_importance or 0,
            "max_importance": max_importance or 0,
            "vector_collection_count": self.collection.count()
        }