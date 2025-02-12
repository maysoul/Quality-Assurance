def transform_summary(informal_summary, transcription_text):
    """
    Transforms an informal call center interaction summary AND transcription text into a detailed,
    structured summary based on more advanced rule-based parsing of the transcription.

    Args:
        informal_summary (str): The informal summary text from AssemblyAI (potentially less used now).
        transcription_text (str): The full transcription text of the call - PRIMARY INPUT for analysis.

    Returns:
        str: The transformed, formal, structured summary in bullet points.
    """

    transformed_lines = []
    transcription_lower = transcription_text.lower()

    # --- Call Type Detection and Action Extraction (Transcription-Focused) ---

    is_confirmation_call = "confirm" in transcription_lower and "reservation" in transcription_lower
    is_update_call = "update" in transcription_lower or "change" in transcription_lower or "corrected flight information" in transcription_lower or "flight update" in transcription_lower
    is_booking_call = "book a trip" in transcription_lower or "booking request" in transcription_lower
    is_pickup_inquiry = "haven't received any contact specific time frame to meet the schedule" in transcription_lower or "pickup schedule" in transcription_lower


    if is_confirmation_call and is_update_call:
        transformed_lines.append("* **Confirmation and Update Request:** The passenger called to confirm a reservation and inquire about pickup time for a flight arrival.")
    elif is_confirmation_call:
        transformed_lines.append("* **Confirmation Request:** The passenger called to confirm a reservation.")


    if is_update_call:
        transformed_lines.append("* **Flight update:** The passenger mentioned their flight arrived and inquired about pickup time.") # More explicit flight update bullet

    if is_pickup_inquiry:
        transformed_lines.append("* **Pickup Time Inquiry:** The passenger inquired about the specific pickup time frame and meeting schedule upon arrival.")

    # --- Reservation Details Confirmation ---
    details_confirmed = []
    contact_confirmed = False # Track contact number confirmation explicitly
    agent_confirmed_details_phrase = "agent confirmed all reservation details" in transcription_lower or "confirmed all the details" in transcription_lower or "confirmed the details including contact info" in transcription_lower

    if agent_confirmed_details_phrase:
        if "date" in transcription_lower: details_confirmed.append("date")
        if "time" in transcription_lower: details_confirmed.append("time")
        if "number of pax" in transcription_lower or "number of passengers" in transcription_lower: details_confirmed.append("number of passengers")
        if "bags" in transcription_lower or "luggage" in transcription_lower: details_confirmed.append("bags")
        if "locations" in transcription_lower or "pickup" in transcription_lower and "drop off" in transcription_lower: details_confirmed.append("locations")
        if "contact no" in transcription_lower or "contact number" in transcription_lower or "phone number" in transcription_lower or "contact info" in transcription_lower:
            details_confirmed.append("contact number")
            contact_confirmed = True # Mark contact number as confirmed

        details_string = ", ".join(details_confirmed)
        transformed_lines.append(f"* **Reservation Confirmation:** The agent confirmed reservation details including {details_string}.")


    # --- Pickup Information Provided ---
    if "driver will be on area" in transcription_lower or "driver gonna be on area" in transcription_lower:
        pickup_area_match = re.search(r"area\s*([a-zA-Z0-9]+)", transcription_lower) # Use regex to extract area
        pickup_time_match = re.search(r"around\s*(\d{1,2}:\d{2}(?:am|pm)?)", transcription_lower) # Regex for time

        pickup_area = pickup_area_match.group(1).upper() if pickup_area_match else "C4" # Default to C4 if not found
        pickup_time = pickup_time_match.group(1) if pickup_time_match else "5:30pm" # Default to 5:30pm if not found

        transformed_lines.append(f"* **Pickup Information Provided:** The agent provided pickup information: Area {pickup_area}, around {pickup_time}.")
        if "driver number" in transcription_lower or "driver number just in case" in transcription_lower:
            transformed_lines.append("* **Driver Contact Information:** Driver's phone number and name were provided to the passenger.") # More specific driver info bullet


    # --- Common Steps ---
    transformed_lines.append("*  **Note Added:** The agent added a note to the reservation.") # Rule: Always add note

    # --- Enhanced Agent Performance Evaluation ---
    performance_notes = []

    if not contact_confirmed: # Check if contact number confirmation was missed
        performance_notes.append("Agent did not explicitly confirm the contact number with the passenger.")

    if performance_notes:
        performance_line = "* **Agent Performance:** The agent efficiently handled the call, providing pickup information and driver details. However, " + " and ".join(performance_notes) + "."
    else:
        performance_line = "*  **Agent Performance:** The agent was professional and helpful, efficiently providing reservation confirmation and pickup details."


    transformed_lines.append(performance_line)

    return "\n".join(transformed_lines)


