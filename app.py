import re
import preprocessor,helper
import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

st.sidebar.write("💡 Upload your exported WhatsApp chat here (usually a `.txt` file). We'll analyze your messages, emojis, media, and links! 📊💬")

uploaded_file = st.sidebar.file_uploader("📂 Choose a file:")

if uploaded_file is not None:
    bytes_data=uploaded_file.getvalue()
    data=bytes_data.decode("utf-8")
   
    df=preprocessor.preproces(data)


    users_list=df['users'].unique().tolist()
    users_list.remove('group_notification')
    users_list.sort()
    users_list.insert(0,"overall")

    selected_user=st.sidebar.selectbox("👤 Show analysis of:",users_list)

    if st.sidebar.button("📈 Show Analysis"):

        st.title("📈 Top Statistics 📊")
        st.markdown("<div style='margin-top: 20px'></div>", unsafe_allow_html=True)

        num_messages, words,media_count, links_count=helper.fetch_stats(selected_user,df)

        col1,col2,col3,col4=st.columns(4)

        with col1:
            st.header("📝 Total Messages")
            st.subheader(num_messages)

        with col2:
            st.header("🖋️ Total Words")
            st.subheader(words)

        with col3:
            st.header("📷 Total Media Files")
            st.subheader(media_count)

        with col4:
            st.header("🔗 Total Links")
            st.subheader(links_count)

        st.markdown("<div style='margin-top: 50px'></div>", unsafe_allow_html=True)


        if selected_user=='overall':

            col1,col2 = st.columns(2)
            with col1:
                st.header("🔥 Most Busy Users")
                busy_users={}
                busy_users=df['users'].value_counts().head()
            
                busy_users.pop('group_notification')
                fig, ax = plt.subplots()

                busy_users.plot(kind='bar', ax=ax,color='teal')
                st.pyplot(fig)

            with col2:
                st.header("📊 Users Contribution Percentage")
                # Create the dataframe
                created_df = round((df['users'].value_counts()/df.shape[0])*100, 2).reset_index()
                created_df.columns = ['User', 'Percentage']
                created_df = created_df[created_df['User'] != 'group_notification']

                # Add top margin before displaying the table
                st.markdown("<div style='margin-top: 70px'></div>", unsafe_allow_html=True)

                # Display the table
                st.dataframe(created_df, width=500)  # wider table


        st.header("☁️ WordCloud")
        fig, ax = plt.subplots()
        df_wc = helper.create_wordcloud(selected_user, df)
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)


        st.header("📚 Most Common Words")
        new_df = helper.top_20_words(selected_user, df)
        fig,ax=plt.subplots()
        new_df.plot(kind='barh',ax=ax)
        st.pyplot(fig)


        st.header("😊 Emoji Analysis")
        col1,col2=st.columns(2)

        with col1:
            emoji_counter=helper.emoji_counter(selected_user,df)
            new_df=pd.DataFrame(emoji_counter)
            new_df.columns=['Emoji','Count']
            new_df.reset_index(drop=True, inplace=True)
            new_df.index += 1
            st.dataframe(new_df,width=400)
        with col2:
            emoji_counter=helper.emoji_counter(selected_user,df)
            new_df=pd.DataFrame(emoji_counter)
            new_df.columns=['Emoji','Count']
            matplotlib.rcParams['font.family'] = 'Segoe UI Emoji'
            new_df=new_df.head(5)
            fig,ax=plt.subplots()
            ax.pie(new_df['Count'],labels=new_df['Emoji'],autopct="%1.1f")

            ax.axis('equal')
            st.pyplot(fig)


        st.header("⏱️ Time Analysis")
        timeline=helper.timeline_analysis(selected_user,df)
        
        fig,ax=plt.subplots(figsize=(12,5))
        
        ax.plot(timeline['time'],timeline['message'])
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Messages", fontsize=12)
        ax.set_title("📅 Monthly Message Timeline")
        plt.xticks(rotation=90)
        st.pyplot(fig)

        daily_timeline=helper.daily_timeline_analysis(selected_user,df)
        fig,ax=plt.subplots(figsize=(8,5))

        ax.plot(daily_timeline['only_date'],daily_timeline['message'])
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Messages", fontsize=12)
        ax.set_title("🗓️ Daily Message Timeline")
        
        st.pyplot(fig)

        col1,col2=st.columns(2)

        with col1:
            st.header("📅 Most Busy Days")
            day_name_analysis=helper.day_name_analysis(selected_user,df)

            fig,ax=plt.subplots(figsize=(12,10))
            bars=ax.bar(day_name_analysis['day_name'],day_name_analysis['message'])
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    int(height),
                    ha='center',
                    va='bottom'
                )
            ax.set_xlabel("Days", fontsize=16)
            ax.tick_params(axis='x', labelsize=16)
            ax.tick_params(axis='y', labelsize=16)
            ax.set_yticks([])
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Number of Messages", fontsize=16)
            

            st.pyplot(fig)

        with col2:
            st.header("📆 Most Busy Months")
            month_analysis = helper.monthly_analysis(selected_user, df)

            fig, ax = plt.subplots(figsize=(12,10))
            bars = ax.bar(month_analysis['month'], month_analysis['message'])

            # 🔑 Add labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    int(height),
                    ha='center',
                    va='bottom'
                )
            ax.set_xlabel("Month", fontsize=16)
            ax.tick_params(axis='x', labelsize=16)
            ax.tick_params(axis='y', labelsize=16)
            plt.xticks(rotation='vertical')
            ax.set_ylabel("Number of Messages", fontsize=16)
            ax.set_yticks([])
            st.pyplot(fig)


        st.header("🗓️ Weekly Activity Map")
        df = helper.daily_activness(selected_user, df)

        order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        heatmap_data = df.pivot_table(
            index='day_name',
            columns='period',
            values='message',
            aggfunc='count'
        ).reindex(order)
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(heatmap_data, ax=ax)
        plt.xticks(rotation='horizontal')
        plt.yticks(rotation='horizontal')
        st.pyplot(fig)

        
    

    else:
        # Show intro only before analysis
        st.title("💬 WhatsApp Chat Analyzer 📊")
        st.write("🔥 Check out your top chat stats! See who talks the most, how many words you send, media shared, and links posted. 🚀💬📷🔗")
