from googletrans import Translator

translator = Translator()

def user_input(text_to_translate): # 한글 -> 영어
    translated = translator.translate(text_to_translate, dest='en')
    return translated

def user_output(text_to_translate): # 영어 -> 한글
    translated = translator.translate(text_to_translate, dest='ko')
    return translated

