from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


# 1️⃣ LLM (Ollama Model)
llm = ChatOllama(
    model="gemma3:1b",   # Change model if needed
    temperature=0
)


# 2️⃣ Prompt Template (Translation Engine Prompt)
prompt = ChatPromptTemplate.from_messages([
    ("system",
    """You are a Translation Engine.
Your job is to accurately translate user-provided text from the source language into the target language.

====================
RULES:
====================
1. ALWAYS translate ONLY the user's text.
2. NEVER add explanations, notes, examples or extra text.
3. Return ONLY the translated output, nothing else.
4. Maintain meaning, tone, and context.
5. Do NOT transliterate unless required by the language itself.

====================
INPUT FORMAT:
====================
Source Language: {source_lang}
Target Language: {target_lang}
Text: {text}
"""),

    ("user", "Translate the text now.")
])


# 3️⃣ Build chain (LangChain v1.0)
chain = prompt | llm


# 4️⃣ Translation function
def translate_text(text: str, source_lang: str, target_lang: str):
    result = chain.invoke({
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    })
    return result.content   

# # 5️⃣ Example usage
# if __name__ == "__main__":
#     while True:
#         print("-" * 40)
#         src = "English"
#         tgt = "Spanish"
#         txt = input("Enter text to translate: ")
#         print("-"*30)
#         print("\nTranslated Output:")
#         x = translate_text(txt, src, tgt)
#         print(x)
#         print(translate_text(x,tgt,src))
#         print("-"*30)





        


