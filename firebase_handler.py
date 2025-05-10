import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Path to your Firebase service account key
SERVICE_ACCOUNT_KEY = 'path/to/your/serviceAccountKey.json'

# Initialize the Firebase app
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("E:\\Downloads\\coma-patient-monitoring-firebase-adminsdk-pa4ie-598c2f19de.json")

    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()


def fetch_patient_and_spectator_data(patient_id: str):
    """Fetch patient name and spectator number for a given patient ID."""
    try:
        # Fetch patient data
        patient_doc = db.collection('patients').document(patient_id).get()
        if patient_doc.exists:
            patient_name = patient_doc.to_dict().get('name', 'No Name Found')
            print(f"Patient Name: {patient_name}")
        else:
            print("No patient found with the given ID.")
            return

        # Fetch spectator(s) data using 'filter' keyword argument
        spectators_query = db.collection('spectators').where('patient_id', '==', int(patient_id)).stream()
        print(f"Debug: Spectator Query → {spectators_query}")
        spectator_numbers = []
        for doc in spectators_query:
            data = doc.to_dict()
            print(f"Debug: Spectator Document Data → {data}")  # Debugging
            number = data.get('number', 'No Number Found')
            spectator_numbers.append(number)
        
        if spectator_numbers:
            mo_number="9336674149"
            print("Spectator Numbers:")
            for num in spectator_numbers:
                print(f"- {num}")
                mo_number=num  

            return mo_number, patient_name 

        else:
            print("No spectators found for the given patient ID.")

    except Exception as e:
        print(f"Error fetching data:1 {e}")
  


def get_next_id(counter_doc_ref):
    """Retrieve and increment the counter document for sequential IDs."""
    counter_doc = counter_doc_ref.get()
    if counter_doc.exists:
        current_id = counter_doc.to_dict().get('last_id', 0)
    else:
        current_id = 0  # Initialize if counter document doesn't exist

    new_id = current_id + 1
    counter_doc_ref.set({'last_id': new_id})  # Update the counter
    return new_id

def store_name_and_time(id: int,name: str):
    """Function to store name and current time in Firestore"""
    # Firestore collection name
    collection_name = 'patient_data'
    counter_doc_ref = db.collection('counters').document('user_data_counter')

    # Get the next sequential ID
    doc_id = str(get_next_id(counter_doc_ref))  

    # Data to store
    data = {
        'id':id,
        'name': name,
        'time': datetime.now()  # Current time in ISO format
    }

    # Add data to Firestore
    db.collection(collection_name).document(doc_id).set(data)
    print(f"Data successfully written with document ID: {doc_id}")





if __name__ == "__main__":
    # fetch_patient_and_spectator_data("1")
    store_name_and_time(1,"sri")
