import csv
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 
import streamlit as st
import time
from gtts import gTTS
import os
#import playsound
import speech_recognition as sr
from googletrans import Translator
#set up user interface
st.title(':green[স্বাস্থ্য সহায়িকা]')
st.subheader('আপনার মাসিকজনিত সমস্যাগুলো নির্দ্বিধায়ে আমাদের বলুন ')

search_result = ""
translator = Translator()
#function to find the best matching result
def return_result(dict, query, threshold):
    try:
        time.sleep(3)
        scores = []
        for key, value in enumerate(dict):
            ratios = [fuzz.ratio(str(query), str(value))] # ensure both are in string
            scores.append({ "index": key, "score": max(ratios)})

        filtered_scores = [item for item in scores if item['score'] >= threshold]
        sorted_filtered_scores = sorted(filtered_scores, key = lambda k: k['score'], reverse=True)
        index = sorted_filtered_scores[0]['index']
        result = list(list(dict.items())[index])
        return result[1]
    except:
        return "দুঃখিত আপনার প্রশ্নের উত্তর আমার জানা নেই "
# Function to open and read the dataset from CSV
def open_dataset():
    with open('bangla_dataset.csv', mode='r', encoding="utf8") as infile:
        reader = csv.reader(infile)
        mydict = {rows[0]:rows[1] for rows in reader}
        return mydict
#load the dataset
with st.spinner('Loading dataset...'):
    dataset = open_dataset()
#set up the tabs for home and settings
tab1, tab2 = st.tabs(["Home", "Settings"])
#settings tab
with tab2:
    threshold = st.slider("Threshold", 0, 100, 50) # a number which ranges from 0 to 100, adjust it as per your requirement
    allow_text_to_speech = st.checkbox('Read out answers', value=True)
    allow_translated_text_display = st.checkbox('Display translated English text', value=True)

#home tab
with tab1:
    
    #def capture_voice_input():
    
    st.write("আপনার প্রশ্ন বলতে 'কথা বলুন' বাটন চাপুন:")
    # audio = recognizer.listen(source, phrase_time_limit=10)
    voice_input_button = st.button("কথা বলুন")
query = ""

if voice_input_button:
    recognizer = sr.Recognizer()
    
    with st.spinner("শুনছি..."):
        with sr.Microphone() as source:
            audio = recognizer.listen(source, phrase_time_limit=10)
            #st.write("Recognizing...")
    try:
        query = recognizer.recognize_google(audio, language='bn-BD')
        st.write(f"প্রশ্নটি: {query}")
    except sr.UnknownValueError:
        st.write("দুঃখিত, আমি আপনার প্রশ্ন বুঝতে পারিনি। অনুগ্রহ করে নিশ্চিত করুন যে আপনার প্রশ্ন পরিষ্কার এবং আবার চেষ্টা করুন।")
    if allow_translated_text_display:
        try:
            translated_query = translator.translate(query, src='bn', dest='en').text
            st.write(f"{translated_query}")
        except sr.UnknownValueError:
            st.write("Sorry, I didn't understand your question. Please make sure your question is clear and try again.")  
    #query = capture_voice_input()

#perform the search
    with st.spinner('অনুসন্ধান করছি. অনুগ্রহপূর্বক অপেক্ষা করুন...'):
        with st.empty():
            search_result = return_result(dataset, query, threshold)
            st.write(search_result)
    if allow_translated_text_display and query:
        with st.empty():
            search_result = return_result(dataset, query, threshold)
            translated_result = translator.translate(search_result, src='bn', dest='en').text
            st.write(f"Answer (Translated): {translated_result}")
        
#text-to-speech feature
    if allow_text_to_speech:
            tts = gTTS(text=search_result, lang='bn', slow=False)
            filename = os.path.dirname(__file__)+ "/" + "result.mp3"
            tts.save(filename)
            # playsound.playsound(filename)
            audio_file = open(filename, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/ogg')
            # os.remove(filename)