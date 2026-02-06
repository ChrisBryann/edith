import pytest

pytestmark = pytest.mark.offline

def test_encryption_at_rest(rag_system):
    """
    Verifies that data stored in ChromaDB is actually encrypted.
    We fetch the raw document from the DB and ensure the plain text is not visible.
    """
    # 1. Pick a known email from dummy data
    # ID: work_102, Subject: "RE: QA Sign-off"
    email_id = "work_102"
    target_phrase = "RE: QA Sign-off"
    
    # 2. Fetch RAW data from ChromaDB (Bypassing RAG class decryption)
    # We access the underlying collection directly
    raw_result = rag_system.collection.get(ids=[email_id])
    
    assert raw_result['ids'], "Email should exist in DB"
    
    # 3. Verify Document Content is Encrypted
    encrypted_doc = raw_result['documents'][0]
    assert target_phrase not in encrypted_doc, "Raw document content should NOT contain plain text"
    assert "GREEN light" not in encrypted_doc
    
    # 4. Verify Metadata is Encrypted
    metadata = raw_result['metadatas'][0]
    encrypted_subject = metadata['subject']
    assert target_phrase not in encrypted_subject, "Metadata subject should be encrypted"
    assert encrypted_subject != target_phrase
    
    # 5. Verify Decryption Works (Sanity Check)
    decrypted_subject = rag_system.encryptor.decrypt(encrypted_subject)
    assert decrypted_subject == target_phrase, "Decryption should restore original text"

def test_pii_scrubbing(rag_system):
    """Unit test for the PII Scrubber."""
    text = "Contact me at 555-0199 or test@example.com regarding the project."
    scrubbed, mapping = rag_system.scrubber.scrub(text)
    
    assert "555-0199" not in scrubbed
    assert "test@example.com" not in scrubbed
    assert "<PHONE" in scrubbed
    assert "<EMAIL" in scrubbed
    
    restored = rag_system.scrubber.restore(scrubbed, mapping)
    assert restored == text