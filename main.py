#!/usr/bin/env python3
"""
Extreme Cloud IQ to Edge Services Configuration Converter
Extracts SSIDs, VLANs, and other common objects from XIQ and posts to Edge Services
"""

import argparse
import sys
import json
import getpass
from pathlib import Path
from src.xiq_parser import XIQParser
from src.xiq_api_client import XIQAPIClient
from src.campus_controller_client import CampusControllerClient
from src.config_converter import ConfigConverter
from src.export_utils import export_to_json, export_all_to_csv


def print_banner():
    """Print application banner"""
    print("=" * 70)
    print("  Extreme Cloud IQ → Edge Services Configuration Converter")
    print("=" * 70)
    print()


def get_xiq_region():
    """Prompt user to select XIQ region"""
    print("\nSelect your ExtremeCloud IQ region:")
    print("  1. Global (api.extremecloudiq.com)")
    print("  2. EU (api-eu.extremecloudiq.com)")
    print("  3. APAC (api-apac.extremecloudiq.com)")
    print("  4. California (cal-api.extremecloudiq.com)")

    choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"

    region_map = {
        "1": ("global", "https://api.extremecloudiq.com"),
        "2": ("eu", "https://api-eu.extremecloudiq.com"),
        "3": ("apac", "https://api-apac.extremecloudiq.com"),
        "4": ("cal", "https://cal-api.extremecloudiq.com")
    }

    return region_map.get(choice, ("global", "https://api.extremecloudiq.com"))


def get_xiq_credentials():
    """Prompt user for XIQ credentials"""
    print("\n" + "-" * 70)
    print("STEP 1: Extreme Cloud IQ Authentication")
    print("-" * 70)

    print("\nHow would you like to authenticate to XIQ?")
    print("  1. Username and Password")
    print("  2. API Token")
    print("  3. Use existing configuration file")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        # Username/Password login
        region_name, region_url = get_xiq_region()

        print(f"\nXIQ Region: {region_name}")
        print(f"API URL: {region_url}")
        print()

        username = input("XIQ Username (email): ").strip()
        password = getpass.getpass("XIQ Password: ")

        if not username or not password:
            print("Error: Username and password are required")
            sys.exit(1)

        return {
            'type': 'login',
            'username': username,
            'password': password,
            'region_url': region_url
        }

    elif choice == "2":
        # API Token
        region_name, region_url = get_xiq_region()

        print(f"\nXIQ Region: {region_name}")
        print(f"API URL: {region_url}")
        print()
        print("To get an API token:")
        print("  1. Log into Extreme Cloud IQ")
        print("  2. Go to Global Settings > API Token Management")
        print("  3. Click Generate and copy the token")
        print()

        token = getpass.getpass("XIQ API Token: ").strip()

        if not token:
            print("Error: API token is required")
            sys.exit(1)

        return {
            'type': 'token',
            'token': token,
            'region_url': region_url
        }

    elif choice == "3":
        # Configuration file
        print()
        file_path = input("Path to XIQ configuration file: ").strip()

        if not file_path:
            print("Error: File path is required")
            sys.exit(1)

        return {
            'type': 'file',
            'file_path': file_path
        }

    else:
        print("Invalid choice")
        sys.exit(1)


def get_campus_controller_info():
    """Prompt user for Edge Services information"""
    print("\n" + "-" * 70)
    print("STEP 2: Edge Services Configuration")
    print("-" * 70)
    print()

    # Get controller URL
    print("Enter Edge Services IP or hostname")
    print("Examples: 10.10.10.100, controller.example.com")
    controller_input = input("\nEdge Services: ").strip()

    if not controller_input:
        print("Error: Edge Services address is required")
        sys.exit(1)

    # Build URL with HTTPS and port
    if not controller_input.startswith('http'):
        controller_url = f"https://{controller_input}"
    else:
        controller_url = controller_input

    # Get credentials
    print()
    username = input("Edge Services Username [admin]: ").strip() or "admin"
    password = getpass.getpass("Edge Services Password: ")

    if not password:
        print("Error: Password is required")
        sys.exit(1)

    return {
        'url': controller_url,
        'username': username,
        'password': password
    }


def confirm_action(message):
    """Ask user for confirmation"""
    response = input(f"\n{message} (y/n): ").strip().lower()
    return response in ['y', 'yes']


