from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from dotenv import load_dotenv
import streamlit as st
from kth_most_similar_outlooks import player_df
from kth_most_similar_outlooks import find_similar_players

load_dotenv()

positions = player_df['position'].unique()

llm = ChatAnthropic(model='claude-3-opus-20240229', temperature=0.7)


# Returns all players who match specified position
def get_players_by_position(position):
    return player_df[player_df['position'] == st.session_state.player_position]['name']

# Update player names in select boxes based on selected position
def update_player_names():
    position = st.session_state.player_position
    st.session_state.player_names = get_players_by_position(position)

# Initialize player_names in session state if it doesn't exist
if 'player_names' not in st.session_state:
    st.session_state.player_names = player_df['name'].tolist()

def generate_player_comparison(player_one, player_two):
    player_one_name = player_one['name']
    player_one_position = player_one['position']
    player_one_outlook = player_one['outlook']

    player_two_name = player_two['name']
    player_two_position = player_two['position']
    player_two_outlook = player_two['outlook']

    prompt_template = PromptTemplate(
        input_variables=['player_one_name', 'player_two_name', 'player_one_outlook', 'player_two_outlook'],
        template=
        '''
        Here's a template for analyzing and comparing two players' fantasy football outlooks:
        Player Comparison Template
        Player 1: {player_one_name}
        Outlook: {player_one_outlook}
        Player 2: {player_two_name}
        Outlook: {player_two_outlook}
        Analyze the sentiment of both player outlooks. Provide a sentiment score for each player on a scale of 1-10, where 1 is extremely negative and 10 is extremely positive. 
        Then, compare the two players and explain which one has the better outlook for fantasy football purposes and why they should be started.
        Return your response in markdown format.
        '''
    )

    name_chain = prompt_template | llm

    response = name_chain.invoke({ 'player_one_name': player_one_name, 'player_two_name': player_two_name, 'player_one_outlook': player_one_outlook, 'player_two_outlook': player_two_outlook})
    return response.content

def generate_similar_outlooks(player_one, player_df_by_pos):

    similar_players = find_similar_players(player_one, player_df_by_pos)

    player_name = player_one['name']
    player_position = player_one['position']

    similar_players_sorted = sorted(similar_players, key=lambda x: x['score'], reverse=True)

    output_string = f'''
    ### Players with Similar Outlooks to {player_name} ({player_position})
    ##### In order of similarity:

    1. **{similar_players_sorted[0]['name']}**
    - Outlook: {similar_players_sorted[0]['outlook']}

    2. **{similar_players_sorted[1]['name']}**
    - Outlook: {similar_players_sorted[1]['outlook']}

    3. **{similar_players_sorted[2]['name']}**
    - Outlook: {similar_players_sorted[2]['outlook']}
    '''

    return output_string

# Streamlit
st.title("Fantasy Football Player Comparison")

player_position = st.sidebar.selectbox('Position', positions, key="player_position", on_change=update_player_names, index=None)
player_one_name = st.sidebar.selectbox('Player 1', st.session_state.player_names, index=None)
player_two_name = st.sidebar.selectbox('Player 2', st.session_state.player_names, index=None)
if st.sidebar.button('Compare'):
    player_df_by_pos = player_df[player_df['position'] == st.session_state.player_position]

    player_one = player_df_by_pos[player_df_by_pos['name'] == player_one_name].to_dict('records')[0]
    player_two = player_df_by_pos[player_df_by_pos['name'] == player_two_name].to_dict('records')[0]

    player_comparison = generate_player_comparison(player_one, player_two)
    st.markdown(player_comparison)
elif st.sidebar.button('Similar outlooks (player 1)'):
    player_one = player_df[player_df['name'] == player_one_name].to_dict('records')[0]

    player_df_by_pos_excl_player = player_df[(player_df['position'] == st.session_state.player_position) & (player_df['name'] != player_one_name)]

    similar_players = generate_similar_outlooks(player_one, player_df_by_pos_excl_player)
    st.markdown(similar_players)





