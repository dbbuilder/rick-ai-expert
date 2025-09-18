"""
Simplified RAG system for Rick using basic text similarity
No heavy dependencies - just SQLite and basic text matching
"""

import os
import sqlite3
import json
import base64
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter
import math
from loguru import logger

@dataclass
class KnowledgeChunk:
    """Simple knowledge chunk"""
    id: str
    url: str
    title: str
    content: str
    category: str
    relevance_score: float = 0.0

class SimpleAnterixRAG:
    """Simplified RAG system using TF-IDF similarity"""

    def __init__(self, spider_db_path: str = None):
        self.spider_db_path = spider_db_path or self._find_spider_db()
        self.knowledge_chunks: List[KnowledgeChunk] = []
        self.word_frequencies = {}
        self.document_frequencies = {}
        self.total_docs = 0

        logger.info(f"Initializing Simple Anterix RAG...")
        self._load_knowledge()
        self._build_tf_idf_index()

    def _find_spider_db(self) -> Optional[str]:
        """Find the spider database"""
        possible_paths = [
            "/mnt/d/dev2/clients/anterix/scraper/spider_anterix_full.db",
            "/mnt/d/dev2/clients/anterix/scraper/spider_anterix.db",
            "../scraper/spider_anterix_full.db"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found spider database: {path}")
                return path

        logger.warning("No spider database found")
        return None

    def _load_knowledge(self):
        """Load knowledge from spider database"""
        if not self.spider_db_path or not os.path.exists(self.spider_db_path):
            logger.warning("No spider database - creating demo knowledge")
            self._create_demo_knowledge()
            return

        try:
            conn = sqlite3.connect(self.spider_db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT url, title, content, summary
                FROM pages
                WHERE content IS NOT NULL AND content != ''
                ORDER BY scraped_at DESC
                LIMIT 100
            """)

            pages = cursor.fetchall()
            logger.info(f"Loading {len(pages)} pages from spider database")

            for page in pages:
                url, title, content, summary = page

                # Decode base64 content if needed
                decoded_content = self._decode_content(content)

                # Clean and extract text
                clean_text = self._extract_text(decoded_content)

                if clean_text and len(clean_text) > 100:  # Only meaningful content
                    # Use summary if available, otherwise first part of content
                    description = summary if summary else clean_text[:300]

                    chunk = KnowledgeChunk(
                        id=f"page_{len(self.knowledge_chunks)}",
                        url=url,
                        title=title or "Untitled",
                        content=f"{description}\n\nFull content: {clean_text[:1500]}",  # Include summary + content
                        category=self._categorize_url(url)
                    )
                    self.knowledge_chunks.append(chunk)

            conn.close()
            logger.info(f"Created {len(self.knowledge_chunks)} knowledge chunks")

        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")
            self._create_demo_knowledge()

    def _decode_content(self, content: str) -> str:
        """Decode base64 content if needed"""
        try:
            # Try to decode as base64
            decoded_bytes = base64.b64decode(content)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except:
            return content

    def _extract_text(self, html_content: str) -> str:
        """Extract text from HTML using simple regex"""
        if not html_content:
            return ""

        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def _categorize_url(self, url: str) -> str:
        """Categorize content based on URL"""
        url_lower = url.lower()

        if any(term in url_lower for term in ['900-mhz', 'spectrum', 'plte', 'private-lte']):
            return "Technology"
        elif any(term in url_lower for term in ['solution', 'utility', 'grid']):
            return "Solutions"
        elif any(term in url_lower for term in ['business', 'roi', 'cost']):
            return "Business"
        else:
            return "General"

    def _create_demo_knowledge(self):
        """Create demo knowledge when database is not available"""
        demo_content = [
            {
                "title": "Private LTE for Critical Infrastructure",
                "content": """Anterix Private LTE solutions use licensed 900 MHz spectrum to provide utilities with dedicated broadband wireless networks. This enables secure, reliable communications for grid modernization applications including Advanced Metering Infrastructure (AMI), Distribution Automation (DA), outage management systems, field workforce communications, and video surveillance. The 900 MHz band offers superior propagation characteristics with wide area coverage and interference-free operation.""",
                "url": "https://anterix.com/private-lte-solutions",
                "category": "Technology"
            },
            {
                "title": "900 MHz Spectrum Advantages",
                "content": """The 900 MHz band is specifically allocated by the FCC for critical infrastructure communications. Anterix holds the largest licensed spectrum position in this band. Key advantages include: better propagation for wide area coverage, licensed spectrum ensuring interference-free operation, fewer cell sites required compared to higher frequencies, and regulatory support specifically for critical infrastructure applications.""",
                "url": "https://anterix.com/900-mhz-spectrum",
                "category": "Technology"
            },
            {
                "title": "Grid Modernization Applications",
                "content": """Anterix Private LTE networks enable comprehensive grid modernization including smart grid applications, real-time monitoring and control, enhanced outage management and restoration, improved field workforce productivity, advanced cybersecurity for critical operations, and support for distributed energy resources integration. These applications help utilities improve reliability, efficiency, and customer service.""",
                "url": "https://anterix.com/grid-modernization",
                "category": "Solutions"
            },
            {
                "title": "Business Value and ROI",
                "content": """Private LTE networks deliver significant business value for utilities through reduced operational expenses versus leased circuits, improved operational efficiency and productivity, enhanced grid reliability reducing outage costs, avoided costs from communication failures, new revenue opportunities from grid services, and improved customer satisfaction. Typical ROI timeframes range from 3-5 years depending on deployment scope.""",
                "url": "https://anterix.com/business-value",
                "category": "Business"
            }
        ]

        for i, item in enumerate(demo_content):
            chunk = KnowledgeChunk(
                id=f"demo_{i}",
                url=item["url"],
                title=item["title"],
                content=item["content"],
                category=item["category"]
            )
            self.knowledge_chunks.append(chunk)

        logger.info(f"Created {len(self.knowledge_chunks)} demo knowledge chunks")

    def _build_tf_idf_index(self):
        """Build TF-IDF index for similarity search"""
        logger.info("Building TF-IDF index...")

        # Tokenize all documents
        all_words = set()
        doc_word_counts = []

        for chunk in self.knowledge_chunks:
            words = self._tokenize(chunk.content + " " + chunk.title)
            word_count = Counter(words)
            doc_word_counts.append(word_count)
            all_words.update(words)

        # Calculate document frequencies
        self.document_frequencies = {}
        for word in all_words:
            df = sum(1 for doc_words in doc_word_counts if word in doc_words)
            self.document_frequencies[word] = df

        self.total_docs = len(self.knowledge_chunks)
        logger.info(f"Built TF-IDF index with {len(all_words)} unique terms")

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

        return [word for word in words if word not in stop_words and len(word) > 2]

    def _calculate_tf_idf_similarity(self, query: str, chunk: KnowledgeChunk) -> float:
        """Calculate TF-IDF similarity between query and document"""
        query_words = self._tokenize(query)
        doc_words = self._tokenize(chunk.content + " " + chunk.title)

        if not query_words or not doc_words:
            return 0.0

        # Calculate query TF-IDF vector
        query_tf = Counter(query_words)
        query_vector = {}

        for word in query_words:
            tf = query_tf[word] / len(query_words)
            idf = math.log(self.total_docs / (self.document_frequencies.get(word, 1) + 1))
            query_vector[word] = tf * idf

        # Calculate document TF-IDF vector
        doc_tf = Counter(doc_words)
        doc_vector = {}

        for word in doc_words:
            tf = doc_tf[word] / len(doc_words)
            idf = math.log(self.total_docs / (self.document_frequencies.get(word, 1) + 1))
            doc_vector[word] = tf * idf

        # Calculate cosine similarity
        dot_product = sum(query_vector.get(word, 0) * doc_vector.get(word, 0) for word in set(query_words + doc_words))

        query_norm = math.sqrt(sum(v**2 for v in query_vector.values()))
        doc_norm = math.sqrt(sum(v**2 for v in doc_vector.values()))

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot_product / (query_norm * doc_norm)

    def search(self, query: str, top_k: int = 5) -> List[KnowledgeChunk]:
        """Search for relevant knowledge chunks"""
        if not self.knowledge_chunks:
            return []

        # Calculate similarity scores
        scored_chunks = []
        for chunk in self.knowledge_chunks:
            similarity = self._calculate_tf_idf_similarity(query, chunk)
            chunk.relevance_score = similarity
            scored_chunks.append(chunk)

        # Sort by relevance and return top k
        scored_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_chunks[:top_k]

    def get_context_for_query(self, query: str, max_tokens: int = 1500) -> str:
        """Get relevant context for a query"""
        relevant_chunks = self.search(query, top_k=5)

        if not relevant_chunks:
            return ""

        context_parts = ["RELEVANT ANTERIX INFORMATION:\n"]
        current_length = len(context_parts[0])

        for i, chunk in enumerate(relevant_chunks, 1):
            if chunk.relevance_score < 0.1:  # Skip very low relevance
                continue

            chunk_text = f"\n{i}. {chunk.title}\nSource: {chunk.url}\nContent: {chunk.content[:400]}...\n"

            if current_length + len(chunk_text) > max_tokens * 4:  # Rough token estimate
                break

            context_parts.append(chunk_text)
            current_length += len(chunk_text)

        return "".join(context_parts)

    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        return {
            "total_chunks": len(self.knowledge_chunks),
            "has_database": bool(self.spider_db_path and os.path.exists(self.spider_db_path)),
            "categories": list(set(chunk.category for chunk in self.knowledge_chunks)),
            "vocabulary_size": len(self.document_frequencies)
        }

# Test the simple RAG system
if __name__ == "__main__":
    rag = SimpleAnterixRAG()

    test_queries = [
        "What is Private LTE?",
        "How does 900 MHz spectrum work?",
        "Grid modernization benefits",
        "ROI for utilities"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = rag.search(query, top_k=3)
        for result in results:
            print(f"✅ {result.title} (score: {result.relevance_score:.3f})")

        context = rag.get_context_for_query(query)
        print(f"📄 Context: {len(context)} chars")

    stats = rag.get_stats()
    print(f"\n📊 RAG Stats: {stats}")