def select_objects_to_migrate(xiq_config):
    """
    Interactive selection of which objects to migrate

    Args:
        xiq_config: Full XIQ configuration

    Returns:
        Filtered configuration with only selected objects
    """
    print("\n" + "=" * 70)
    print("SELECT OBJECTS TO MIGRATE")
    print("=" * 70)

    filtered_config = {
        'ssids': [],
        'vlans': [],
        'radio_profiles': [],
        'network_policies': xiq_config.get('network_policies', []),
        'authentication': [],
        'qos_profiles': [],
        'captive_portals': [],
        'user_profiles': []
    }

    # 1. Select SSIDs
    ssids = xiq_config.get('ssids', [])
    if ssids:
        print("\n" + "-" * 70)
        print(f"SSIDs Found: {len(ssids)}")
        print("-" * 70)

        for idx, ssid in enumerate(ssids, 1):
            sec_type = ssid.get('security', {}).get('type', 'unknown')
            vlan = ssid.get('vlan_id', 'N/A')
            enabled = "✓" if ssid.get('enabled', True) else "✗"
            print(f"  {idx}. [{enabled}] {ssid.get('name'):<30} (Security: {sec_type:10} VLAN: {vlan})")

        print("\nSelect SSIDs to migrate:")
        print("  • Enter numbers separated by commas (e.g., 1,2,4)")
        print("  • Enter 'all' to select all SSIDs")
        print("  • Enter 'none' to skip SSIDs")

        selection = input("\nYour selection: ").strip().lower()

        if selection == 'all':
            filtered_config['ssids'] = ssids
            print(f"✓ Selected all {len(ssids)} SSIDs")
        elif selection == 'none':
            print("✓ Skipped SSIDs")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                filtered_config['ssids'] = [ssids[i] for i in indices if 0 <= i < len(ssids)]
                print(f"✓ Selected {len(filtered_config['ssids'])} SSIDs")
            except (ValueError, IndexError):
                print("⚠ Invalid selection, no SSIDs selected")
    else:
        print("\n⚠ No SSIDs found in XIQ configuration")

    # 2. Select VLANs
    vlans = xiq_config.get('vlans', [])
    if vlans:
        print("\n" + "-" * 70)
        print(f"VLANs Found: {len(vlans)}")
        print("-" * 70)

        for idx, vlan in enumerate(vlans, 1):
            vlan_id = vlan.get('vlan_id', 'N/A')
            subnet = vlan.get('subnet') or 'No subnet'
            name = vlan.get('name') or f'VLAN_{vlan_id}'
            dhcp = "DHCP" if vlan.get('dhcp_enabled') else "No DHCP"
            print(f"  {idx}. VLAN {str(vlan_id):<6} {name:<25} ({subnet:<20} {dhcp})")

        print("\nSelect VLANs to migrate:")
        print("  • Enter numbers separated by commas (e.g., 1,2,3)")
        print("  • Enter 'all' to select all VLANs")
        print("  • Enter 'none' to skip VLANs")
        print("  • Enter 'auto' to auto-select VLANs used by selected SSIDs")

        selection = input("\nYour selection: ").strip().lower()

        if selection == 'all':
            filtered_config['vlans'] = vlans
            print(f"✓ Selected all {len(vlans)} VLANs")
        elif selection == 'none':
            print("✓ Skipped VLANs")
        elif selection == 'auto':
            # Auto-select VLANs that are used by selected SSIDs
            used_vlan_ids = set()
            for ssid in filtered_config['ssids']:
                vlan_id = ssid.get('vlan_id')
                if vlan_id:
                    used_vlan_ids.add(vlan_id)

            filtered_config['vlans'] = [v for v in vlans if v.get('vlan_id') in used_vlan_ids]
            print(f"✓ Auto-selected {len(filtered_config['vlans'])} VLANs used by SSIDs")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                filtered_config['vlans'] = [vlans[i] for i in indices if 0 <= i < len(vlans)]
                print(f"✓ Selected {len(filtered_config['vlans'])} VLANs")
            except (ValueError, IndexError):
                print("⚠ Invalid selection, no VLANs selected")
    else:
        print("\n⚠ No VLANs found in XIQ configuration")

    # 3. Select RADIUS Servers
    radius_servers = xiq_config.get('authentication', [])
    if radius_servers:
        print("\n" + "-" * 70)
        print(f"RADIUS Servers Found: {len(radius_servers)}")
        print("-" * 70)

        for idx, server in enumerate(radius_servers, 1):
            ip = server.get('ip', server.get('address', 'N/A'))
            name = server.get('name', f'Server-{idx}')
            port = server.get('auth_port', server.get('port', 1812))
            print(f"  {idx}. {name:<30} ({ip}:{port})")

        print("\nSelect RADIUS servers to migrate:")
        print("  • Enter numbers separated by commas (e.g., 1,2)")
        print("  • Enter 'all' to select all RADIUS servers")
        print("  • Enter 'none' to skip RADIUS servers")

        selection = input("\nYour selection: ").strip().lower()

        if selection == 'all':
            filtered_config['authentication'] = radius_servers
            print(f"✓ Selected all {len(radius_servers)} RADIUS servers")
        elif selection == 'none':
            print("✓ Skipped RADIUS servers")
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                filtered_config['authentication'] = [radius_servers[i] for i in indices if 0 <= i < len(radius_servers)]
                print(f"✓ Selected {len(filtered_config['authentication'])} RADIUS servers")
            except (ValueError, IndexError):
                print("⚠ Invalid selection, no RADIUS servers selected")
    else:
        print("\n⚠ No RADIUS servers found in XIQ configuration")

    # 4. Radio Profiles (informational only)
    radio_profiles = xiq_config.get('radio_profiles', [])
    if radio_profiles:
        print("\n" + "-" * 70)
        print(f"Radio Profiles Found: {len(radio_profiles)}")
        print("-" * 70)
        print("  Note: Radio profiles are informational only and not migrated directly")
        for idx, profile in enumerate(radio_profiles, 1):
            band = profile.get('band', 'N/A')
            channel = profile.get('channel', 'auto')
            print(f"  {idx}. {profile.get('name'):<30} (Band: {band}, Channel: {channel})")

    # Summary
    print("\n" + "=" * 70)
    print("SELECTION SUMMARY")
    print("=" * 70)
    print(f"  SSIDs:          {len(filtered_config['ssids'])}")
    print(f"  VLANs:          {len(filtered_config['vlans'])}")
    print(f"  RADIUS Servers: {len(filtered_config['authentication'])}")

    if not confirm_action("\nProceed with these selections?"):
        print("\nCancelled. Please run the tool again to make new selections.")
        sys.exit(0)

    return filtered_config


