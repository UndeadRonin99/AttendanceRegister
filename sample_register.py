import pyqrcode
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timedelta
from flask import Flask, request, send_file
import os

def create_qr_code(data, filename):
    # Create and save QR code
    qr = pyqrcode.create(data)
    qr.png(filename, scale=8)
    print(f"QR Code saved as {filename}")

# Generate a QR code containing the URL to invoke the attendance function
# This could be hosted on a server, which when accessed will call `update_attendance`
qr_data = 'https://attendanceregister-c6f3.onrender.com/record-attendance'
create_qr_code(qr_data, 'gym_attendance_qr.png')

# Initialize Firebase Admin SDK
cred = credentials.Certificate('/etc/secrets/serviceAccountKey')
firebase_admin.initialize_app(cred, {
    'databaseURL':  'https://alleysway-310a8-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)

def update_attendance():
    # Get current date and time
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    hour = now.strftime("%H")+2

    # Reference to attendance node in Firebase RTDB
    attendance_ref = db.reference(f'attendance/{date}')

    # Update attendance for the specific hour
    attendance_data = attendance_ref.get()

    if isinstance(attendance_data, list):
        # If attendance data is a list, update the specific hour
        if len(attendance_data) > int(hour):
            attendance_data[int(hour)] += 1
        else:
            attendance_data.extend([0] * (int(hour) - len(attendance_data) + 1))
            attendance_data[int(hour)] = 1
        attendance_ref.set(attendance_data)
    elif isinstance(attendance_data, dict) or attendance_data is None:
        # If attendance data is a dict or None, initialize or update accordingly
        attendance_ref.update({
            hour: attendance_data.get(hour, 0) + 1 if attendance_data else 1
        })

    print(f"Attendance recorded at: {hour}:00")
@app.route('/record-attendance', methods=['GET'])
def record_attendance():
    update_attendance()
    return "Attendance recorded successfully", 200

@app.route('/get-qr-code', methods=['GET'])
def get_qr_code():
    try:
        return send_file('gym_attendance_qr.png', mimetype='image/png')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
