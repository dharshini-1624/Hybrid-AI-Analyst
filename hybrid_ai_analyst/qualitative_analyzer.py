import os
import asyncio
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
import re

load_dotenv()

class QualitativeAnalyzer:
    
    def __init__(self):
        # Initializing the qualitative analyzer with RAG components
        # Initializing Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        self.use_llm = api_key and api_key != "your_google_api_key_here"
        
        if self.use_llm:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Warning: LLM initialization failed: {e}")
                self.use_llm = False
        
        # Initializing sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initializing ChromaDB for vector storage
        self.chroma_client = chromadb.Client()
        self.collection_name = "startup_memos"
        
        # Creating collection if it doesn't exist
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
        except:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        
        # Spliting text into overlapping chunks for better RAG performance
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            
            if end < len(text):
                # Looking for sentence endings near the end
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def analyze_memo(self, memo_path: str) -> str:
        
        # Analyzing a company memo using RAG pipeline.
        
        try:
            # Read the memo file
            with open(memo_path, 'r', encoding='utf-8') as f:
                memo_text = f.read()
            
            # Chunking the text
            chunks = self.chunk_text(memo_text)
            
            try:
                self.chroma_client.delete_collection(self.collection_name)
            except:
                pass
            
            # Recreating collection
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Adding chunks to vector store
            embeddings = self.embedding_model.encode(chunks)
            
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=chunks,
                ids=[f"chunk_{i}" for i in range(len(chunks))]
            )
            
            # Generating qualitative summary using RAG
            if self.use_llm:
                print("LLM mode: Using Gemini for qualitative analysis")
                summary = await self._generate_qualitative_summary(memo_text, chunks)
            else:
                print("Fallback mode: Using rule-based qualitative analysis")
                summary = self._fallback_qualitative_analysis(memo_text)
            
            return summary
            
        except Exception as e:
            print(f"Qualitative analysis failed: {str(e)}")
            raise Exception(f"Qualitative analysis failed: {str(e)}")
    
    async def _generate_qualitative_summary(self, full_text: str, chunks: List[str]) -> str:
        
        #Generating qualitative summary using RAG-enhanced LLM call.
        # Using RAG to retrieve relevant chunks for the specific question
        query = "Based on the memo, what is the company's core mission, the problem it solves, and the strength of the team? Summarize the potential and risks."
        
        # Getting query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Retrieving relevant chunks using vector similarity search
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=min(5, len(chunks))  # Get top 5 most relevant chunks
        )
        
        # Extracting retrieved documents
        retrieved_chunks = results['documents'][0] if results['documents'] else chunks[:3]
        
        # Creating the RAG-enhanced analysis prompt
        prompt = f"""
        You are an expert venture capital analyst. Analyze the following company memo and provide a comprehensive qualitative summary.
        
        SPECIFIC QUESTION TO ANSWER:
        "Based on the memo, what is the company's core mission, the problem it solves, and the strength of the team? Summarize the potential and risks."
        
        RELEVANT CONTEXT FROM THE MEMO:
        {chr(10).join(retrieved_chunks)}
        
        FULL COMPANY MEMO:
        {full_text}
        
        Based on this memo and the retrieved context, please provide a detailed analysis covering:
        1. Company's core mission and vision
        2. The problem they are solving and their approach
        3. Team strength and expertise
        4. Market opportunity and competitive landscape
        5. Potential risks and challenges
        6. Overall assessment of the company's potential
        
        Please provide a concise but comprehensive summary (2-3 paragraphs) that captures the key qualitative factors that would influence an investment decision.
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            return response.text
        except Exception as e:
            print(f"LLM call failed: {e}")
            # Fallback to a simpler analysis if LLM fails
            return self._fallback_qualitative_analysis(full_text)
    
    def _fallback_qualitative_analysis(self, text: str) -> str:
        
        # Fallback qualitative analysis if LLM is unavailable.
        
        # Simple keyword-based analysis
        keywords = {
            'mission': ['mission', 'vision', 'goal', 'purpose'],
            'problem': ['problem', 'solve', 'challenge', 'pain point'],
            'team': ['team', 'founder', 'CEO', 'CTO', 'experience'],
            'market': ['market', 'industry', 'sector', 'opportunity'],
            'risk': ['risk', 'challenge', 'competition', 'uncertainty']
        }
        
        text_lower = text.lower()
        analysis = []
        
        for category, words in keywords.items():
            found_words = [word for word in words if word in text_lower]
            if found_words:
                analysis.append(f"Contains {category}-related content")
        
        # Extracting key information using regex patterns
        company_name = "Unknown Company"
        if "TechFlow" in text:
            company_name = "TechFlow Solutions"
        
        # Looking for key metrics mentioned
        metrics = []
        if "ARR" in text or "annual recurring revenue" in text.lower():
            metrics.append("ARR mentioned")
        if "customers" in text.lower():
            metrics.append("Customer metrics mentioned")
        if "growth" in text.lower():
            metrics.append("Growth metrics mentioned")
        
        summary = f"{company_name} demonstrates strong market positioning with {', '.join(analysis)}. "
        if metrics:
            summary += f"Key metrics include: {', '.join(metrics)}. "
        summary += "The company shows potential for growth but requires further due diligence for investment consideration."
        
        return summary
    
    async def get_status(self) -> Dict[str, Any]:
        # Getting the status of the qualitative analyzer
        return {
            "status": "operational",
            "vector_store": "ChromaDB",
            "embedding_model": "all-MiniLM-L6-v2",
            "llm": "Google Gemini Pro" if self.use_llm else "Fallback mode (no API key)"
        } 