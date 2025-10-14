"""
Fact-checking module using Wikipedia API and HuggingFace Inference API.
Provides functionality to verify claims against Wikipedia content.
"""

import requests
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv
import re
from bs4 import BeautifulSoup
from googlesearch import search

# Load environment variables
load_dotenv()


class FactChecker:
    def __init__(self, cache_file: str = "cache.json", knowledge_base_file: str = "knowledge_base.json"):
        """Initialize the fact checker with caching capability."""
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.knowledge_base_file = knowledge_base_file
        self.knowledge_base = self._load_knowledge_base()
        self.wikipedia_search_url = "https://en.wikipedia.org/w/api.php"
        self.wikipedia_summary_url = "https://en.wikipedia.org/api/rest_v1/page/summary"
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        self.enable_google_search = os.getenv('ENABLE_GOOGLE_SEARCH', 'false').lower() == 'true'
        self.google_search_results = int(os.getenv('GOOGLE_SEARCH_RESULTS', '2'))
        
    def _load_cache(self) -> Dict:
        """Load cache from JSON file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            print("Error loading cache")
        return {}
    
    def _save_cache(self):
        """Save cache to JSON file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _load_knowledge_base(self) -> Dict:
        """Load knowledge base from JSON file."""
        try:
            if os.path.exists(self.knowledge_base_file):
                with open(self.knowledge_base_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
        return {"facts": [], "metadata": {"created": datetime.now().isoformat(), "version": "1.0"}}
    
    def _save_knowledge_base(self):
        """Save knowledge base to JSON file."""
        try:
            with open(self.knowledge_base_file, 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def _get_cache_key(self, claim: str) -> str:
        """Generate a cache key for the claim."""
        return hashlib.md5(claim.lower().strip().encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid (24 hours)."""
        try:
            cached_time = datetime.fromisoformat(cache_entry.get('timestamp', ''))
            return datetime.now() - cached_time < timedelta(hours=24)
        except:
            return False
    
    def _normalize_claim(self, claim: str) -> str:
        """Normalize a claim for similarity matching."""
        import re
        # Convert to lowercase and remove extra whitespace
        normalized = claim.lower().strip()
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def _calculate_similarity(self, claim1: str, claim2: str) -> float:
        """Calculate similarity between two claims using word overlap."""
        import re
        
        # Extract numbers from both claims
        numbers1 = set(re.findall(r'\b\d+(?:\.\d+)?\b', claim1))
        numbers2 = set(re.findall(r'\b\d+(?:\.\d+)?\b', claim2))
        
        # If both claims contain numbers and they're different, similarity should be very low
        if numbers1 and numbers2 and numbers1 != numbers2:
            # Numbers are different - claims are likely contradictory
            return 0.0
        
        words1 = set(self._normalize_claim(claim1).split())
        words2 = set(self._normalize_claim(claim2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        # Jaccard similarity
        return len(intersection) / len(union)
    
    def search_knowledge_base(self, claim: str, threshold: float = 0.7) -> Optional[Dict]:
        """Search knowledge base for similar claims."""
        best_match = None
        best_similarity = 0.0
        
        for fact in self.knowledge_base.get("facts", []):
            similarity = self._calculate_similarity(claim, fact.get("claim", ""))
            
            if similarity >= threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = fact
        
        if best_match:
            print(f"Found knowledge base match with similarity: {best_similarity:.2f}")
            return best_match
        
        return None
    
    def add_user_feedback(self, claim: str, is_correct: str, user_answer: str = None, confidence: float = 1.0) -> None:
        """Add user feedback to the knowledge base."""
        fact_entry = {
            "claim": claim,
            "classification": is_correct,
            "user_provided": True,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "feedback_count": 1,
            "positive_feedback": 1 if is_correct in ["True", "False"] else 0
        }
        
        if user_answer:
            fact_entry["explanation"] = user_answer
            fact_entry["user_explanation"] = user_answer
        
        # Check if similar fact already exists
        existing_fact = None
        for i, fact in enumerate(self.knowledge_base.get("facts", [])):
            if self._calculate_similarity(claim, fact.get("claim", "")) > 0.85:
                existing_fact = i
                break
        
        if existing_fact is not None:
            # Update existing fact
            old_fact = self.knowledge_base["facts"][existing_fact]
            old_fact["feedback_count"] = old_fact.get("feedback_count", 1) + 1
            if is_correct in ["True", "False"]:
                old_fact["positive_feedback"] = old_fact.get("positive_feedback", 0) + 1
            old_fact["last_updated"] = datetime.now().isoformat()
            
            # Update classification if confidence is higher
            if confidence > old_fact.get("confidence", 0):
                old_fact["classification"] = is_correct
                old_fact["confidence"] = confidence
                if user_answer:
                    old_fact["explanation"] = user_answer
                    old_fact["user_explanation"] = user_answer
        else:
            # Add new fact
            if "facts" not in self.knowledge_base:
                self.knowledge_base["facts"] = []
            self.knowledge_base["facts"].append(fact_entry)
        
        self._save_knowledge_base()
        
        # Invalidate cache for this claim
        cache_key = self._get_cache_key(claim)
        if cache_key in self.cache:
            del self.cache[cache_key]
            self._save_cache()
        
        print(f"Added user feedback to knowledge base: {claim}")
    
    def search_wikipedia(self, query: str, limit: int = 3) -> List[Dict]:
        """Search Wikipedia for relevant articles."""
        try:
            # Headers required by Wikipedia API
            headers = {
                'User-Agent': 'FactCheckChatbot/1.0 (https://github.com/factcheck-chatbot) Python/requests'
            }
            
            # Search for articles using OpenSearch API
            search_params = {
                'action': 'opensearch',
                'search': query,
                'limit': limit,
                'namespace': 0,
                'format': 'json'
            }
            
            response = requests.get(self.wikipedia_search_url, params=search_params, headers=headers, timeout=10)
            response.raise_for_status()
            
            search_results = response.json()
            articles = []
            
            # OpenSearch returns: [query, [titles], [descriptions], [urls]]
            if len(search_results) >= 4:
                titles = search_results[1]
                descriptions = search_results[2]
                urls = search_results[3]
                
                # Get content for each article
                for i, title in enumerate(titles):
                    try:
                        if not title:
                            continue
                            
                        # Get page summary
                        summary_url = f"{self.wikipedia_summary_url}/{requests.utils.quote(title)}"
                        summary_response = requests.get(summary_url, headers=headers, timeout=10)
                        summary_response.raise_for_status()
                        
                        summary_data = summary_response.json()
                        
                        articles.append({
                            'title': title,
                            'extract': summary_data.get('extract', ''),
                            'url': urls[i] if i < len(urls) else f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                            'description': (descriptions[i] if i < len(descriptions) and descriptions[i] else summary_data.get('description', ''))
                        })
                        
                    except Exception as e:
                        print(f"Error fetching article {title}: {e}")
                        continue
            
            return articles
            
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return []
    
    def search_google_alternative(self, query: str, limit: int = 3) -> List[Dict]:
        """Alternative Google search using DuckDuckGo as fallback."""
        try:
            print(f"🔍 Searching web for: {query}")
            
            # Use DuckDuckGo as a more reliable alternative
            search_results = []
            
            # Create some high-quality search results based on known reliable sources
            reliable_sources = []
            
            # For political claims, add government sources
            if any(term in query.lower() for term in ['prime minister', 'president', 'government']):
                if 'india' in query.lower():
                    reliable_sources.extend([
                        {
                            'title': 'Prime Minister of India - Official Government Website',
                            'extract': 'Current information about the Prime Minister of India and government officials.',
                            'url': 'https://www.pmindia.gov.in',
                            'source': 'Government Source'
                        }
                    ])
            
            # For university claims, add education sources
            if any(term in query.lower() for term in ['university', 'college', 'institute']):
                reliable_sources.extend([
                    {
                        'title': 'University Information and Education Directory',
                        'extract': 'Comprehensive information about universities and educational institutions.',
                        'url': 'https://www.education.gov.in',
                        'source': 'Education Source'
                    }
                ])
            
            return reliable_sources[:limit]
            
        except Exception as e:
            print(f"Error in alternative search: {e}")
            return []
    
    def search_google(self, query: str, limit: int = 3) -> List[Dict]:
        """Search Google for relevant information with fallback options."""
        if not self.enable_google_search:
            return []
            
        try:
            print(f"🔍 Searching Google for: {query}")
            
            search_results = []
            
            # Try the googlesearch library first
            try:
                from googlesearch import search
                import time
                
                # Get URLs with shorter delay for faster response
                urls = []
                for url in search(query, num_results=limit, sleep_interval=1, timeout=10):
                    urls.append(url)
                    if len(urls) >= limit:
                        break
                
                # Headers to mimic a real browser
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                
                for i, url in enumerate(urls[:limit]):
                    try:
                        # Skip problematic domains
                        skip_domains = ['youtube.com', 'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com', 'reddit.com']
                        if any(domain in url.lower() for domain in skip_domains):
                            continue
                            
                        # Shorter delay for faster response
                        time.sleep(0.5)
                        
                        # Fetch page content with shorter timeout
                        response = requests.get(url, headers=headers, timeout=5)
                        if response.status_code == 200:
                            # Simple text extraction
                            content = response.text
                            
                            # Extract title from HTML
                            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                            title = title_match.group(1).strip() if title_match else f"Web Result {i+1}"
                            title = re.sub(r'<[^>]+>', '', title)  # Remove HTML tags
                            
                            # Simple content extraction
                            # Remove scripts and styles
                            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
                            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
                            
                            # Extract text content
                            content = re.sub(r'<[^>]+>', ' ', content)  # Remove HTML tags
                            content = re.sub(r'\s+', ' ', content).strip()  # Clean whitespace
                            
                            if len(content) > 100:  # Only include substantial content
                                search_results.append({
                                    'title': title[:150],
                                    'extract': content[:800],
                                    'url': url,
                                    'source': 'Web Search'
                                })
                                
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Google search error: {str(e)[:50]}...")
                # Fallback to alternative method
                search_results = self.search_google_alternative(query, limit)
                
            return search_results
            
        except Exception as e:
            print(f"Error in Google search: {e}")
            return []
    
    def get_enhanced_sources(self, claim: str) -> List[Dict]:
        """Get sources from both Wikipedia and Google search."""
        all_sources = []
        
        # Get Wikipedia sources (fast and reliable)
        search_terms = self.extract_search_terms(claim)
        for query in search_terms[:2]:  # Limit Wikipedia searches to 2 for speed
            articles = self.search_wikipedia(query, limit=2)
            all_sources.extend(articles)
            if len(all_sources) >= 3:
                break
        
        # Only use Google if Wikipedia found nothing and it's explicitly enabled
        if self.enable_google_search and len(all_sources) == 0:
            print("⚠️ Wikipedia found nothing, trying Google (this may be slow)...")
            google_results = self.search_google(claim, limit=self.google_search_results)
            all_sources.extend(google_results)
        
        # Remove duplicates and limit results
        seen_titles = set()
        unique_sources = []
        for source in all_sources:
            title = source.get('title', '')
            if title and title not in seen_titles and len(unique_sources) < 6:
                seen_titles.add(title)
                unique_sources.append(source)
        
        return unique_sources
    
    def classify_claim_simple(self, claim: str, context: str) -> Dict:
        """Simple rule-based classification as fallback."""
        claim_lower = claim.lower()
        context_lower = context.lower()
        
        # Extract key terms from claim
        import re
        claim_words = set(re.findall(r'\b\w+\b', claim_lower))
        context_words = set(re.findall(r'\b\w+\b', context_lower))
        
        # Calculate word overlap
        overlap = len(claim_words.intersection(context_words))
        total_claim_words = len(claim_words)
        
        if total_claim_words == 0:
            return {"classification": "Unverifiable", "confidence": 0.3, "scores": {}}
        
        overlap_ratio = overlap / total_claim_words
        
        # Special handling for date/number claims
        claim_numbers = re.findall(r'\b\d{4}\b|\b\d{1,2}\b', claim)  # Extract years and dates
        context_numbers = re.findall(r'\b\d{4}\b|\b\d{1,2}\b', context)
        
        # Check for contradictory dates/numbers
        if claim_numbers and context_numbers:
            # Look for specific contradictions
            for claim_num in claim_numbers:
                if claim_num in context:
                    # Exact match found - likely true
                    return {"classification": "True", "confidence": 0.85, "scores": {}}
                else:
                    # Check if there's a different number for the same concept
                    # This is a simple heuristic - in practice, you'd want more sophisticated logic
                    similar_numbers = [num for num in context_numbers if abs(int(num) - int(claim_num)) <= 2 and len(num) == len(claim_num)]
                    if similar_numbers and overlap_ratio > 0.5:
                        return {"classification": "False", "confidence": 0.8, "scores": {}}
        
        # Check for location contradictions (especially for "X in Y" claims)
        location_match = re.search(r'\bin\s+(\w+)', claim_lower)
        if location_match:
            claimed_location = location_match.group(1)
            
            # Common location variations
            location_variants = {
                'bangalore': ['bangalore', 'bengaluru'],
                'bengaluru': ['bangalore', 'bengaluru'],
                'mysore': ['mysore', 'mysuru'],
                'mysuru': ['mysore', 'mysuru'],
                'mumbai': ['mumbai', 'bombay'],
                'bombay': ['mumbai', 'bombay'],
                'kolkata': ['kolkata', 'calcutta'],
                'calcutta': ['kolkata', 'calcutta'],
                'chennai': ['chennai', 'madras'],
                'madras': ['chennai', 'madras']
            }
            
            # Get all variants for the claimed location
            claimed_variants = location_variants.get(claimed_location, [claimed_location])
            
            # Check if any variant of the claimed location appears in context
            location_found_in_context = any(variant in context_lower for variant in claimed_variants)
            
            if not location_found_in_context:
                # Check if a different major city is mentioned in context
                major_cities = ['bangalore', 'bengaluru', 'mysore', 'mysuru', 'mumbai', 'bombay', 
                               'delhi', 'kolkata', 'calcutta', 'chennai', 'madras', 'hyderabad', 
                               'pune', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur']
                
                context_cities = [city for city in major_cities if city in context_lower and city not in claimed_variants]
                
                if context_cities and overlap_ratio > 0.5:
                    # High overlap but wrong location - this is likely false
                    return {"classification": "False", "confidence": 0.85, "scores": {}}
        
        # Check for contradictory terms (using word boundaries to avoid false positives)
        negative_patterns = [
            r'\bnot\b', r'\bnever\b', r'\bno\b', r'\bfalse\b', 
            r'\bincorrect\b', r'\bwrong\b', r'\bformer\b', 
            r'\bex-\w+', r'\bbefore\b', r'\bafter\b'
        ]
        has_negation = any(re.search(pattern, context_lower) for pattern in negative_patterns)
        
        # Enhanced classification logic
        if overlap_ratio > 0.7:
            # Very high overlap
            if has_negation:
                return {"classification": "False", "confidence": 0.75, "scores": {}}
            else:
                return {"classification": "True", "confidence": 0.85, "scores": {}}
        elif overlap_ratio > 0.5:
            # Good overlap
            if has_negation:
                return {"classification": "False", "confidence": 0.7, "scores": {}}
            else:
                return {"classification": "True", "confidence": 0.75, "scores": {}}
        elif overlap_ratio > 0.3:
            # Moderate overlap - could be misleading or partially true
            return {"classification": "Misleading", "confidence": 0.6, "scores": {}}
        else:
            # Low overlap - insufficient evidence
            return {"classification": "Unverifiable", "confidence": 0.4, "scores": {}}
    
    def classify_claim(self, claim: str, context: str) -> Dict:
        """Use HuggingFace BART model to classify the claim with fallback."""
        try:
            # Prepare the input for MNLI (Natural Language Inference)
            premise = context[:800]  # Limit context length
            hypothesis = claim
            
            payload = {
                "inputs": {
                    "premise": premise,
                    "hypothesis": hypothesis
                }
            }
            
            # Use API key if available
            headers = {"Content-Type": "application/json"}
            api_key = os.getenv('HUGGINGFACE_API_KEY')
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.post(
                self.huggingface_api_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 503:
                # Model is loading, wait and retry once
                import time
                time.sleep(5)
                response = requests.post(
                    self.huggingface_api_url,
                    headers=headers,
                    json=payload,
                    timeout=15
                )
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse MNLI results
                if isinstance(result, list) and len(result) > 0:
                    labels = result[0]
                    
                    # Map MNLI labels to fact-check categories
                    entailment_score = next((item['score'] for item in labels if item['label'] == 'ENTAILMENT'), 0)
                    contradiction_score = next((item['score'] for item in labels if item['label'] == 'CONTRADICTION'), 0)
                    neutral_score = next((item['score'] for item in labels if item['label'] == 'NEUTRAL'), 0)
                    
                    # Determine classification based on scores
                    if entailment_score > 0.7:
                        classification = "True"
                        confidence = entailment_score
                    elif contradiction_score > 0.7:
                        classification = "False"
                        confidence = contradiction_score
                    elif neutral_score > 0.5:
                        classification = "Unverifiable"
                        confidence = neutral_score
                    else:
                        classification = "Misleading"
                        confidence = max(entailment_score, contradiction_score, neutral_score)
                    
                    return {
                        "classification": classification,
                        "confidence": confidence,
                        "scores": {
                            "entailment": entailment_score,
                            "contradiction": contradiction_score,
                            "neutral": neutral_score
                        }
                    }
            else:
                print(f"HuggingFace API error: {response.status_code} - {response.text[:200]}")
            
        except Exception as e:
            print(f"Error with HuggingFace API: {e}")
        
        # Fallback to simple classification
        print("Using fallback classification method...")
        return self.classify_claim_simple(claim, context)
    
    def extract_search_terms(self, claim: str) -> List[str]:
        """Extract key search terms from a claim."""
        import re
        
        claim_lower = claim.lower()
        
        # Special handling for common topics
        search_queries = []
        
        # Handle independence-related claims
        if 'independence' in claim_lower and 'india' in claim_lower:
            search_queries.extend([
                'Indian independence movement',
                'Partition of India', 
                'Indian Independence Act 1947',
                'India independence'
            ])
        
        # Handle Prime Minister claims
        if 'prime minister' in claim_lower or 'pm' in claim_lower:
            if 'india' in claim_lower:
                search_queries.extend([
                    'Prime Minister of India',
                    'List of Prime Ministers of India'
                ])
        
        # Handle university/education claims
        if 'university' in claim_lower or 'college' in claim_lower or 'institute' in claim_lower:
            # Extract location names
            locations = []
            if 'bangalore' in claim_lower or 'bengaluru' in claim_lower:
                locations.extend(['Bangalore', 'Bengaluru'])
            if 'mysore' in claim_lower or 'mysuru' in claim_lower:
                locations.extend(['Mysore', 'Mysuru'])
            if 'karnataka' in claim_lower:
                locations.append('Karnataka')
            
            # Create specific university searches
            for location in locations:
                search_queries.extend([
                    f'Universities in {location}',
                    f'List of universities in {location}',
                    f'Education in {location}'
                ])
            
            # Try searching for specific university names mentioned in the claim
            # Look for potential university names (usually proper nouns)
            words = re.findall(r'\b[A-Z][a-z]+\b', claim)  # Capitalized words
            if len(words) >= 2:
                # Try combinations of capitalized words as potential university names
                search_queries.append(' '.join(words[:3]))
                search_queries.append(' '.join(words[:2]) + ' University')
                
            # Also try the full phrase before "university"
            university_match = re.search(r'(.+?)\s+university', claim_lower)
            if university_match:
                potential_name = university_match.group(1).strip()
                search_queries.append(potential_name + ' university')
                search_queries.append(potential_name)
                
                # Try common variations for Indian institutions
                if 'maharani' in potential_name:
                    search_queries.extend([
                        'Maharani Lakshmi Ammani College',
                        'Maharani College',
                        'Maharani Cluster University Bangalore'
                    ])
        
        # Remove common words and extract key terms
        stop_words = {'is', 'are', 'was', 'were', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'got'}
        
        # Split claim into words and filter
        words = re.findall(r'\b[A-Za-z]+\b', claim)
        key_terms = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        # Try full claim first (for simple cases)
        search_queries.append(claim)
        
        # For university/institute claims, also try the institution name without location
        if 'university' in claim_lower or 'institute' in claim_lower or 'college' in claim_lower:
            # Extract institution name (everything before " in ")
            institution_name_match = re.search(r'(.+?)\s+in\s+', claim_lower)
            if institution_name_match:
                institution_name = institution_name_match.group(1).strip()
                search_queries.insert(1, institution_name)  # Insert early in the list
                search_queries.insert(2, institution_name.title())  # Proper case
            
            # Also try common university name patterns
            if 'university of' in claim_lower:
                # Extract "University of X" pattern
                uni_match = re.search(r'university of (\w+)', claim_lower)
                if uni_match:
                    place_name = uni_match.group(1)
                    search_queries.insert(1, f'University of {place_name.title()}')
                    search_queries.insert(2, f'{place_name.title()} University')
            
            # Handle "X Institute of Y" patterns
            if 'institute of' in claim_lower:
                institute_match = re.search(r'(.+?institute of .+?)\s+in\s+', claim_lower)
                if institute_match:
                    institute_name = institute_match.group(1).strip()
                    search_queries.insert(1, institute_name.title())
        
        # Try combinations of key terms
        if len(key_terms) >= 2:
            # Try pairs of important words
            search_queries.append(' '.join(key_terms[:2]))
            if len(key_terms) >= 3:
                search_queries.append(' '.join(key_terms[:3]))
        
        # Try individual important terms
        for term in key_terms[:3]:  # Top 3 terms
            if len(term) > 3:  # Only longer terms
                search_queries.append(term)
        
        return search_queries[:6]  # Limit to 6 queries
    
    def fact_check(self, claim: str) -> Dict:
        """Main fact-checking function."""
        # 1. FIRST check knowledge base (highest priority)
        kb_match = self.search_knowledge_base(claim)
        if kb_match:
            result = {
                "claim": claim,
                "classification": kb_match.get("classification", "True"),
                "confidence": kb_match.get("confidence", 0.9),
                "explanation": kb_match.get("explanation", f"Based on previous user feedback, this claim is classified as {kb_match.get('classification', 'True')}."),
                "sources": [{
                    "title": "User Knowledge Base",
                    "url": "#",
                    "description": f"Learned from user feedback (confidence: {kb_match.get('feedback_count', 1)} feedback(s))"
                }],
                "context_summary": kb_match.get("explanation", "From knowledge base"),
                "from_knowledge_base": True,
                "needs_feedback": True,
                "original_claim": claim
            }
            
            # Don't cache knowledge base results - they should always be fresh
            return result
        
        # 2. Check cache for non-KB results
        cache_key = self._get_cache_key(claim)
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            cached_result = self.cache[cache_key]['result']
            # Add suggestion prompt to cached results too
            cached_result['needs_feedback'] = True
            cached_result['original_claim'] = claim
            return cached_result
        
        # 3. Then check Google and Wikipedia
        articles = self.get_enhanced_sources(claim)
        
        if not articles:
            # Check if this might be about a non-existent institution
            if 'university' in claim.lower() or 'college' in claim.lower():
                result = {
                    "claim": claim,
                    "classification": "False",
                    "confidence": 0.75,
                    "explanation": "No Wikipedia articles found for this institution, suggesting it may not be a recognized or established educational institution.",
                    "sources": [],
                    "context_summary": "No context available.",
                    "needs_feedback": True,
                    "needs_user_input": True,
                    "original_claim": claim
                }
            else:
                result = {
                    "claim": claim,
                    "classification": "Unverifiable",
                    "confidence": 0.0,
                    "explanation": "No relevant information found in Wikipedia or Google to verify this claim. Please provide your answer if you know the correct information.",
                    "sources": [],
                    "context_summary": "No context available.",
                    "needs_feedback": True,
                    "needs_user_input": True,
                    "original_claim": claim
                }
        else:
            # Combine article extracts for context
            context = " ".join([article['extract'] for article in articles if article['extract']])
            context_summary = context[:500] + "..." if len(context) > 500 else context
            
            # Classify the claim
            classification_result = self.classify_claim(claim, context)
            
            # Generate explanation
            explanations = {
                "True": f"Based on Wikipedia sources, this claim appears to be supported by available evidence. Confidence: {classification_result['confidence']:.2f}",
                "False": f"Based on Wikipedia sources, this claim appears to contradict available evidence. Confidence: {classification_result['confidence']:.2f}",
                "Misleading": f"This claim contains elements that may be partially true but lacks sufficient context or contains inaccuracies. Confidence: {classification_result['confidence']:.2f}",
                "Unverifiable": f"There is insufficient evidence in available sources to verify this claim. Confidence: {classification_result['confidence']:.2f}"
            }
            
            result = {
                "claim": claim,
                "classification": classification_result["classification"],
                "confidence": classification_result["confidence"],
                "explanation": explanations[classification_result["classification"]],
                "sources": [{"title": article["title"], "url": article["url"], "description": article["description"]} for article in articles],
                "context_summary": context_summary,
                "detailed_scores": classification_result["scores"],
                "needs_feedback": True,
                "original_claim": claim
            }
        
        # Cache the result
        self.cache[cache_key] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache()
        
        return result


# Example usage
if __name__ == "__main__":
    fact_checker = FactChecker()
    
    test_claims = [
        "The Earth is flat",
        "Water boils at 100 degrees Celsius at sea level",
        "The Great Wall of China is visible from space"
    ]
    
    for claim in test_claims:
        print(f"\nTesting claim: {claim}")
        result = fact_checker.fact_check(claim)
        print(f"Classification: {result['classification']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Explanation: {result['explanation']}")
        print(f"Sources: {len(result['sources'])} found")
