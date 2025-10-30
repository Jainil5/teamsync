from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

model = ChatOllama(model="gemma2:2b-instruct-q5_0")

def translate_text(text: str, source_lang: str, target_lang: str) -> str:

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a professional translator. Translate {source_lang} text into {target_lang}. "
                   f"Always reply with only the {target_lang} translation, nothing else."),
        
        ("user", "The project is completed. Please review the attached report."),
        ("assistant", "El proyecto está completado. Por favor revise el informe adjunto."),
        
        ("user", "I will send you the updated proposal by tomorrow morning."),
        ("assistant", "Le enviaré la propuesta actualizada mañana por la mañana."),
        
        ("user", "{text}")
    ])
    
    chain = prompt | model
    response = chain.invoke({"text": text})
    return response.content

# print(translate_text("Can you help me with the translation?", "English", "Spanish"))