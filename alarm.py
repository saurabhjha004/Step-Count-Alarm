import streamlit as st
import time
import os
import getpass  # Library to hide password input
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import pygame

# Setting up Google Fit API credentials
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read', 'offline_access']

def authenticate_with_google():
    flow = InstalledAppFlow.from_client_secrets_file(
        'web.json',
        scopes=SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return credentials

def authenticate_with_email():
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        st.write(f"Email: {email}")
        st.write(f"Password: {password}")
        return True

def fetch_step_count(credentials):
    fit_service = build('fitness', 'v1', credentials=credentials)
    now = datetime.datetime.now()
    start_time = (now - datetime.timedelta(days=1)).isoformat() + 'Z'
    end_time = now.isoformat() + 'Z'
    data = fit_service.users().dataset().aggregate(userId='me', body={
        "aggregateBy": [{
            "dataTypeName": "com.google.step_count.delta",
            "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
        }],
        "bucketByTime": { "durationMillis": 86400000 },
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }).execute()
    step_count = data['bucket'][0]['dataset'][0]['point'][0]['value'][0]['intVal']
    return step_count

def play_alarm(audio_file):
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    pygame.quit()

def turn_off_alarm():
    pass

def run_alarm_system(threshold, audio_file, credentials):
    while True:
        current_step_count = fetch_step_count(credentials)
        if current_step_count >= threshold:
            st.success("Alarm deactivated. You've walked 100 steps!")
            play_alarm(audio_file)  # Play alarm sound
            turn_off_alarm()  # Turn off the alarm
            break
        st.write(f"Current step count: {current_step_count}")
        time.sleep(10)  # Check step count every 10 seconds

def main():
    st.title("Real-time Step Count Alarm")

    login_option = st.radio("Login Options", ["Continue with Google", "Login with Email"])

    if login_option == "Continue with Google":
        st.markdown("Click the button below to continue with Google login")
        if st.button("Continue with Google"):
            credentials = authenticate_with_google()
            st.write("Authentication successful.")
            # Proceed with alarm setup and activation
            setup_and_run_alarm(credentials)
    else:
        if authenticate_with_email():
            # Proceed with alarm setup and activation
            setup_and_run_alarm(None)

def setup_and_run_alarm(credentials):
    st.sidebar.header("Set Threshold")
    threshold = st.sidebar.number_input("Enter Step Threshold", min_value=1, value=100, step=1)

    audio_file_path = os.path.expanduser("~/Desktop/audio.mp3")

    if st.button("Activate Alarm"):
        run_alarm_system(threshold, audio_file_path, credentials)

if __name__ == "__main__":
    main()
