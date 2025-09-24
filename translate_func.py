from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

model = ChatOllama(model="gemma2:2b-instruct-q5_0")

def translate_text(text: str, source_lang: str, target_lang: str) -> str:

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a professional translator. Translate {source_lang} text into {target_lang}. "
                   f"Always reply with only the {target_lang} translation, nothing else."),
        
        # Few-shot examples (optional, can keep generic)
        ("user", "The project is completed. Please review the attached report."),
        ("assistant", "El proyecto está completado. Por favor revise el informe adjunto."),
        
        ("user", "I will send you the updated proposal by tomorrow morning."),
        ("assistant", "Le enviaré la propuesta actualizada mañana por la mañana."),
        
        ("user", "{text}")
    ])
    
    chain = prompt | model
    response = chain.invoke({"text": text})
    return response.content

# if __name__ == "__main__":
    # english_text = "Frontend tasks are completed. I will share the updated file to you over mail."
    # spanish_translation = translate_text(english_text, source_lang="English", target_lang="Spanish")
    
    # print("English:", english_text)
    # print("Spanish:", spanish_translation)
    
    # # Another example: English → French
    # french_translation = translate_text(english_text, source_lang="English", target_lang="French")
    # print("French:", french_translation)
