# backend/call_manager.py
import os
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from config import Config
from models import update_call_status

class CallManager:
    def __init__(self):
        self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        self.from_number = Config.TWILIO_PHONE_NUMBER
    
    def make_call(self, to_number: str, message: str, call_id: int) -> dict:
        """
        Place a single outbound call with TTS message.
        Returns dict with status and details.
        """
        try:
            # Clean the message for XML
            clean_message = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Create TwiML - Properly formatted XML
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna" language="en-US">{clean_message}</Say>
    <Pause length="1"/>
    <Say voice="Polly.Joanna">Thank you for listening. Goodbye.</Say>
</Response>'''
            
            # Make the call
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                twiml=twiml,
                timeout=30,  # Ring for 30 seconds
                status_callback_event=['completed', 'busy', 'failed', 'no-answer', 'canceled']
            )
            
            # Update database with initiated status
            update_call_status(call_id, 'initiated', twilio_sid=call.sid)
            
            # Wait and check status (since webhooks don't work on localhost)
            time.sleep(5)  # Give Twilio time to process
            
            # Poll for status
            final_status = self._poll_call_status(call.sid, call_id)
            
            return {
                'success': True,
                'sid': call.sid,
                'status': final_status,
                'number': to_number
            }
            
        except TwilioRestException as e:
            error_msg = str(e.msg) if hasattr(e, 'msg') else str(e)
            update_call_status(call_id, 'failed', error_message=error_msg)
            return {
                'success': False,
                'error': error_msg,
                'number': to_number
            }
        except Exception as e:
            error_msg = str(e)
            update_call_status(call_id, 'failed', error_message=error_msg)
            return {
                'success': False,
                'error': error_msg,
                'number': to_number
            }
    
    def _poll_call_status(self, call_sid: str, call_id: int, max_attempts: int = 10) -> str:
        """Poll Twilio for call status since webhooks don't work on localhost."""
        for _ in range(max_attempts):
            try:
                call = self.client.calls(call_sid).fetch()
                
                # Map Twilio status to our status
                status_map = {
                    'queued': 'initiated',
                    'ringing': 'ringing',
                    'in-progress': 'answered',
                    'completed': 'completed',
                    'busy': 'busy',
                    'failed': 'failed',
                    'no-answer': 'no-answer',
                    'canceled': 'failed'
                }
                
                our_status = status_map.get(call.status, 'pending')
                duration = int(call.duration) if call.duration else 0
                
                # ============================================
                # 2-SECOND TIMER LOGIC
                # ============================================
                # If call completed, check duration to determine if answered
                if our_status == 'completed':
                    if duration >= 2:  # 2 SECONDS OR MORE = ANSWERED
                        our_status = 'answered'
                    elif duration > 0:
                        our_status = 'voicemail'  # Short duration = voicemail
                    else:
                        our_status = 'no-answer'
                
                # Update database
                update_call_status(call_id, our_status, duration=duration)
                
                # If call is done, stop polling
                if call.status in ['completed', 'busy', 'failed', 'no-answer', 'canceled']:
                    return our_status
                
                time.sleep(3)  # Wait 3 seconds between polls
                
            except Exception as e:
                print(f"Polling error: {e}")
                break
        
        return 'unknown'
    
    def get_call_status(self, call_sid: str) -> dict:
        """Fetch current status of a call from Twilio."""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                'sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'direction': call.direction,
                'from': call.from_,
                'to': call.to
            }
        except Exception as e:
            return {'error': str(e)}
    
    def handle_status_callback(self, call_sid: str, call_status: str, call_duration: str = None):
        """Handle webhook from Twilio when call status changes."""
        # Map Twilio status to our status
        status_map = {
            'queued': 'initiated',
            'ringing': 'ringing',
            'in-progress': 'answered',
            'completed': 'completed',
            'busy': 'busy',
            'failed': 'failed',
            'no-answer': 'no-answer',
            'canceled': 'failed'
        }
        
        our_status = status_map.get(call_status, 'pending')
        duration = int(call_duration) if call_duration else 0
        
        # ============================================
        # 2-SECOND TIMER LOGIC (Webhook version)
        # ============================================
        if our_status == 'completed':
            if duration >= 2:  # 2 SECONDS OR MORE = ANSWERED
                our_status = 'answered'
            elif duration > 0:
                our_status = 'voicemail'
            else:
                our_status = 'no-answer'
        
        return {
            'status': our_status,
            'duration': duration
        }