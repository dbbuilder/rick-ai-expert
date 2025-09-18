"""
Knowledge Integration for Rick - Retrieval-Augmented Generation (RAG)
Integrates scraped Anterix data with GPT-4o mini responses
"""

import os
import sqlite3
import json
import base64
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from loguru import logger

@dataclass
class KnowledgeChunk:
    """Represents a chunk of Anterix knowledge"""
    id: str
    url: str
    title: str
    content: str
    category: str
    embedding: Optional[np.ndarray] = None
    relevance_score: float = 0.0

class AnterixRAG:
    """Retrieval-Augmented Generation for Anterix knowledge"""

    def __init__(self, spider_db_path: str = None):
        self.spider_db_path = spider_db_path or self._find_spider_db()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_chunks: List[KnowledgeChunk] = []
        self.faiss_index = None

        logger.info(f"Initializing Anterix RAG system...")
        self._load_knowledge()
        self._build_vector_index()

    def _find_spider_db(self) -> Optional[str]:
        """Find the spider database"""
        possible_paths = [
            "/mnt/d/dev2/clients/anterix/scraper/spider_anterix_full.db",
            "/mnt/d/dev2/clients/anterix/scraper/spider_anterix.db",
            "../scraper/spider_anterix_full.db",
            "../scraper/spider_anterix.db"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found spider database: {path}")
                return path

        logger.warning("No spider database found - RAG will have limited knowledge")
        return None

    def _load_knowledge(self):
        """Load and chunk knowledge from spider database"""
        if not self.spider_db_path:
            logger.warning("No spider database - creating demo knowledge")
            self._create_demo_knowledge()
            return

        try:
            conn = sqlite3.connect(self.spider_db_path)
            cursor = conn.cursor()

            # Get all pages with content
            cursor.execute("""
                SELECT url, title, content, meta_description, headings, word_count
                FROM pages
                WHERE content IS NOT NULL AND content != ''
                ORDER BY word_count DESC
            """)

            pages = cursor.fetchall()
            logger.info(f"Loading {len(pages)} pages from spider database")

            for page in pages:
                url, title, content, meta_desc, headings_json, word_count = page

                # Decode base64 content if needed
                decoded_content = self._decode_content(content)

                # Create knowledge chunks
                chunks = self._chunk_content(url, title, decoded_content, meta_desc)
                self.knowledge_chunks.extend(chunks)

            conn.close()
            logger.info(f"Created {len(self.knowledge_chunks)} knowledge chunks")

        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")
            self._create_demo_knowledge()

    def _decode_content(self, content: str) -> str:
        """Decode base64 content if needed"""
        try:
            # Try to decode as base64 first
            decoded_bytes = base64.b64decode(content)
            return decoded_bytes.decode('utf-8')
        except:
            # If not base64, return as-is
            return content

    def _chunk_content(self, url: str, title: str, content: str, meta_desc: str = None) -> List[KnowledgeChunk]:
        """Split content into manageable chunks"""
        chunks = []

        # Clean content
        clean_content = self._clean_html_content(content)

        # Create title chunk
        title_chunk = KnowledgeChunk(
            id=f"{url}#title",
            url=url,
            title=title,
            content=f"Title: {title}\nDescription: {meta_desc or ''}\n\nPage URL: {url}",
            category=self._categorize_url(url)
        )
        chunks.append(title_chunk)

        # Split content into paragraphs/sections
        paragraphs = clean_content.split('\n\n')
        current_chunk = ""
        chunk_num = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If adding this paragraph would make chunk too long, save current and start new
            if len(current_chunk) + len(paragraph) > 1000 and current_chunk:
                chunk = KnowledgeChunk(
                    id=f"{url}#chunk_{chunk_num}",
                    url=url,
                    title=f"{title} (Section {chunk_num + 1})",
                    content=current_chunk.strip(),
                    category=self._categorize_url(url)
                )
                chunks.append(chunk)
                current_chunk = paragraph
                chunk_num += 1
            else:
                current_chunk += f"\n\n{paragraph}" if current_chunk else paragraph

        # Add final chunk if there's content
        if current_chunk.strip():
            chunk = KnowledgeChunk(
                id=f"{url}#chunk_{chunk_num}",
                url=url,
                title=f"{title} (Section {chunk_num + 1})" if chunk_num > 0 else title,
                content=current_chunk.strip(),
                category=self._categorize_url(url)
            )
            chunks.append(chunk)

        return chunks

    def _clean_html_content(self, content: str) -> str:
        """Clean HTML content to extract readable text"""
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text and clean it
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except:
            return content  # Return as-is if parsing fails

    def _categorize_url(self, url: str) -> str:
        """Categorize content based on URL"""
        url_lower = url.lower()

        if any(term in url_lower for term in ['900-mhz', 'spectrum', 'plte', 'private-lte']):
            return "Technology"
        elif any(term in url_lower for term in ['solution', 'utility', 'grid']):
            return "Solutions"
        elif any(term in url_lower for term in ['business', 'roi', 'cost']):
            return "Business"
        elif any(term in url_lower for term in ['security', 'cyber']):
            return "Security"
        elif any(term in url_lower for term in ['about', 'company']):
            return "Company"
        else:
            return "General"

    def _create_demo_knowledge(self):
        """Create demo knowledge when no spider database is available"""
        demo_content = [
            {
                "title": "Private LTE Overview",
                "content": """Anterix provides Private LTE solutions using licensed 900 MHz spectrum for critical infrastructure. Private LTE networks give utilities their own dedicated broadband wireless communications infrastructure, ensuring secure, reliable connectivity for grid modernization applications. Key benefits include enhanced cybersecurity, improved coverage, and reduced operational costs compared to leased circuits.""",
                "url": "https://anterix.com/private-lte",
                "category": "Technology"
            },
            {
                "title": "900 MHz Spectrum Benefits",
                "content": """The 900 MHz band offers superior propagation characteristics for wide-area coverage. Licensed spectrum ensures interference-free operation and dedicated bandwidth for critical infrastructure applications. Anterix holds the largest portion of 900 MHz spectrum specifically allocated by the FCC for critical infrastructure communications.""",
                "url": "https://anterix.com/900-mhz-spectrum",
                "category": "Technology"
            },
            {
                "title": "Grid Modernization Solutions",
                "content": """Anterix Private LTE enables comprehensive grid modernization including Advanced Metering Infrastructure (AMI), Distribution Automation (DA), outage management, field workforce communications, and video surveillance. These applications improve operational efficiency, enhance grid reliability, and support the transition to clean energy.""",
                "url": "https://anterix.com/grid-modernization",
                "category": "Solutions"
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

    def _build_vector_index(self):
        """Build FAISS vector index for fast similarity search"""
        if not self.knowledge_chunks:
            logger.warning("No knowledge chunks to index")
            return

        logger.info("Building vector embeddings...")

        # Generate embeddings for all chunks
        texts = [chunk.content for chunk in self.knowledge_chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Store embeddings in chunks
        for i, embedding in enumerate(embeddings):
            self.knowledge_chunks[i].embedding = embedding

        # Build FAISS index
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.faiss_index.add(embeddings.astype('float32'))

        logger.info(f"Built FAISS index with {len(self.knowledge_chunks)} chunks")

    def search(self, query: str, top_k: int = 5) -> List[KnowledgeChunk]:
        """Search for relevant knowledge chunks"""
        if not self.faiss_index or not self.knowledge_chunks:
            return []

        # Encode query
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), top_k)

        # Return relevant chunks with scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.knowledge_chunks):
                chunk = self.knowledge_chunks[idx]
                chunk.relevance_score = float(score)
                results.append(chunk)

        return results

    def get_context_for_query(self, query: str, max_tokens: int = 2000) -> str:
        """Get relevant context for a query, respecting token limits"""
        relevant_chunks = self.search(query, top_k=10)

        context_parts = ["RELEVANT ANTERIX INFORMATION:\n"]
        current_tokens = len(context_parts[0]) // 4  # Rough token estimate

        for i, chunk in enumerate(relevant_chunks, 1):
            chunk_text = f"\n{i}. {chunk.title}\nSource: {chunk.url}\nContent: {chunk.content}\n"
            chunk_tokens = len(chunk_text) // 4  # Rough estimate

            if current_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(chunk_text)
            current_tokens += chunk_tokens

        return "".join(context_parts)

# Test the RAG system
if __name__ == "__main__":
    rag = AnterixRAG()

    test_queries = [
        "What is Private LTE?",
        "How does 900 MHz spectrum work?",
        "Grid modernization benefits"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = rag.search(query, top_k=3)
        for result in results:
            print(f"✅ {result.title} (score: {result.relevance_score:.3f})")
            print(f"   {result.content[:100]}...")

        context = rag.get_context_for_query(query)
        print(f"📄 Context length: {len(context)} chars")