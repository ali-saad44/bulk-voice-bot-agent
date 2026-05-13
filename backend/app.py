# backend/app.py
import os
import sys
import time
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, validate_config
from models import (
    init_db, create_campaign, add_call, update_call_status,
    get_campaign_stats, get_campaign_calls, update_campaign_status,
    get_all_campaigns, get_db_connection
)
from file_parser import extract_numbers_from_file, create_result_file
from call_manager import CallManager

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database on startup
init_db()

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files."""
    return send_from_directory('../frontend', path)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and parse phone numbers file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use: Excel, CSV, TXT, or PDF'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract numbers
        numbers = extract_numbers_from_file(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'total_numbers': len(numbers),
            'numbers': numbers[:10],  # Show first 10 preview
            'filepath': filepath
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/create', methods=['POST'])
def create_new_campaign():
    """Create a new campaign."""
    data = request.get_json()
    
    name = data.get('name', 'Untitled Campaign')
    message = data.get('message', '')
    filepath = data.get('filepath', '')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    if not filepath:
        return jsonify({'error': 'File path is required'}), 400
    
    try:
        # Extract all numbers
        numbers = extract_numbers_from_file(filepath)
        
        if len(numbers) == 0:
            return jsonify({'error': 'No valid phone numbers found in file'}), 400
        
        # Create campaign in database
        campaign_id = create_campaign(name, message)
        
        # Add all numbers to calls table
        for number in numbers:
            add_call(campaign_id, number)
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'total_numbers': len(numbers),
            'message': 'Campaign created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/campaign/<int:campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start calling numbers one by one."""
    def call_numbers():
        call_manager = CallManager()
        calls = get_campaign_calls(campaign_id)
        
        # Get campaign message
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT message FROM campaigns WHERE id = ?', (campaign_id,))
        message = cursor.fetchone()['message']
        conn.close()
        
        update_campaign_status(campaign_id, 'running')
        
        for call in calls:
            if call['status'] != 'pending':
                continue
            
            # Make the call and wait for it to complete
            result = call_manager.make_call(
                call['phone_number'],
                message,
                call['id']
            )
            
            # Wait before next call (rate limiting)
            time.sleep(Config.CALL_DELAY_SECONDS)
        
        update_campaign_status(campaign_id, 'completed')
        
        # Generate result file
        final_calls = get_campaign_calls(campaign_id)
        filepath = os.path.join(Config.UPLOAD_FOLDER, f"campaign_{campaign_id}.xlsx")
        result_path = create_result_file(filepath, campaign_id, final_calls, Config.CAMPAIGNS_FOLDER)
        print(f"Results saved to: {result_path}")
    
    # Run in background thread
    thread = threading.Thread(target=call_numbers)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Campaign started',
        'campaign_id': campaign_id
    })

@app.route('/api/campaign/<int:campaign_id>/status', methods=['GET'])
def campaign_status(campaign_id):
    """Get real-time campaign status."""
    stats = get_campaign_stats(campaign_id)
    calls = get_campaign_calls(campaign_id)
    
    return jsonify({
        'campaign_id': campaign_id,
        'stats': stats,
        'calls': calls,
        'progress': {
            'total': stats['total'],
            'completed': stats['total'] - stats['pending'],
            'percentage': round(((stats['total'] - stats['pending']) / stats['total'] * 100), 1) if stats['total'] > 0 else 0
        }
    })

@app.route('/api/campaign/<int:campaign_id>/results', methods=['GET'])
def get_results(campaign_id):
    """Get final results with file download link."""
    calls = get_campaign_calls(campaign_id)
    stats = get_campaign_stats(campaign_id)
    
    # Find the result file
    result_files = [f for f in os.listdir(Config.CAMPAIGNS_FOLDER) if f.startswith(f"campaign_{campaign_id}") or f.endswith('_results_')]
    
    return jsonify({
        'campaign_id': campaign_id,
        'stats': stats,
        'calls': calls,
        'result_files': result_files
    })

@app.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    """List all campaigns."""
    campaigns = get_all_campaigns()
    return jsonify({'campaigns': campaigns})

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download result file."""
    return send_from_directory(Config.CAMPAIGNS_FOLDER, filename, as_attachment=True)

@app.route('/webhook/call-status', methods=['POST'])
def call_status_webhook():
    """Receive Twilio call status webhooks."""
    data = request.form
    
    call_sid = data.get('CallSid')
    call_status = data.get('CallStatus')
    call_duration = data.get('CallDuration', '0')
    
    # Find call by SID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM calls WHERE twilio_sid = ?', (call_sid,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        call_manager = CallManager()
        result = call_manager.handle_status_callback(call_sid, call_status, call_duration)
        update_call_status(row['id'], result['status'], duration=result['duration'])
    
    return '', 200

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    try:
        validate_config()
        print("=" * 50)
        print("VOICEBOT SERVER STARTING...")
        print("=" * 50)
        print(f"Upload folder: {Config.UPLOAD_FOLDER}")
        print(f"Campaigns folder: {Config.CAMPAIGNS_FOLDER}")
        print(f"Database: {Config.DATABASE_PATH}")
        print("=" * 50)
        print("Open browser: http://localhost:5000")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ValueError as e:
        print(f"\nCONFIG ERROR: {e}")
        print("\nPlease check your .env file and add your Twilio credentials.")
        sys.exit(1)