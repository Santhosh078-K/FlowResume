# db_operations.py
import json
import os
import datetime
import streamlit as st # Used for st.error, st.warning, st.sidebar.info

from config import DB_FILE

def load_db_data():
    """
    Loads data from the JSON database file.
    Ensures the loaded data is a dictionary with 'users' and 'history' keys.
    """
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                # Ensure that the loaded data is a dictionary and has the expected keys
                if isinstance(data, dict) and "users" in data and "history" in data:
                    return data
                else:
                    st.error(f"Error: '{DB_FILE}' contains valid JSON but is not in the expected dictionary format. Re-initializing database.")
                    return {"users": [], "history": []}
        except json.JSONDecodeError:
            st.error(f"Error: '{DB_FILE}' is corrupted or empty. It will be re-initialized upon the next save.")
            return {"users": [], "history": []}
        except IOError as e:
            st.error(f"Error reading '{DB_FILE}': {e}. Please check file permissions and ensure the file is not locked.")
            return {"users": [], "history": []}
    # If file doesn't exist, initialize with default structure
    return {"users": [], "history": []}

def save_db_data(data):
    """
    Saves data to the JSON database file.
    Includes error handling for I/O errors.
    """
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
        # st.sidebar.success(f"Data saved to '{DB_FILE}'.") # Optional: for debugging save operations
    except IOError as e:
        st.error(f"Error writing to '{DB_FILE}': {e}. Ensure the application has write permissions to this directory.")
    except Exception as e:
        st.error(f"An unexpected error occurred while saving data: {e}")

def record_interaction(user_name, user_email, analysis_type, job_description, ai_response):
    """Records a user interaction in the database."""
    db_data = load_db_data()

    # Record user (for unique count)
    user_exists = False
    for user in db_data["users"]:
        if user.get("email") == user_email: # Use .get() for safer access
            user_exists = True
            break
    if user_email and not user_exists:
        db_data["users"].append({"name": user_name, "email": user_email})

    # Record history
    history_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "name": user_name,
        "email": user_email,
        "analysis_type": analysis_type,
        "job_description_excerpt": job_description[:200] + "..." if job_description and len(job_description) > 200 else job_description,
        "ai_response_excerpt": ai_response[:500] + "..." if ai_response and len(ai_response) > 500 else ai_response
    }
    db_data["history"].append(history_entry)
    save_db_data(db_data)
    st.sidebar.info(f"Interaction recorded: {analysis_type}") # Small feedback for dev

def clean_old_history(db_data_to_clean, days_threshold=100):
    """
    Removes history entries older than days_threshold from the database.
    Returns True if cleanup occurred, False otherwise.
    """
    current_time = datetime.datetime.now()
    cleaned_history = []
    cleanup_occurred = False

    for entry in db_data_to_clean["history"]:
        try:
            # Ensure timestamp exists and is parsable
            if "timestamp" in entry:
                dt_obj = datetime.datetime.fromisoformat(entry['timestamp'])
                time_difference = current_time - dt_obj
                if time_difference.days <= days_threshold:
                    cleaned_history.append(entry)
                else:
                    cleanup_occurred = True # This entry is old, so cleanup occurred
            else: # If timestamp is missing or malformed, keep it but log a warning (adjust as per desired strictness)
                st.sidebar.warning(f"Skipping history entry with missing/malformed timestamp, keeping it: {entry}")
                cleaned_history.append(entry)
        except ValueError:
            # Handle malformed timestamp: keep it but log a warning
            st.sidebar.warning(f"Skipping history entry with unparsable timestamp, keeping it: {entry.get('timestamp')}")
            cleaned_history.append(entry)
        except TypeError:
            # Handle non-dictionary entry in history
            st.sidebar.warning(f"Skipping malformed history entry (not a dictionary): {entry}")
            continue # Do not add malformed entry

    if cleanup_occurred:
        db_data_to_clean["history"] = cleaned_history
        save_db_data(db_data_to_clean)
        return True
    return False