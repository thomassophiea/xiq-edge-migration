#!/usr/bin/env python3
"""
Web UI for XIQ to Edge Services Migration Tool
Provides a user-friendly web interface for the migration workflow
"""

import os
import sys
import json
import threading
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from xiq_api_client import XIQAPIClient
from campus_controller_client import CampusControllerClient
from config_converter import ConfigConverter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app)

# XIQ Region URLs for authentication
REGION_URLS = {
    'Global': 'https://api.extremecloudiq.com',
    'EU': 'https://api-eu.extremecloudiq.com',
    'APAC': 'https://api-apac.extremecloudiq.com',
    'California': 'https://api-ca.extremecloudiq.com'
}

# Store migration state
migration_state = {
    'status': 'idle',  # idle, running, completed, error
    'progress': 0,
    'current_step': '',
    'logs': [],
    'results': {},
    'xiq_data': {},
    'converted_config': {},
    'profiles': []
}


def log_message(message, level='info'):
    """Add a log message to the migration state"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    migration_state['logs'].append({
        'timestamp': timestamp,
        'level': level,
        'message': message
    })


def update_progress(step, progress):
    """Update migration progress"""
    migration_state['current_step'] = step
    migration_state['progress'] = progress


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - authenticate with XIQ credentials"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        region = request.form.get('region', 'Global')

        # Validate credentials by attempting XIQ authentication
        try:
            base_url = REGION_URLS.get(region, REGION_URLS['Global'])
            xiq_client = XIQAPIClient.login(
                username=username,
                password=password,
                base_url=base_url,
                verbose=False
            )

            if xiq_client:
                # Successful authentication
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Invalid XIQ credentials')

        except Exception as e:
            return render_template('login.html', error=f'Authentication failed: {str(e)}')

    # If already logged in, redirect to main page
    if session.get('logged_in'):
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/connect_xiq', methods=['POST'])
@login_required
def connect_xiq():
    """Connect to XIQ and retrieve configuration"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        region = data.get('region', 'Global')

        # Map region to base URL
        region_urls = {
            'Global': 'https://api.extremecloudiq.com',
            'EU': 'https://api-eu.extremecloudiq.com',
            'APAC': 'https://api-apac.extremecloudiq.com',
            'California': 'https://api-ca.extremecloudiq.com'
        }
        base_url = region_urls.get(region, 'https://api.extremecloudiq.com')

        log_message(f'Connecting to XIQ ({region})...')
        update_progress('Connecting to XIQ', 10)

        # Initialize XIQ client using login classmethod
        xiq_client = XIQAPIClient.login(
            username=username,
            password=password,
            base_url=base_url,
            verbose=False
        )

        if not xiq_client:
            log_message('Failed to authenticate with XIQ', 'error')
            return jsonify({'success': False, 'error': 'Authentication failed'}), 401

        log_message('Successfully authenticated with XIQ')
        update_progress('Retrieving XIQ configuration', 30)

        # Get complete configuration
        log_message('Fetching configuration from XIQ...')
        xiq_config = xiq_client.get_configuration()

        log_message('Fetching device information...')
        devices = xiq_client.get_devices()
        xiq_config['devices'] = devices

        # Extract data from configuration
        ssids = xiq_config.get('ssids', [])
        vlans = xiq_config.get('vlans', [])
        radius_servers = xiq_config.get('authentication', [])

        # Store in session
        migration_state['xiq_data'] = xiq_config

        log_message(f'Retrieved {len(ssids)} SSIDs, {len(vlans)} VLANs, {len(radius_servers)} RADIUS servers, {len(devices)} devices')
        update_progress('XIQ data retrieved', 50)

        return jsonify({
            'success': True,
            'data': {
                'ssids': [{'id': s.get('id'), 'name': s.get('name', s.get('ssid_name'))} for s in ssids],
                'vlans': [{'id': v.get('id'), 'name': v.get('name'), 'vlan_id': v.get('vlan_id')} for v in vlans],
                'radius_servers': [{'id': r.get('id'), 'name': r.get('name'), 'ip': r.get('ip')} for r in radius_servers],
                'devices': [{'serial': d.get('serial_number'), 'name': d.get('hostname'), 'location': d.get('location')} for d in devices]
            }
        })

    except Exception as e:
        log_message(f'Error connecting to XIQ: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/connect_edge', methods=['POST'])
