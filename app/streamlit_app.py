# streamlitapp.py
import os
import streamlit as st
from app.spotify_api import get_spotify_client, get_spotify_auth_url, get_top_tracks, CACHE_FILE
from app.plotting import create_songs_df, recently_played_songs
import pandas as pd

def run_app():
    st.write("My Spotify Wrapped Clone")
    
    if st.button("Sign in with Spotify"):
        st.session_state.clear()
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        st.write("Click the link below to sign in to your Spotify Account:")
        auth_url = get_spotify_auth_url()
        st.markdown(f"[Authorize Spotify]({auth_url})", unsafe_allow_html=True)
    else:
        query_params = st.query_params
        spotify_client = get_spotify_client(auth_response=query_params)
        
        if isinstance(spotify_client, dict) and "auth_url" in spotify_client:
            st.write("Please click the button above to sign in with Spotify.")
        else:
            st.write("Fetching your Spotify data...")
            try:
                user_info = spotify_client.current_user()
                user_name = user_info['display_name']
                profile_image_url = user_info['images'][0]['url'] if user_info['images'] else None
                if profile_image_url:
                    if profile_image_url:
                        # --- Uses custom CSS to make the image round and smaller ---
                        st.markdown(
                            f"""
                            <style>
                            .profile-image {{
                                width: 100px;  # Adjust the size as needed
                                height: 100px; # Adjust the size as needed
                                border-radius: 50%;  # Make the image round
                                object-fit: cover;  # Ensure the image fits properly
                            }}
                            </style>
                            """,
                            unsafe_allow_html=True
                        )
                        st.image(profile_image_url, width=100, caption="Profile Picture")
                else:
                    st.write("No profile picture available.")

                st.subheader(f"Welcome to your Wrap, {user_name} 🎉")

                st.markdown("<br><br>", unsafe_allow_html=True)

                top_tracks = get_top_tracks(spotify_client)
                if top_tracks and top_tracks.get("items"):
                    st.write("### Most Listened Tracks Over the Past Year:")
                    for idx, track in enumerate(top_tracks["items"]):
                        track_name = track.get("name", "Unknown")
                        artists = ", ".join([artist.get("name", "Unknown") for artist in track.get("artists", [])])
                        st.write(f"{idx + 1}. **{track_name}** by {artists}")
                else:
                    st.write("No top tracks found or unable to fetch data.")

                st.markdown("<br><br>", unsafe_allow_html=True)
                    
                # --- Recently Played Songs Feature ---
                recently_played = spotify_client.current_user_recently_played(limit=10)
                if recently_played and recently_played.get("items"):
                    st.write("### Your Recently Played Songs:")
                    # Process the recently played data using our helper function.
                    rp_df = recently_played_songs(recently_played)
                    # Display as a table or custom list.
                    st.table(rp_df)
                else:
                    st.write("No recently played songs found.")
                    
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.header("Your Top Tracks and Their Popularity Worldwide")
                track_df = create_songs_df(top_tracks)
                st.bar_chart(track_df.set_index('name')['popularity'])
            except Exception as e:
                st.error(f"An error occurred: {e}")