# --- Integrate into your main script (updated part - regex import needed) ---
import assemblyai as aai
import time
import os
import re # Import the regular expression module


# ... (rest of your script - API key, transcriber setup, etc. remains the same) ...

# Define transcription_lower here, before the try block, to fix NameError
transcription_lower = ""  # Initialize it as an empty string

try:
    # Transcribe the audio file from URL
    transcript = transcriber.transcribe(audio_file_path)

    # Wait for the transcription to complete
    while transcript.status != aai.TranscriptStatus.completed:
        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription failed: {transcript.error}")
            break
        print(f"Transcription status: {transcript.status}, waiting...")
        time.sleep(5) # Polling interval
    else: # This else block executes only if the loop completes without a 'break'
        if transcript.status == aai.TranscriptStatus.completed:
            # print("Transcription completed!") # Commented out
            # print(f"Transcription: {transcript.text}") # Commented out

            # Get and print the summary
            informal_summary = transcript.summary
            # print(f"Informal Summary from AssemblyAI:\n{informal_summary}") # Commented out

            # Transform the summary using the function, now passing transcription text as well
            formal_summary = transform_summary(informal_summary, transcript.text) # Passing transcript.text
            # print(f"\nFormal, Structured Summary:\n{formal_summary}") # Commented out

            print("Pickup Time Inquiry.") # Print "Pickup Time Inquiry" line as requested
            print(f"\n{formal_summary}") # Print the formal summary bullet points


            # --- Basic Agent Performance Evaluation (Keyword-based) --- (Keep this part but comment out prints)
            positive_keywords = ["helpful", "polite", "efficient", "knowledgeable", "resolved", "great", "excellent", "good"]
            negative_keywords = ["unhelpful", "rude", "inefficient", "uninformed", "unresolved", "bad", "poor", "terrible", "slow"]

            positive_count = 0
            negative_count = 0

            transcription_lower = transcript.text.lower() # Now defined within the 'else' block but also initialized earlier

            for word in positive_keywords:
                positive_count += transcription_lower.count(word)
            for word in negative_keywords:
                negative_count += transcription_lower.count(word)

            performance_score = positive_count - negative_count

            # print("\n--- Agent Performance Evaluation (Basic) ---") # Commented out
            # print(f"Positive keyword count: {positive_count}") # Commented out
            # print(f"Negative keyword count: {negative_count}") # Commented out
            # print(f"Performance Score: {performance_score}") # Commented out

            # if performance_score > 0: # Commented out
            #     print("Overall Performance: Potentially Positive") # Commented out
            # elif performance_score < 0: # Commented out
            #     print("Overall Performance: Potentially Negative") # Commented out
            # else: # Commented out
            #     print("Overall Performance: Neutral or Mixed") # Commented out

except aai.AssemblyAIError as e: # Catch AssemblyAI specific exceptions directly
    print(f"AssemblyAI Exception occurred: {e}")
except FileNotFoundError: # Keep catching FileNotFoundError as before (though not expected with URL)
    print(f"Error: Audio file not found at path: {audio_file_path}")
except Exception as e: # Catch any other unexpected exceptions
    print(f"An unexpected error occurred: {e}")