@login_required
def connect_edge():
    """Connect to Edge Services and retrieve profiles"""
    try:
        data = request.json
        controller_url = data.get('controller_url')
        username = data.get('username')
        password = data.get('password')

        log_message(f'Connecting to Edge Services at {controller_url}...')

        # Initialize Edge Services client (authenticates automatically in __init__)
        controller_client = CampusControllerClient(
            base_url=controller_url,
            username=username,
            password=password,
            verbose=False
        )

        # If we get here, authentication succeeded (otherwise exception was thrown)
        log_message('Successfully authenticated with Edge Services')

        # Get profiles
        log_message('Fetching Associated Profiles...')
        profiles = controller_client.get_profiles()

        # Sort profiles (custom first, then defaults)
        custom_profiles = [p for p in profiles if '/default' not in p.get('name', '').lower()]
        default_profiles = [p for p in profiles if '/default' in p.get('name', '').lower()]
        custom_profiles.sort(key=lambda p: p.get('name', ''))
        default_profiles.sort(key=lambda p: p.get('name', ''))
        sorted_profiles = custom_profiles + default_profiles

        migration_state['profiles'] = sorted_profiles

        log_message(f'Retrieved {len(sorted_profiles)} Associated Profiles')

        return jsonify({
            'success': True,
            'data': {
                'profiles': [
                    {
                        'id': p.get('id'),
                        'name': p.get('name'),
                        'platform': p.get('apPlatform'),
                        'is_custom': '/default' not in p.get('name', '').lower()
                    }
                    for p in sorted_profiles
                ]
            }
        })

    except Exception as e:
        log_message(f'Error connecting to Edge Services: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/convert', methods=['POST'])
