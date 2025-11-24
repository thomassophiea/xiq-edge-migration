#!/usr/bin/env python3
"""
Apply fixes for Edge Services integration
This script patches the necessary files to fix posting issues
"""

import os
import sys

# Define the fixes to apply
FIXES = {
    'src/config_converter.py': {
        'changes': [
            {
                'find': 'def convert(self, xiq_config: Dict[str, Any]) -> Dict[str, Any]:',
                'replace': 'def convert(self, xiq_config: Dict[str, Any], existing_topologies: List[Dict] = None) -> Dict[str, Any]:',
                'description': 'Add existing_topologies parameter to convert method'
            },
            {
                'find': "        return {\n            'services': self._convert_ssids(xiq_config.get('ssids', []), xiq_config.get('vlans', [])),",
                'replace': "        return {\n            'services': self._convert_ssids(xiq_config.get('ssids', []), xiq_config.get('vlans', []), existing_topologies),",
                'description': 'Pass existing_topologies to _convert_ssids'
            },
            {
                'find': '    def _convert_ssids(self, ssids: List[Dict[str, Any]], vlans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:',
                'replace': '    def _convert_ssids(self, ssids: List[Dict[str, Any]], vlans: List[Dict[str, Any]], existing_topologies: List[Dict] = None) -> List[Dict[str, Any]]:',
                'description': 'Add existing_topologies parameter to _convert_ssids'
            },
            {
                'find': '        # Create VLAN ID to Topology ID mapping\n        vlan_to_topology = {}\n        topologies = self._convert_vlans(vlans)',
                'replace': '''        # Create VLAN ID to Topology ID mapping
        vlan_to_topology = {}

        # First, use existing topologies from Edge Services
        if existing_topologies:
            for topology in existing_topologies:
                vlan_id = topology.get('vlanid')
                topology_id = topology.get('id')
                if vlan_id and topology_id:
                    vlan_to_topology[vlan_id] = topology_id

        # Then add new topologies we're creating
        topologies = self._convert_vlans(vlans)''',
                'description': 'Use existing topologies first'
            },
            {
                'find': '            # Determine if captive portal is enabled\n            enable_captive_portal = ssid.get(\'captive_portal\') is not None\n\n            # Create role IDs (required even when not using captive portal)\n            authenticated_role_id = str(uuid.uuid4())\n            non_authenticated_role_id = str(uuid.uuid4())',
                'replace': '''            # Determine if captive portal is enabled
            enable_captive_portal = ssid.get('captive_portal') is not None

            # Use a standard authenticated role ID (from existing Edge Services config)
            # This is a default role ID that exists in Edge Services
            default_auth_role_id = "4459ee6c-2f76-11e7-93ae-92361f002671"''',
                'description': 'Use existing role ID instead of generating new one'
            },
            {
                'find': '                "enableCaptivePortal": False,  # Disable captive portal for now\n                "mbaAuthorization": False,  # Disable MBA\n                "authenticatedUserDefaultRoleID": default_auth_role_id,\n                "nonAuthenticatedUserDefaultRoleID": None,',
                'replace': '                "enableCaptivePortal": True,  # Required to avoid role ID error\n                "captivePortalType": "Internal",\n                "mbaAuthorization": False,  # Disable MBA\n                "authenticatedUserDefaultRoleID": default_auth_role_id,\n                "nonAuthenticatedUserDefaultRoleID": default_auth_role_id,  # Use same ID',
                'description': 'Enable captive portal and set both role IDs'
            }
        ]
    },
    'src/campus_controller_client.py': {
        'changes': [
            {
                'find': '        return results',
                'replace': '''        return results

    def get_existing_topologies(self) -> List[Dict[str, Any]]:
        """Get existing topologies from Edge Services to avoid conflicts"""
        url = f'{self.base_url}/v1/topologies'
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                topologies = response.json()
                return topologies if isinstance(topologies, list) else []
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Could not fetch existing topologies: {e}")
        return []''',
                'description': 'Add get_existing_topologies method',
                'after_method': 'post_configuration'
            }
        ]
    },
    'main.py': {
        'changes': [
            {
                'find': '    # Convert to Edge Services format\n    if verbose:\n        print("\\nConverting to Edge Services format...")\n\n    converter = ConfigConverter()\n    campus_config = converter.convert(filtered_config)',
                'replace': '''    # Convert to Edge Services format
    if verbose:
        print("\\nConverting to Edge Services format...")

    converter = ConfigConverter()

    # Get existing topologies from Edge Services to avoid conflicts
    existing_topologies = []
    if not dry_run and controller_client:
        try:
            existing_topologies = controller_client.get_existing_topologies()
            if verbose:
                print(f"  Found {len(existing_topologies)} existing topologies in Edge Services")
        except Exception as e:
            if verbose:
                print(f"  Warning: Could not fetch existing topologies: {e}")

    campus_config = converter.convert(filtered_config, existing_topologies)''',
                'description': 'Fetch existing topologies before conversion'
            }
        ]
    }
}

def apply_patches():
    """Apply all patches to the files"""
    print("=" * 70)
    print("Applying Edge Services Integration Fixes")
    print("=" * 70)

    for filename, patch_info in FIXES.items():
        print(f"\n📝 Patching: {filename}")

        filepath = filename
        if not os.path.exists(filepath):
            print(f"  ❌ File not found: {filepath}")
            continue

        # Read file
        with open(filepath, 'r') as f:
            content = f.read()

        original_content = content
        changes_applied = 0

        # Apply each change
        for change in patch_info['changes']:
            find_str = change['find']
            replace_str = change['replace']
            desc = change['description']

            if find_str in content:
                content = content.replace(find_str, replace_str, 1)
                changes_applied += 1
                print(f"  ✓ {desc}")
            else:
                print(f"  ⚠  Could not find: {desc}")
                print(f"     (String not found - may already be patched)")

        # Write back if changes were made
        if content != original_content:
            # Backup original
            backup_file = filepath + '.backup'
            with open(backup_file, 'w') as f:
                f.write(original_content)
            print(f"  💾 Backup saved to: {backup_file}")

            # Write patched version
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"  ✅ Applied {changes_applied} changes to {filename}")
        else:
            print(f"  ℹ️  No changes needed (already patched or patterns not found)")

    print("\n" + "=" * 70)
    print("✅ Patching complete!")
    print("=" * 70)
    print("\nYou can now test the converter:")
    print("  python main.py --xiq-login --controller-url https://your-controller.example.com \\")
    print("    --username admin --password 'your-password'")
    print("\nBackup files have been created with .backup extension")

if __name__ == "__main__":
    try:
        apply_patches()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
