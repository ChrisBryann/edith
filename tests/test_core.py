import pytest

pytestmark = pytest.mark.offline

@pytest.mark.parametrize("scenario, question, expected_phrases", [
    ("Work Deadline", "When is the deadline for Project Phoenix?", ["November 15", "Friday"]),
    ("Technical Details", "What port is the staging environment using?", ["8080"]),
    ("Personal Event", "Where is Mom's birthday party?", ["Italian Place", "Main St"]),
    ("Travel Details", "What is my seat number for the Tokyo flight?", ["14A"]),
])
def test_rag_retrieval(rag_system, scenario, question, expected_phrases):
    """Tests that the RAG system can retrieve and answer correctly."""
    answer = rag_system.answer_question(question)
    print(f"\nQ: {question}\nA: {answer}")
    
    # Check if any of the expected phrases are in the answer
    found = any(phrase.lower() in answer.lower() for phrase in expected_phrases)
    assert found, f"Expected one of {expected_phrases} in answer: '{answer}'"

def test_rag_negative_case(rag_system):
    """Tests that the system gracefully handles missing information."""
    question = "What is the budget for Project Phoenix?"
    answer = rag_system.answer_question(question)
    
    # LLM-as-a-Judge: Ask Gemini if the answer is a refusal
    # This is more robust than string matching for natural language variations
    prompt = f"""
    Question: {question}
    Answer: {answer}
    
    Does the answer indicate that the information was NOT found or is unknown?
    Respond with exactly YES or NO.
    """
    
    response = rag_system.client.models.generate_content(
        model=rag_system.config.gemini_model,
        contents=prompt
    )
    
    is_refusal = "YES" in response.text.strip().upper()
    assert is_refusal, f"System should admit ignorance. Got: '{answer}'"

def test_audio_transcription_mock(rag_system):
    """Tests the audio transcription interface (connectivity check)."""
    # Dummy MP3 header + silence
    dummy_audio = b'\xFF\xF3\x44\xC4' + b'\x00' * 100
    
    # We expect it to run without crashing, even if the audio is garbage
    try:
        transcript = rag_system.transcribe_audio(dummy_audio)
        assert isinstance(transcript, str)
        assert len(transcript) > 0
    except Exception as e:
        pytest.fail(f"Transcription raised exception: {e}")