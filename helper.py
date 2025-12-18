import re
from wordcloud import WordCloud
import pandas as pd
import emoji
from collections import Counter

def fetch_stats(selected_user,df):

    if selected_user !='overall':
        df=df[df['users']==selected_user]

    # returns total nof of messages
    num_messages= df.shape[0]

    #total no of words
    words=[]
    for message in df['message']:
        words.extend(message.split(" "))
        
    words=len(words)

    #total no of medias shared
    media_count=0
    media_count_pattern = r"\s*<\s*Media\s+omitted\s*>\s*"
    for message in df['message']:
        result=re.findall(media_count_pattern,message)

        if result:
            media_count+=1


    links_count=0
    links_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    for message in df['message']:
        result=re.findall(links_pattern,message)

        if result:
            links_count+=1

    return num_messages,words,media_count,links_count
    
def create_wordcloud(selected_user, df):
    if selected_user != "overall":
        df = df[df['users'] == selected_user]

    removed_stopwords = []

    media_words = {
        "<media", "omitted>", "media", "omitted", "<media omitted>"
    }

    with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
        stop_words = set(f.read().split('\n'))

    for message in df['message']:
        for word in message.lower().split():
            if word not in stop_words and word not in media_words:
                removed_stopwords.append(word)

    clean_text = " ".join(removed_stopwords)

    wc = WordCloud(
        width=500,
        height=500,
        background_color='white',
        min_font_size=11
    )

    df_wc=wc.generate(clean_text)
    return df_wc

def top_20_words(selected_user,df):

    if selected_user !='overall':
        df=df[df['users']==selected_user]

    words=[]

    for message in df['message']:
        words.extend(message.split())

    
    new_df=pd.DataFrame(words,columns=['words'])

    
    word1="<Media"
    word2="omitted>"

    new_df=new_df[~new_df['words'].isin([word1, word2])]

    f=open('stop_hinglish.txt','r',encoding='utf-8')
    stop_words=f.read()
    stop_words=stop_words.split('\n')

    new_df=new_df[~new_df['words'].isin(stop_words)]
    
    result = new_df['words'].value_counts().head(20)
    result.columns = ['Words', 'Count']
    return result

def emoji_counter(selected_user,df):

    if selected_user !='overall':
        df=df[df['users']==selected_user]
 
    emojis = []

    for message in df['message']:
        emoji_data = emoji.emoji_list(message)
        for e in emoji_data:
            emojis.append(e['emoji'])

    emoji_counter = Counter(emojis)
    emoji_counter=emoji_counter.most_common()
    return emoji_counter

def timeline_analysis(selected_user, df):
    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

    df['month_num'] = df['date'].dt.month

    timeline = (
        df.groupby(['year', 'month_num', 'month'])
          .count()['message']
          .reset_index()
    )

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline_analysis(selected_user, df):
    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

    df = df.copy()

    df['only_date'] = df['date'].dt.date

    daily_timeline = (
        df.groupby('only_date')
          .count()
          .reset_index()
    )

    return daily_timeline

def day_name_analysis(selected_user,df):

    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

   
    day_name_analysis=df.groupby(['day_name']).count()['message'].reset_index()

    return day_name_analysis

def monthly_analysis(selected_user,df):
    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

    month_analysis=df.groupby(['month']).count()['message'].reset_index()

    return month_analysis

def daily_activness(selected_user, df):
    if selected_user != 'overall':
        df = df[df['users'] == selected_user]

    period = []

    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour+1}")

    df = df.copy()        # IMPORTANT
    df['period'] = period

    return df
