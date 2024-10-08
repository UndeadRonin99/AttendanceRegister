import pyqrcode
import firebase_admin
import os
from firebase_admin import credentials
from datetime import datetime
from flask import Flask, request

def create_qr_code(data, filename):
    # Create and save QR code
    qr = pyqrcode.create(data)
    qr.png(filename, scale=8)
    print(f"QR Code saved as {filename}")
# Generate a QR code containing the URL to invoke the attendance function
# This could be hosted on a server, which when accessed will call `update_attendance`
qr_data = f'http://{server_ip}:5000/record-attendance'
create_qr_code(qr_data, 'sampleAttendance.png')

# Initialize Firebase Admin SDK
cred = credentials.Certificate('/etc/secrets/serviceAccountKey')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://alleysway-310a8-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)



def update_attendance():
    # Get current date and time
    now = datetime.now()
    day_of_week = now.strftime("%A")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # Reference to attendance node in Firebase RTDB
    attendance_ref = db.reference('attendance')
    new_attendance = attendance_ref.push({
        'day_of_week': day_of_week,
        'timestamp': timestamp
    })
    print(f"Attendance recorded at: {timestamp}")

@app.route('/record-attendance', methods=['GET'])
def record_attendance():
    update_attendance()
    return "Attendance recorded successfully", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