def main():
    parser = argparse.ArgumentParser(
        description='Convert Extreme Cloud IQ Wireless Configuration to Edge Services',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for all credentials)
  python main.py

  # Command-line mode with file
  python main.py --input-file config.json --controller-url https://10.10.10.100 --username admin --password secret

  # Dry run to test conversion
  python main.py --dry-run --output test.json
        """
    )

    # Make all arguments optional for interactive mode
    parser.add_argument(
        '--input-file',
        type=str,
        help='Path to XIQ configuration file (JSON format)'
    )
    parser.add_argument(
        '--xiq-token',
        type=str,
        help='XIQ API token to pull configuration directly from XIQ'
    )
    parser.add_argument(
        '--xiq-username',
        type=str,
        help='XIQ username (email)'
    )
    parser.add_argument(
        '--xiq-password',
        type=str,
        help='XIQ password'
    )
    parser.add_argument(
        '--xiq-region',
        type=str,
        choices=['global', 'eu', 'apac', 'cal'],
        default='global',
        help='XIQ region (global, eu, apac, cal). Default: global'
    )
    parser.add_argument(
        '--controller-url',
        type=str,
        help='Edge Services URL or IP (e.g., https://10.10.10.100 or 192.168.1.100)'
    )
    parser.add_argument(
        '--username',
        type=str,
        help='Edge Services username'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Edge Services password'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse and convert without posting to controller'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Save converted configuration to file (JSON format)'
    )
    parser.add_argument(
        '--export-csv',
        type=str,
        help='Export XIQ configuration to CSV files in specified directory'
    )
    parser.add_argument(
        '--export-json',
        type=str,
        help='Export raw XIQ configuration to JSON file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--select-all',
        action='store_true',
        help='Skip interactive selection and migrate all objects'
    )

    args = parser.parse_args()

    try:
        # Print banner
        print_banner()

        # Determine if we're in interactive mode or command-line mode
        interactive_mode = not (args.input_file or args.xiq_token or args.xiq_username)

        # STEP 1: Get XIQ Configuration
        if interactive_mode:
            xiq_creds = get_xiq_credentials()
        else:
            # Command-line mode
            xiq_creds = None
            if args.input_file:
                xiq_creds = {'type': 'file', 'file_path': args.input_file}
            elif args.xiq_token:
                region_urls = {
                    'global': 'https://api.extremecloudiq.com',
                    'eu': 'https://api-eu.extremecloudiq.com',
                    'apac': 'https://api-apac.extremecloudiq.com',
                    'cal': 'https://cal-api.extremecloudiq.com'
                }
                xiq_creds = {
                    'type': 'token',
                    'token': args.xiq_token,
                    'region_url': region_urls.get(args.xiq_region, 'https://api.extremecloudiq.com')
                }
            elif args.xiq_username:
                if not args.xiq_password:
                    args.xiq_password = getpass.getpass("XIQ Password: ")
                region_urls = {
                    'global': 'https://api.extremecloudiq.com',
                    'eu': 'https://api-eu.extremecloudiq.com',
                    'apac': 'https://api-apac.extremecloudiq.com',
                    'cal': 'https://cal-api.extremecloudiq.com'
                }
                xiq_creds = {
                    'type': 'login',
                    'username': args.xiq_username,
                    'password': args.xiq_password,
                    'region_url': region_urls.get(args.xiq_region, 'https://api.extremecloudiq.com')
                }

        # Get configuration from XIQ
        if xiq_creds['type'] == 'file':
            # Read from file
            input_path = Path(xiq_creds['file_path'])
            if not input_path.exists():
                print(f"\nError: Input file '{xiq_creds['file_path']}' not found")
                sys.exit(1)

            print(f"\nReading XIQ configuration from {xiq_creds['file_path']}...")
            xiq_parser = XIQParser(xiq_creds['file_path'])
            xiq_config = xiq_parser.parse()

        elif xiq_creds['type'] == 'login':
            # Login with username/password
            print(f"\nAuthenticating to Extreme Cloud IQ...")
            print(f"  Region: {xiq_creds['region_url']}")

            xiq_client = XIQAPIClient.login(
                username=xiq_creds['username'],
                password=xiq_creds['password'],
                base_url=xiq_creds['region_url'],
                verbose=args.verbose
            )

            print("\n✓ Authentication successful")
            print("Retrieving configuration from XIQ...")
            xiq_config = xiq_client.get_configuration()

        elif xiq_creds['type'] == 'token':
            # Use API token
            print(f"\nConnecting to Extreme Cloud IQ API...")
            print(f"  Region: {xiq_creds['region_url']}")

            xiq_client = XIQAPIClient(
                api_token=xiq_creds['token'],
                base_url=xiq_creds['region_url'],
                verbose=args.verbose
            )

            if not xiq_client.test_connection():
                print("\nError: Failed to connect to XIQ API. Please check your API token.")
                sys.exit(1)

            print("\n✓ Connection successful")
            print("Retrieving configuration from XIQ...")
            xiq_config = xiq_client.get_configuration()

        # Show what was extracted
        print("\n✓ Configuration retrieved from XIQ")
        print(f"  - SSIDs: {len(xiq_config.get('ssids', []))}")
        print(f"  - VLANs: {len(xiq_config.get('vlans', []))}")
        print(f"  - Radio Profiles: {len(xiq_config.get('radio_profiles', []))}")
        print(f"  - RADIUS Servers: {len(xiq_config.get('authentication', []))}")

        # Show SSID details if verbose
        if args.verbose and xiq_config.get('ssids'):
            print("\n  SSIDs found:")
            for ssid in xiq_config.get('ssids', []):
                sec_type = ssid.get('security', {}).get('type', 'unknown')
                vlan = ssid.get('vlan_id', 'N/A')
                print(f"    - {ssid.get('name')} (Security: {sec_type}, VLAN: {vlan})")

        # Export raw XIQ config if requested
        if args.export_json:
            print(f"\nExporting raw XIQ configuration to {args.export_json}...")
            export_to_json(xiq_config, args.export_json)
            print(f"✓ Raw XIQ configuration saved to {args.export_json}")

        # Export to CSV if requested
        if args.export_csv:
            print(f"\nExporting XIQ configuration to CSV files in {args.export_csv}...")
            csv_files = export_all_to_csv(xiq_config, args.export_csv)
            print("✓ Exported to CSV:")
            for obj_type, file_path in csv_files.items():
                if file_path:
                    print(f"  - {obj_type}: {file_path}")

        # Interactive object selection (if in interactive mode and not --select-all)
        if interactive_mode and not args.select_all:
            xiq_config = select_objects_to_migrate(xiq_config)
        elif args.select_all:
            print("\n✓ Migrating all objects (--select-all)")

        # STEP 2: Convert to Edge Services format
        print("\n" + "-" * 70)
        print("Converting to Edge Services format...")
        print("-" * 70)

        # If posting to Edge Services, get controller info and fetch existing topologies
        existing_topologies = []
        controller_client = None

        if not args.dry_run:
            # Get Edge Services info first
            if interactive_mode:
                cc_info = get_campus_controller_info()
            else:
                if not args.controller_url:
                    print("\nError: --controller-url is required (or run without args for interactive mode)")
                    sys.exit(1)
                if not args.username:
                    args.username = input("\nEdge Services Username: ").strip()
                if not args.password:
                    args.password = getpass.getpass("Edge Services Password: ")

                cc_info = {
                    'url': args.controller_url,
                    'username': args.username,
                    'password': args.password
                }

            # Connect to Edge Services and fetch existing topologies
            print(f"\nConnecting to Edge Services at {cc_info['url']}...")
            try:
                controller_client = CampusControllerClient(
                    cc_info['url'],
                    cc_info['username'],
                    cc_info['password'],
                    verbose=args.verbose
                )
                print("✓ Connected to Edge Services")

                # Fetch existing topologies to avoid conflicts
                print("Fetching existing topologies from Edge Services...")
                existing_topologies = controller_client.get_existing_topologies()
                print(f"✓ Found {len(existing_topologies)} existing topologies")
            except Exception as e:
                print(f"✗ Error connecting to Edge Services: {e}")
                sys.exit(1)

        converter = ConfigConverter()
        campus_config = converter.convert(xiq_config, existing_topologies)

        print(f"\n✓ Conversion complete")
        print(f"  - Services (SSIDs): {len(campus_config.get('services', []))}")
        print(f"  - Topologies (VLANs): {len(campus_config.get('topologies', []))}")
        print(f"  - AAA Policies: {len(campus_config.get('aaa_policies', []))}")

        # Save to file if requested
        if args.output:
            print(f"\nSaving converted configuration to {args.output}...")
            with open(args.output, 'w') as f:
                json.dump(campus_config, f, indent=2)
            print("✓ Configuration saved successfully")

        # STEP 3: Post to Edge Services
        if not args.dry_run and controller_client:
            # Confirm before posting
            print("\n" + "-" * 70)
            print("STEP 3: Post Configuration to Edge Services")
            print("-" * 70)
            print(f"\nReady to post configuration to: {cc_info['url']}")
            print(f"  - {len(campus_config.get('services', []))} Services (SSIDs)")
            print(f"  - {len(campus_config.get('topologies', []))} Topologies (VLANs)")
            print(f"  - {len(campus_config.get('aaa_policies', []))} AAA Policies")

            if interactive_mode and not confirm_action("\nProceed with posting to Edge Services?"):
                print("\nCancelled by user. Configuration was not posted.")
                if not args.output:
                    save_output = confirm_action("Would you like to save the converted configuration to a file?")
                    if save_output:
                        output_file = input("Output filename [campus_config.json]: ").strip() or "campus_config.json"
                        with open(output_file, 'w') as f:
                            json.dump(campus_config, f, indent=2)
                        print(f"✓ Configuration saved to {output_file}")
                sys.exit(0)

            print("\nPosting configuration...")

            result = controller_client.post_configuration(campus_config)

            if result['success']:
                print("\n" + "=" * 70)
                print("✓ SUCCESS: Configuration posted to Edge Services!")
                print("=" * 70)
                if result.get('details'):
                    print("\nDetails:")
                    for key, value in result['details'].items():
                        print(f"  {key}: {value}")
            else:
                print("\n" + "=" * 70)
                print("✗ ERROR: Failed to post configuration")
                print("=" * 70)
                print(f"\nError: {result.get('error')}")
                if result.get('errors'):
                    print("\nErrors:")
                    for error in result['errors']:
                        print(f"  - {error}")
                sys.exit(1)
        else:
            print("\n" + "-" * 70)
            print("[DRY RUN MODE - Configuration not posted to Edge Services]")
            print("-" * 70)
            if not args.output:
                print("\nConverted configuration preview (first 500 characters):")
                print(json.dumps(campus_config, indent=2)[:500] + "...")

        print("\n" + "=" * 70)
        print("✓ Process completed successfully!")
        print("=" * 70)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n" + "=" * 70)
        print("✗ ERROR")
        print("=" * 70)
        print(f"\n{str(e)}")
        if args.verbose:
            print("\nStack trace:")
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
