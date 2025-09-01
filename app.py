import streamlit as st
from utils import word_handling as wh

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Skribbl Word Collector",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- DATABASE INITIALIZATION ---
# The init_db() line is now removed, as MongoDB creates collections automatically.

# --- HEADER ---
st.title("🎨 Skribbl.io Word Collector")
st.caption("A simple tool to collaboratively create custom word lists for games like Skribbl.io.")

# --- CREATE NEW COLLECTION ---
st.header("Create a New Collection")
with st.form(key="create_collection_form", clear_on_submit=True):
    new_collection_input = st.text_input(
        "Enter new collection name",
        placeholder="e.g., Video Games, Science, Disney Movies",
    )
    col1, col2 = st.columns([2, 3])
    submitted = col1.form_submit_button("Create Collection")
    # --- The Confirmation Checkbox ---
    # Add this checkbox to the form. It must be checked to proceed.
    confirmed = col2.checkbox("I'm sure I want to create this new collection.")

    if submitted and new_collection_input and confirmed:
        if wh.create_collection(new_collection_input):
            st.success(f"Collection '{new_collection_input}' was created successfully!")
        else:
            st.error(f"Collection '{new_collection_input}' already exists or is an invalid name.")

st.divider()

# --- EXISTING COLLECTIONS ---
st.header("Existing Collections")
collections = wh.get_all_collections()

if not collections:
    st.info("No collections found. Create one above to get started!")
else:
    for collection_name in collections:
        word_count = wh.get_word_count(collection_name)

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.subheader(f"{collection_name.replace('-', ' ').title()}")
            col2.metric(label="Words", value=word_count)

            # Add word form for each collection
            with st.form(key=f"add_word_form_{collection_name}", clear_on_submit=True):
                word_col, btn_col = st.columns([3, 1])
                new_word_input = word_col.text_input(
                    "Add a new word",
                    placeholder="Type a word and press 'Add'",
                    label_visibility="collapsed",
                    key=f"new_word_input_{collection_name}"
                )
                add_word_submitted = btn_col.form_submit_button("Add Word")

                if add_word_submitted and new_word_input:
                    message = wh.add_word(collection_name, new_word_input)
                    if "Success" in message:
                        st.rerun() # Rerun the app to update the word count
                    else:
                        st.toast(message, icon="⚠️")
                        # pass
                        
# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("👑 Admin Zone")
    
    admin_collections = wh.get_all_collections()
    if not admin_collections:
        st.info("No collections to manage.")
    else:
        selected_collection = st.selectbox("Select a collection to manage:", admin_collections)
        password = st.text_input("Enter admin password:", type="password")

        # --- View Words ---
        if st.button("View Words as List"):
            if selected_collection and password:
                word_list = wh.view_words(selected_collection, password)
                if "Error" in word_list:
                    st.error(word_list)
                else:
                    st.text_area("Copy words from here:", word_list, height=200)
            else:
                st.warning("Please select a collection and enter the password.")
        
        # --- Delete Collection ---
        st.subheader("Delete Collection")
        if st.checkbox(f"Confirm deletion of '{selected_collection}'"):
            if st.button("Delete Collection Permanently", type="primary"):
                if selected_collection and password == wh.ADMIN_PASSWORD:
                    wh.delete_collection(selected_collection)
                    st.success(f"Deleted '{selected_collection}'.")
                    st.rerun()
                elif password != wh.ADMIN_PASSWORD:
                    st.error("Incorrect password.")



st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    col2.markdown("""<div style="font-size:1.5rem; text-align: center;">Made for Fun</div>""", unsafe_allow_html=True)
    col2.markdown("""<div style="font-size:2rem; text-align: center;">By Jatin Yadav</div>""", unsafe_allow_html=True)