@login_required
def convert_config():
    """Convert XIQ configuration to Edge Services format"""
    try:
        data = request.json
        selected_ssids = data.get('selected_ssids', [])
        selected_vlans = data.get('selected_vlans', [])
        selected_radius = data.get('selected_radius', [])

        log_message('Converting configuration...')
        update_progress('Converting configuration', 60)

        xiq_data = migration_state['xiq_data']

        # DEBUG: Log what we received
        print(f'DEBUG: Received selected_ssids: {selected_ssids}')
        print(f'DEBUG: Total SSIDs in xiq_data: {len(xiq_data["ssids"])}')

        # Filter selected objects
        ssids = [s for s in xiq_data['ssids'] if s.get('id') in selected_ssids]
        vlans = [v for v in xiq_data['vlans'] if v.get('id') in selected_vlans]
        radius = [r for r in xiq_data.get('authentication', []) if r.get('id') in selected_radius]

        # DEBUG: Log filtered results
        print(f'DEBUG: Filtered to {len(ssids)} SSIDs')
        print(f'DEBUG: SSID names: {[s.get("name", s.get("ssid_name")) for s in ssids]}')

        # Build filtered xiq_config structure
        filtered_config = {
            'ssids': ssids,
            'vlans': vlans,
            'authentication': radius,
            'devices': xiq_data.get('devices', []),
            'rate_limiters': xiq_data.get('rate_limiters', []),
            'cos_policies': xiq_data.get('cos_policies', []),
            'user_profiles': xiq_data.get('user_profiles', [])
        }

        # Convert configuration
        converter = ConfigConverter()
        campus_config = converter.convert(filtered_config)

        # DEBUG: Log conversion results
        print(f'DEBUG: Conversion created {len(campus_config.get("services", []))} services')
        print(f'DEBUG: Service names: {[s.get("serviceName") for s in campus_config.get("services", [])]}')

        migration_state['converted_config'] = campus_config

        # Build summary
        summary = {
            'rate_limiters': len(campus_config.get('rate_limiters', [])),
            'cos_policies': len(campus_config.get('cos_policies', [])),
            'topologies': len(campus_config.get('topologies', [])),
            'aaa_policies': len(campus_config.get('aaa_policies', [])),
            'services': len(campus_config.get('services', [])),
            'ap_configs': len(campus_config.get('ap_configs', []))
        }

        log_message(f'Converted: {summary["services"]} services, {summary["topologies"]} topologies, {summary["aaa_policies"]} AAA policies')
        update_progress('Conversion complete', 70)

        return jsonify({
            'success': True,
            'data': {
                'summary': summary,
                'services': [
                    {
                        'id': s.get('id'),
                        'name': s.get('serviceName'),
                        'ssid': s.get('ssid'),
                        'status': s.get('status')
                    }
                    for s in campus_config.get('services', [])
                ]
            }
        })

    except Exception as e:
        log_message(f'Error converting configuration: {str(e)}', 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/migrate', methods=['POST'])
@login_required
def migrate():
    """Execute migration to Edge Services"""
    try:
        data = request.json
        controller_url = data.get('controller_url')
        username = data.get('username')
        password = data.get('password')
        dry_run = data.get('dry_run', False)
        profile_assignments = data.get('profile_assignments', {})

        log_message('Starting migration...')
        update_progress('Migrating to Edge Services', 75)
        migration_state['status'] = 'running'

        if dry_run:
            log_message('DRY RUN MODE - No changes will be made', 'warning')

            # Save to JSON file
            output_file = '/tmp/migration_dry_run.json'
            with open(output_file, 'w') as f:
                json.dump(migration_state['converted_config'], f, indent=2)

            log_message(f'Configuration saved to {output_file}')
            update_progress('Dry run complete', 100)
            migration_state['status'] = 'completed'

            return jsonify({
                'success': True,
                'data': {
                    'dry_run': True,
                    'output_file': output_file
                }
            })

        # Initialize Edge Services client (authenticates automatically in __init__)
        controller_client = CampusControllerClient(
            base_url=controller_url,
            username=username,
            password=password,
            verbose=False
        )

        # If we get here, authentication succeeded (otherwise exception was thrown)
        log_message('Authenticated with Edge Services')

        campus_config = migration_state['converted_config']

        # Post configuration using unified method
        log_message('Posting configuration to Edge Services...')
        result = controller_client.post_configuration(campus_config)

        # Extract results
        results = result.get('details', {})

        update_progress('Applying profile assignments', 90)

        # Apply profile assignments
        if profile_assignments:
            log_message('Applying profile assignments...')
            assignment_count = 0

            for service_id, assignments in profile_assignments.items():
                # Group by profile
                profile_groups = {}
                for assignment in assignments:
                    profile_id = assignment['profile_id']
                    if profile_id not in profile_groups:
                        profile_groups[profile_id] = {
                            'profile_name': assignment['profile_name'],
                            'ssid_assignments': []
                        }
                    profile_groups[profile_id]['ssid_assignments'].append({
                        'serviceId': service_id,
                        'index': assignment['radio_index']
                    })

                # Apply assignments
                for profile_id, group in profile_groups.items():
                    log_message(f'Assigning to profile {group["profile_name"]}...')
                    if controller_client.update_profile_ssid_assignments(profile_id, group['ssid_assignments']):
                        assignment_count += len(group['ssid_assignments'])

            log_message(f'Applied {assignment_count} profile assignments')
            results['profile_assignments'] = assignment_count

        migration_state['results'] = results
        update_progress('Migration complete', 100)
        migration_state['status'] = 'completed'

        log_message('Migration completed successfully!', 'success')

        return jsonify({
            'success': True,
            'data': {
                'results': results
            }
        })

    except Exception as e:
        log_message(f'Error during migration: {str(e)}', 'error')
        migration_state['status'] = 'error'
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
@login_required
def get_status():
    """Get current migration status"""
    return jsonify({
        'success': True,
        'data': {
            'status': migration_state['status'],
            'progress': migration_state['progress'],
            'current_step': migration_state['current_step'],
            'logs': migration_state['logs'][-50:]  # Last 50 log entries
        }
    })


@app.route('/api/reset', methods=['POST'])
@login_required
def reset():
    """Reset migration state"""
    global migration_state
    migration_state = {
        'status': 'idle',
        'progress': 0,
        'current_step': '',
        'logs': [],
        'results': {},
        'xiq_data': {},
        'converted_config': {},
        'profiles': []
    }
    return jsonify({'success': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'

    print('=' * 70)
    print('XIQ to Edge Services Migration Tool - Web UI')
    print('=' * 70)
    print()
    print('Starting web server...')
    print(f'Open your browser and navigate to: http://localhost:{port}')
    print()
    print('Press Ctrl+C to stop the server')
    print('=' * 70)

    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
