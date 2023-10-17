# Importing required libraries
from venv import create
import streamlit as st
# st.session_state["twelve_labs_key"] = ""
# st.session_state["index_id"] = ""
# st.session_state["index_name"] = ""
# st.session_state["url"] = ""

if "video_id" not in st.session_state:
    st.session_state["video_id"] = ""
if "index_id" not in st.session_state:
    st.session_state["index_id"] = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
import requests


def list_video_indexing_tasks(twelve_labs_key):
    url = "https://api.twelvelabs.io/v1.2/tasks?page=1&page_limit=10&sort_by=created_at&sort_option=desc"

    headers = {
        "accept": "application/json",
        "x-api-key": twelve_labs_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    st.write(response.json().get("data"))

def get_indexes(twelve_labs_key):
    url = "https://api.twelvelabs.io/v1.2/indexes?page=1&page_limit=10&sort_by=created_at&sort_option=desc"
    headers = {
        "accept": "application/json",
        "x-api-key": twelve_labs_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    return response.json()

def get_videos(index_id, twelve_labs_key):
    url = f"https://api.twelvelabs.io/v1.2/indexes/{index_id}/videos?page=1&page_limit=10&sort_by=created_at&sort_option=desc"

    headers = {
        "accept": "application/json",
        "x-api-key": twelve_labs_key,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def index_video(video_url,twelve_labs_key):
    url = "https://api.twelvelabs.io/v1.2/tasks/external-provider"
    payload = {
        "index_id": st.session_state["index_id"],
        "url": video_url
    }
    headers = {
        "accept": "application/json",
        "x-api-key": twelve_labs_key,
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print("created video")
    return response.json()

def create_index(index_name, twelve_labs_key):
    url = "https://api.twelvelabs.io/v1.2/indexes"

    payload = {
        "index_name": index_name,
        "engines": [
            {
            "engine_name": "marengo2.5",
            "engine_options": ["visual", "conversation", "text_in_video", "logo"]
            },
            {
            "engine_name": "pegasus1",
            "engine_options": ["visual", "conversation"]
            }
        ],
    }
    headers = {
        "accept": "application/json",
        "x-api-key": twelve_labs_key,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    return response.json()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Sidebar section
st.sidebar.title("AskMedio")
twelve_labs_key = st.sidebar.text_input("Enter Twelve Labs Key:", type="password")

if twelve_labs_key:
    indexes = get_indexes(twelve_labs_key).get("data")
    index_ids = []
    for index in indexes:
        index_ids.append(index['_id'])
    print(index)
    if len(index_ids) > 0:
        print(index_ids)
        option = st.sidebar.selectbox(
        "Select an index:",
        index_ids,
        placeholder="Select index method...",
        )
        st.session_state["index_id"] = option


    if st.session_state["index_id"] == "":
        index_name = st.sidebar.text_input("Index name:")
        index_id = create_index(index_name,twelve_labs_key).get("_id")
        st.sidebar.write("added new id")
        st.sidebar.write(index_id)
        st.session_state["index_id"] = index_id
        print("here----------------------------------")
        video_url = st.sidebar.text_input("Enter the URL to index:")
        if video_url:
            video_index = index_video(video_url,twelve_labs_key).get("_id")
            # print(video_index)
            # st.session_state["video_id"] = video_index[7:-2]
            # st.sidebar.write(st.session_state["video_id"])

            video_index = index_video(video_url,twelve_labs_key)
            print(video_index)
            st.session_state["video_id"] = video_index
            st.sidebar.write(st.session_state["video_id"]) 
    
    add_new_video = st.sidebar.checkbox('Add new video')

    if add_new_video:
        video_url = st.sidebar.text_input("Enter the URL to index:")
        if video_url:
            video_index = index_video(video_url,twelve_labs_key).get("_id")
    
    result = get_videos(st.session_state["index_id"],twelve_labs_key)
    data = result['data']
    if data:
        v_id = []
        for d in data:
            v_id.append(d["metadata"]["filename"]+"-"+d["_id"])
        option = st.sidebar.selectbox(
                    "Select an video:",
                    v_id,
                    placeholder="Select video...",
                    )
        st.session_state["video_id"] = option.split("-")[-1]
        st.sidebar.write("id : " + st.session_state["video_id"])


    prompt = st.chat_input("Say something")

    new_index = st.sidebar.checkbox('Create a new index')
    if new_index:
        video_url = st.sidebar.text_input("Enter the URL to index:")
        if video_url:
            video_index = index_video(video_url,twelve_labs_key).get("_id")
        index_name = st.sidebar.text_input("Index name:")
        if index_name:
            index_id = create_index(index_name,twelve_labs_key).get("_id")
            st.sidebar.write("Added new index id")
            st.sidebar.write(index_id)
            st.session_state["index_id"] = index_id
        
            # print(video_index)
            # st.session_state["video_id"] = video_index[7:-2]
            # st.sidebar.write(st.session_state["video_id"])
            st.sidebar.video(video_url)
            video_index = index_video(video_url,twelve_labs_key)
            st.sidebar.write(video_index)
            # st.session_state["video_id"] = video_index
            # st.sidebar.write(st.session_state["video_id"]) 

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            
            url = "https://api.twelvelabs.io/v1.2/generate"

            payload = {
                "video_id": st.session_state["video_id"],
                "prompt": prompt
            }
            headers = {
                "accept": "application/json",
                "x-api-key": twelve_labs_key,
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)
            st.markdown(response.json().get("data"))
        st.session_state.messages.append(
            {"role": "assistant", "content": response.json().get("data")}
        )
indexing_status = st.sidebar.checkbox('video indexing status')
if indexing_status:
    list_video_indexing_tasks(twelve_labs_key)

if st.sidebar.button("Clear Chats", type="primary"):
    st.session_state.messages = []
    st.session_state["video_id"] = ""
    st.session_state["index_id"] = ""