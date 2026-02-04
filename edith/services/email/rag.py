import chromadb
from chromadb.utils import embedding_functions
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from edith.lib.shared.models.email import EmailMessage
from edith.config import EmailAssistantConfig
from edith.services.security.scrubber import PIIScrubber
from edith.services.security.encryption import DataEncryptor
from edith.services.security.guard import PromptGuard

class EmailRAGSystem:
    def __init__(self, config: EmailAssistantConfig):
        self.config = config
        self.client = genai.Client(api_key=config.gemini_api_key)
        
        # Initialize ChromaDB
        if config.chroma_server_host:
            print(f"   🔌 Connecting to ChromaDB Server at {config.chroma_server_host}:{config.chroma_server_port}...")
            self.chroma_client = chromadb.HttpClient(
                host=config.chroma_server_host, 
                port=config.chroma_server_port
            )
        else:
            self.chroma_client = chromadb.PersistentClient(path=config.chroma_db_path)
            
        self.collection = self.chroma_client.get_or_create_collection(
            name="email_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Explicitly load embedding function so we can generate embeddings on plaintext
        # before encrypting the content for storage.
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        # Initialize Privacy Scrubber
        self.scrubber = PIIScrubber()
        # Initialize At-Rest Encryption
        self.encryptor = DataEncryptor(config.encryption_key)
        # Initialize Prompt Guard
        self.prompt_guard = PromptGuard()
    
    def index_emails(self, emails: List[EmailMessage]):
        """Index relevant emails in the vector database"""
        documents = []
        metadatas = []
        ids = []
        
        for email in emails:
            if email.is_relevant:
                # Security Check: Prompt Injection
                if not self.prompt_guard.validate(email.subject + " " + email.body):
                    print(f"   🛡️ Security Alert: Skipping email '{email.subject[:30]}...' due to potential prompt injection.")
                    continue

                # Create a searchable document
                doc_text = f"""
                Subject: {email.subject}
                From: {email.sender}
                Date: {email.date.strftime('%Y-%m-%d')}
                Body: {email.body[:1000]}  # Limit body length for indexing
                """
                
                # 1. Generate Embedding on PLAINTEXT (so search works)
                # We do this later in batch, just preparing lists here
                plain_doc = doc_text.strip()
                documents.append(plain_doc)
                
                # 2. Prepare Metadata (Encrypt sensitive fields)
                metadatas.append({
                    'email_id': email.id,
                    'subject': self.encryptor.encrypt(email.subject),
                    'sender': self.encryptor.encrypt(email.sender),
                    'date': email.date.isoformat(),
                    'account_type': email.account_type
                })
                ids.append(email.id)
        
        if documents:
            # Generate embeddings on plaintext
            embeddings = self.embedding_fn(documents)
            
            # 3. Encrypt Document Content for Storage
            encrypted_documents = [self.encryptor.encrypt(doc) for doc in documents]
            
            # Add to ChromaDB
            self.collection.upsert(
                documents=encrypted_documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
    
    def search_emails(self, query: str, n_results: int = 30) -> List[Dict[str, Any]]:
        """Search for relevant emails based on a query"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    
                    # Decrypt data for application use
                    decrypted_doc = self.encryptor.decrypt(doc)
                    metadata['subject'] = self.encryptor.decrypt(metadata['subject'])
                    metadata['sender'] = self.encryptor.decrypt(metadata['sender'])
                    
                    # Security Check: Filter out unsafe content on retrieval (Defense in Depth)
                    if not self.prompt_guard.validate(decrypted_doc) or not self.prompt_guard.validate(metadata['subject']):
                        print(f"   🛡️ Security Alert: Excluded retrieved document '{metadata['subject']}' due to potential prompt injection.")
                        continue
                    
                    search_results.append({
                        'document': decrypted_doc,
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if 'distances' in results else 0
                    })
            
            return search_results
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def answer_question(self, question: str, additional_context: str = "", return_sources: bool = False, n_results: int = 30) -> Union[str, Dict[str, Any]]:
        """Answer a user's question using RAG"""
        
        # 1. Input Guard: Check the user's question for injection attempts
        if not self.prompt_guard.validate(question):
            msg = "I cannot answer this question as it triggered a security alert (Prompt Injection detected)."
            if return_sources:
                return {"answer": msg, "sources": [], "context_used": ""}
            return msg
            
        print(f"   [RAG] Querying vector DB for: '{question}'")
        # Search for relevant emails
        search_results = self.search_emails(question, n_results=n_results)
        
        if search_results:
            print(f"   [RAG] Retrieved {len(search_results)} context documents:")
            for res in search_results:
                print(f"      - {res['metadata']['subject']} (Score: {res.get('distance', 0):.4f})")
        
        if not search_results and not additional_context:
            msg = "I couldn't find any relevant emails to answer your question."
            if return_sources:
                return {"answer": msg, "sources": [], "context_used": ""}
            return msg
        
        # Build context from search results
        email_context = "No relevant emails found."
        if search_results:
            email_context = "\n\n".join([
                f"Email from {result['metadata']['sender']} on {result['metadata']['date']}:\n"
                f"Subject: {result['metadata']['subject']}\n"
                f"Content: {result['document']}"
                for result in search_results
            ])
        
        # Generate answer using Gemini
        try:
            prompt = f"""You are Edith, an intelligent and helpful personal AI assistant.
Your goal is to help the user manage their digital life by synthesizing information from their emails and calendar.

Guidelines:
1. **Tone**: Be conversational, warm, and professional (like Google Gemini). Avoid robotic or overly terse responses.
2. **Accuracy**: Answer strictly based on the provided context. If the information is missing, politely say so.
3. **Synthesis**: When asked about lists (e.g., "jobs applied to"), aggregate the information rather than just listing emails.
4. **Transparency**: If you are summarizing a large number of items, mention that this is based on the most relevant emails found.

Additional Context (Calendar/System):
<calendar_context>
{additional_context}
</calendar_context>

Email Context:
<email_context>
{email_context}
</email_context>

Question: {question}"""
            
            # --- Privacy Layer: Scrub PII before sending to LLM ---
            scrubbed_prompt, pii_mapping = self.scrubber.scrub(prompt)
            
            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=scrubbed_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower temperature for more factual answers
                )
            )
            
            # --- Privacy Layer: Restore PII in the response ---
            final_answer = self.scrubber.restore(response.text, pii_mapping)
            
            if return_sources:
                return {
                    "answer": final_answer,
                    "sources": search_results,
                    "context_used": email_context
                }
            return final_answer
        except Exception as e:
            print(f"Error generating answer: {e}")
            if "404" in str(e) and "models/" in str(e):
                print(f"⚠️  Tip: Try setting GEMINI_MODEL='gemini-2.5-flash' in your .env file.")
            msg = "I'm having trouble processing your question right now."
            if return_sources:
                return {"answer": msg, "sources": [], "context_used": ""}
            return msg
    
    def get_email_summary(self, days: int = 7) -> str:
        """Get a summary of recent emails"""
        # This would require date-based filtering in ChromaDB
        # For now, we'll get recent emails and filter them
        recent_query = f"emails from the last {days} days"
        search_results = self.search_emails(recent_query, n_results=30)
        
        if not search_results:
            return f"No relevant emails found in the last {days} days."
        
        context = "\n\n".join([
            f"From: {result['metadata']['sender']} | {result['metadata']['subject']}"
            for result in search_results
        ])
        
        try:
            prompt = f"""Summarize the key points from these emails from the last {days} days. Focus on action items and important information.

Emails:
{context}"""
            
            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "I'm having trouble generating a summary right now."

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str = "audio/mp3") -> str:
        """Transcribe audio content using Gemini"""
        try:
            prompt = "Transcribe this audio file exactly as spoken."
            
            response = self.client.models.generate_content(
                model=self.config.gemini_model,
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                    prompt
                ]
            )
            transcript = response.text
            
            # 2. Ingestion Guard: Check the generated transcript before returning/using it
            if not self.prompt_guard.validate(transcript):
                return "[Transcript Redacted: Security Alert - Potential Prompt Injection Detected]"
                
            return transcript
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return "Error processing audio file."