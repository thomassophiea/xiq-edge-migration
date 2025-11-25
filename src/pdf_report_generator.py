"""
PDF Report Generator for XIQ to Edge Services Migration
Generates comprehensive migration assessment reports
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, List
import io


class MigrationReportGenerator:
    """Generates detailed PDF reports for XIQ to Edge Services migration"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6200EE'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#6200EE'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#018786'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))

    def generate_report(self, xiq_data: Dict[str, Any], output_path: str = None) -> io.BytesIO:
        """
        Generate a comprehensive migration report

        Args:
            xiq_data: Dictionary containing XIQ configuration data
            output_path: Optional file path to save PDF (if None, returns BytesIO)

        Returns:
            BytesIO buffer containing the PDF
        """
        # Create PDF buffer
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer if not output_path else output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Build content
        story = []

        # Add title page
        story.extend(self._create_title_page())
        story.append(PageBreak())

        # Add executive summary
        story.extend(self._create_executive_summary(xiq_data))
        story.append(Spacer(1, 0.2 * inch))

        # Add network inventory
        story.extend(self._create_network_inventory(xiq_data))
        story.append(PageBreak())

        # Add SSID details
        story.extend(self._create_ssid_details(xiq_data.get('ssids', [])))
        story.append(PageBreak())

        # Add VLAN details
        story.extend(self._create_vlan_details(xiq_data.get('vlans', [])))
        story.append(PageBreak())

        # Add RADIUS details
        story.extend(self._create_radius_details(xiq_data.get('authentication', [])))
        story.append(PageBreak())

        # Add device inventory
        story.extend(self._create_device_inventory(xiq_data.get('devices', [])))
        story.append(PageBreak())

        # Add migration strategy
        story.extend(self._create_migration_strategy(xiq_data))
        story.append(PageBreak())

        # Add detailed object mapping
        story.extend(self._create_object_mapping_details(xiq_data))
        story.append(PageBreak())

        # Add Edge Services API reference
        story.extend(self._create_edge_services_api_reference())
        story.append(PageBreak())

        # Add NGC architecture and migration
        story.extend(self._create_ngc_migration_guide(xiq_data))
        story.append(PageBreak())

        # Add NGC object mapping
        story.extend(self._create_ngc_object_mapping())
        story.append(PageBreak())

        # Add complete migration timeline
        story.extend(self._create_complete_migration_timeline())

        # Build PDF
        doc.build(story)

        # Return buffer
        if not output_path:
            buffer.seek(0)
            return buffer

    def _create_title_page(self) -> List:
        """Create title page"""
        elements = []

        elements.append(Spacer(1, 2 * inch))
        elements.append(Paragraph(
            "XIQ to Edge Services<br/>Migration Assessment Report",
            self.styles['CustomTitle']
        ))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['CustomSubtitle']
        ))

        elements.append(Spacer(1, 0.5 * inch))
        elements.append(HRFlowable(
            width="80%",
            thickness=2,
            color=colors.HexColor('#6200EE'),
            spaceAfter=20,
            spaceBefore=20
        ))

        elements.append(Paragraph(
            "Comprehensive analysis of ExtremeCloud IQ configuration<br/>"
            "and migration strategy to Extreme Edge Services",
            self.styles['Normal']
        ))

        return elements

    def _create_executive_summary(self, xiq_data: Dict[str, Any]) -> List:
        """Create executive summary section"""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        # Summary statistics
        ssid_count = len(xiq_data.get('ssids', []))
        vlan_count = len(xiq_data.get('vlans', []))
        radius_count = len(xiq_data.get('authentication', []))
        device_count = len(xiq_data.get('devices', []))

        summary_data = [
            ['Configuration Item', 'Count', 'Status'],
            ['Wireless Networks (SSIDs)', str(ssid_count), 'Ready for Migration'],
            ['VLANs', str(vlan_count), 'Ready for Migration'],
            ['RADIUS Servers', str(radius_count), 'Requires Review'],
            ['Access Points', str(device_count), 'Inventory Complete'],
        ]

        table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(table)

        return elements

    def _create_network_inventory(self, xiq_data: Dict[str, Any]) -> List:
        """Create network inventory overview"""
        elements = []

        elements.append(Paragraph("Network Inventory Overview", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "This section provides a high-level overview of the current XIQ network configuration.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Security types analysis
        ssids = xiq_data.get('ssids', [])
        security_types = {}
        for ssid in ssids:
            sec_type = ssid.get('security', {}).get('type', 'Unknown')
            security_types[sec_type] = security_types.get(sec_type, 0) + 1

        elements.append(Paragraph("Security Distribution", self.styles['SubsectionHeader']))

        if security_types:
            sec_data = [['Security Type', 'Count', 'Percentage']]
            total = len(ssids)
            for sec_type, count in security_types.items():
                percentage = f"{(count/total*100):.1f}%" if total > 0 else "0%"
                sec_data.append([sec_type, str(count), percentage])

            sec_table = Table(sec_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
            sec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            elements.append(sec_table)

        return elements

    def _create_ssid_details(self, ssids: List[Dict[str, Any]]) -> List:
        """Create detailed SSID information"""
        elements = []

        elements.append(Paragraph(f"Wireless Networks (SSIDs) - {len(ssids)} Total", self.styles['SectionHeader']))

        if not ssids:
            elements.append(Paragraph("No SSIDs found in XIQ configuration.", self.styles['Normal']))
            return elements

        for idx, ssid in enumerate(ssids, 1):
            elements.append(Paragraph(f"{idx}. {ssid.get('name', 'Unnamed SSID')}", self.styles['SubsectionHeader']))

            # SSID details table
            ssid_data = [
                ['Property', 'Value'],
                ['SSID Name', ssid.get('ssid', 'N/A')],
                ['Security Type', ssid.get('security', {}).get('type', 'N/A')],
                ['VLAN ID', str(ssid.get('vlan_id', 'N/A'))],
                ['Broadcast', 'Yes' if not ssid.get('hidden', False) else 'No'],
                ['Status', ssid.get('status', 'Unknown')],
            ]

            # Add encryption if available
            if 'encryption' in ssid.get('security', {}):
                ssid_data.append(['Encryption', ssid['security']['encryption']])

            # Add authentication method
            if ssid.get('security', {}).get('type') == 'wpa2-enterprise':
                ssid_data.append(['Authentication', 'RADIUS (802.1X)'])
            elif ssid.get('security', {}).get('type') == 'wpa2-psk':
                ssid_data.append(['Authentication', 'Pre-Shared Key'])

            ssid_table = Table(ssid_data, colWidths=[2.5*inch, 4*inch])
            ssid_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            elements.append(ssid_table)
            elements.append(Spacer(1, 0.2 * inch))

        return elements

    def _create_vlan_details(self, vlans: List[Dict[str, Any]]) -> List:
        """Create detailed VLAN information"""
        elements = []

        elements.append(Paragraph(f"VLANs - {len(vlans)} Total", self.styles['SectionHeader']))

        if not vlans:
            elements.append(Paragraph("No VLANs found in XIQ configuration.", self.styles['Normal']))
            return elements

        vlan_data = [['VLAN ID', 'Name', 'Description', 'Status']]

        for vlan in vlans:
            vlan_data.append([
                str(vlan.get('vlan_id', 'N/A')),
                vlan.get('name', 'Unnamed'),
                vlan.get('description', 'No description')[:50],
                'Active'
            ])

        vlan_table = Table(vlan_data, colWidths=[1*inch, 2*inch, 2.5*inch, 1*inch])
        vlan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(vlan_table)

        return elements

    def _create_radius_details(self, radius_servers: List[Dict[str, Any]]) -> List:
        """Create detailed RADIUS server information"""
        elements = []

        elements.append(Paragraph(f"RADIUS Servers - {len(radius_servers)} Total", self.styles['SectionHeader']))

        if not radius_servers:
            elements.append(Paragraph("No RADIUS servers found in XIQ configuration.", self.styles['Normal']))
            return elements

        elements.append(Paragraph(
            "<b>Note:</b> RADIUS server shared secrets are not included in this report for security reasons. "
            "You will need to manually configure these in Edge Services.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))

        for idx, radius in enumerate(radius_servers, 1):
            elements.append(Paragraph(f"{idx}. {radius.get('name', 'Unnamed Server')}", self.styles['SubsectionHeader']))

            radius_data = [
                ['Property', 'Value'],
                ['Server Name', radius.get('name', 'N/A')],
                ['IP Address', radius.get('ip', 'N/A')],
                ['Port', str(radius.get('port', '1812'))],
                ['Type', radius.get('type', 'Authentication')],
                ['Accounting Port', str(radius.get('accounting_port', '1813'))],
            ]

            radius_table = Table(radius_data, colWidths=[2.5*inch, 4*inch])
            radius_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            elements.append(radius_table)
            elements.append(Spacer(1, 0.2 * inch))

        return elements

    def _create_device_inventory(self, devices: List[Dict[str, Any]]) -> List:
        """Create device inventory section"""
        elements = []

        elements.append(Paragraph(f"Access Point Inventory - {len(devices)} Total", self.styles['SectionHeader']))

        if not devices:
            elements.append(Paragraph("No devices found in XIQ configuration.", self.styles['Normal']))
            return elements

        # Group devices by model
        device_models = {}
        for device in devices:
            model = device.get('model', 'Unknown Model')
            if model not in device_models:
                device_models[model] = []
            device_models[model].append(device)

        elements.append(Paragraph("Device Summary by Model", self.styles['SubsectionHeader']))

        model_data = [['Model', 'Count', 'Firmware', 'Status']]
        for model, device_list in device_models.items():
            firmware = device_list[0].get('firmware', 'N/A') if device_list else 'N/A'
            model_data.append([
                model,
                str(len(device_list)),
                firmware,
                'Active'
            ])

        model_table = Table(model_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1*inch])
        model_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(model_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Detailed device list
        elements.append(Paragraph("Detailed Device List", self.styles['SubsectionHeader']))

        device_data = [['Hostname', 'Serial Number', 'Model', 'MAC Address']]
        for device in devices[:50]:  # Limit to first 50 devices for PDF size
            device_data.append([
                device.get('hostname', 'N/A')[:20],
                device.get('serial_number', 'N/A'),
                device.get('model', 'N/A'),
                device.get('mac_address', 'N/A')
            ])

        if len(devices) > 50:
            elements.append(Paragraph(
                f"<b>Note:</b> Showing first 50 of {len(devices)} devices. "
                "Contact your administrator for the complete device list.",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 0.1 * inch))

        device_table = Table(device_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
        device_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E0E0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(device_table)

        return elements

    def _create_migration_strategy(self, xiq_data: Dict[str, Any]) -> List:
        """Create migration strategy section"""
        elements = []

        elements.append(Paragraph("Migration Strategy & Recommendations", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "This section outlines the recommended approach for migrating from XIQ device-level "
            "configuration to Edge Services centralized management.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Phase 1
        elements.append(Paragraph("Phase 1: Pre-Migration Preparation", self.styles['SubsectionHeader']))
        elements.append(Paragraph(
            "<b>1. Audit Current Configuration</b><br/>"
            "• Verify all SSIDs are documented and approved<br/>"
            "• Confirm VLAN assignments and IP addressing schemes<br/>"
            "• Test RADIUS server connectivity and authentication<br/>"
            "• Document any custom device-specific configurations<br/><br/>"

            "<b>2. Edge Services Setup</b><br/>"
            "• Deploy Edge Services controller (virtual or hardware)<br/>"
            "• Configure management network connectivity<br/>"
            "• Set up OAuth 2.0 authentication<br/>"
            "• Create organizational hierarchy (Sites, Profiles)<br/><br/>"

            "<b>3. Network Infrastructure</b><br/>"
            "• Ensure IP reachability between APs and Edge Services<br/>"
            "• Configure firewall rules for control plane traffic<br/>"
            "• Verify NTP, DNS, and DHCP services<br/>"
            "• Plan for temporary dual-management during transition",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Phase 2
        elements.append(Paragraph("Phase 2: Configuration Migration", self.styles['SubsectionHeader']))

        migration_steps = [
            ['Step', 'Action', 'Tool', 'Duration'],
            ['1', 'Export XIQ Configuration', 'This Tool', '5 min'],
            ['2', 'Create VLANs/Topologies', 'Edge Services UI or API', '30 min'],
            ['3', 'Configure RADIUS Servers', 'Edge Services UI', '15 min'],
            ['4', 'Create Wireless Services (SSIDs)', 'This Tool', '10 min'],
            ['5', 'Create Associated Profiles', 'Edge Services UI', '20 min'],
            ['6', 'Assign SSIDs to Profiles', 'This Tool', '10 min'],
            ['7', 'Test Configuration', 'Edge Services + Test AP', '60 min'],
        ]

        migration_table = Table(migration_steps, colWidths=[0.5*inch, 3*inch, 2*inch, 1*inch])
        migration_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(migration_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Phase 3
        elements.append(Paragraph("Phase 3: Device Onboarding", self.styles['SubsectionHeader']))
        elements.append(Paragraph(
            "<b>XIQ Device-Level to Edge Services Transition</b><br/><br/>"

            "The key difference between XIQ and Edge Services is the management model:<br/><br/>"

            "<b>XIQ Model (Current):</b><br/>"
            "• Each AP is individually configured in XIQ<br/>"
            "• Device profiles are assigned per-AP<br/>"
            "• Configuration is pushed to each device independently<br/>"
            "• APs connect directly to XIQ for management<br/><br/>"

            "<b>Edge Services Model (Target):</b><br/>"
            "• APs connect to Edge Services controller<br/>"
            "• Configuration is centralized at the controller level<br/>"
            "• Associated Profiles determine which SSIDs are broadcast<br/>"
            "• Group-based management reduces per-device configuration<br/><br/>"

            "<b>Recommended Onboarding Strategy:</b><br/><br/>"

            "1. <b>Pilot Deployment</b> (1-3 APs)<br/>"
            "   • Select test APs from different models<br/>"
            "   • Remove APs from XIQ management<br/>"
            "   • Configure APs to connect to Edge Services<br/>"
            "   • Verify SSIDs broadcast correctly<br/>"
            "   • Test client connectivity and roaming<br/><br/>"

            "2. <b>Phased Rollout</b> (By Site/Building)<br/>"
            "   • Migrate one site/building at a time<br/>"
            "   • Schedule during maintenance windows<br/>"
            "   • Keep XIQ available for rollback if needed<br/>"
            "   • Monitor for 24-48 hours before next phase<br/><br/>"

            "3. <b>Bulk Migration</b> (Remaining APs)<br/>"
            "   • After successful pilots, migrate remaining devices<br/>"
            "   • Use Edge Services zero-touch provisioning<br/>"
            "   • APs discover controller via DHCP Option 43 or DNS<br/>"
            "   • Automated profile assignment based on location/tags",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Critical Considerations
        elements.append(Paragraph("Critical Considerations", self.styles['SubsectionHeader']))

        considerations_data = [
            ['Area', 'Consideration', 'Impact'],
            ['RADIUS', 'Shared secrets must be manually configured', 'High'],
            ['VLANs', 'Edge Services uses topology UUIDs, not just VLAN IDs', 'Medium'],
            ['SSIDs', 'All migrated SSIDs start DISABLED for safety', 'Medium'],
            ['Profiles', 'AP profile assignment determines SSID visibility', 'High'],
            ['Firmware', 'Verify AP firmware compatibility with Edge Services', 'High'],
            ['Certificates', '802.1X certificates may need to be re-imported', 'Medium'],
            ['Roaming', 'Fast roaming settings may differ from XIQ', 'Low'],
        ]

        considerations_table = Table(considerations_data, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
        considerations_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57C00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(considerations_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Rollback Plan
        elements.append(Paragraph("Rollback Plan", self.styles['SubsectionHeader']))
        elements.append(Paragraph(
            "<b>If issues are encountered during migration:</b><br/><br/>"

            "1. <b>Immediate Rollback:</b> APs can be re-added to XIQ management<br/>"
            "2. <b>Configuration Backup:</b> This PDF serves as configuration documentation<br/>"
            "3. <b>Dual Management:</b> XIQ and Edge Services can coexist temporarily<br/>"
            "4. <b>Support Resources:</b> Contact Extreme Networks support if needed<br/><br/>"

            "<b>Success Criteria:</b><br/>"
            "• All SSIDs broadcasting on assigned profiles<br/>"
            "• Client authentication working (PSK and 802.1X)<br/>"
            "• Roaming between APs seamless<br/>"
            "• No coverage gaps or dead zones<br/>"
            "• Performance metrics meet baseline requirements",
            self.styles['Normal']
        ))

        elements.append(Spacer(1, 0.3 * inch))

        # Future: NGC Migration Path
        elements.append(Paragraph("Future: Next-Gen Configuration (NGC) Path", self.styles['SubsectionHeader']))
        elements.append(Paragraph(
            "<b>Note:</b> After successful migration to Edge Services, you can later transition to "
            "Extreme Platform ONE with Next-Gen Configuration (NGC) for enhanced cloud-based management. "
            "NGC provides:<br/><br/>"

            "• Unified management plane across all network infrastructure<br/>"
            "• Template-based configuration with site variables<br/>"
            "• Advanced assurance and analytics<br/>"
            "• Zero-touch provisioning at scale<br/>"
            "• API-first architecture for automation<br/><br/>"

            "The current Edge Services deployment will serve as the control plane foundation "
            "for NGC, making this migration a strategic investment in your network's future.",
            self.styles['Normal']
        ))

        return elements

    def _create_object_mapping_details(self, xiq_data: Dict[str, Any]) -> List:
        """Create detailed object mapping from XIQ to Edge Services"""
        elements = []

        elements.append(Paragraph("Detailed Object Mapping: XIQ → Edge Services", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "This section provides comprehensive mapping of configuration objects from XIQ to Edge Services, "
            "including all associations, dependencies, and API endpoints.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # SSID Mapping
        elements.append(Paragraph("1. SSID (Wireless Network) Mapping", self.styles['SubsectionHeader']))

        ssid_mapping = [
            ['XIQ Object', 'Edge Services Object', 'API Endpoint', 'Notes'],
            ['SSID Profile', 'Service', '/management/v1/services', 'One-to-one mapping'],
            ['SSID Name', 'serviceName + ssid', 'POST /services', 'Must be unique'],
            ['Security Type', 'privacy', 'POST /services', 'See security mapping'],
            ['VLAN ID', 'defaultTopology (UUID)', 'POST /services', 'Requires topology lookup'],
            ['Enable/Disable', 'status', 'POST /services', 'Always "disabled" initially'],
            ['Hidden SSID', 'suppressSsid', 'POST /services', 'Boolean flag'],
            ['Client Isolation', 'isolation', 'POST /services', 'Not directly supported'],
        ]

        ssid_table = Table(ssid_mapping, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
        ssid_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(ssid_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Security Type Mapping
        elements.append(Paragraph("Security Type Mapping", self.styles['SubsectionHeader']))

        security_mapping = [
            ['XIQ Security', 'Edge Services Privacy', 'Additional Fields Required'],
            ['Open', 'None (null)', 'None'],
            ['WPA2-PSK', '"PSK"', 'psk (shared key)'],
            ['WPA2-Enterprise', '"Enterprise"', 'aaaPolicy reference, RADIUS config'],
            ['WPA3-SAE', '"SAE"', 'saePassword'],
            ['WPA3-Enterprise', '"Enterprise192"', 'aaaPolicy reference, certificate'],
        ]

        security_table = Table(security_mapping, colWidths=[2*inch, 2*inch, 2.5*inch])
        security_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(security_table)
        elements.append(Spacer(1, 0.2 * inch))

        # VLAN/Topology Mapping
        elements.append(Paragraph("2. VLAN to Topology Mapping", self.styles['SubsectionHeader']))

        elements.append(Paragraph(
            "<b>Critical Difference:</b> XIQ uses simple VLAN IDs (1-4094), while Edge Services uses "
            "Topology objects with UUIDs. The migration tool automatically handles this mapping.<br/><br/>"

            "<b>Mapping Process:</b><br/>"
            "1. Tool retrieves existing topologies from Edge Services<br/>"
            "2. Matches VLAN IDs to existing topology UUIDs<br/>"
            "3. Creates new topologies only if VLAN doesn't exist<br/>"
            "4. Stores vlanId → topologyUUID mapping for SSID references",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))

        vlan_mapping = [
            ['XIQ Object', 'Edge Services Object', 'API Endpoint', 'Key Fields'],
            ['VLAN Profile', 'Topology', '/management/v1/topologies', 'id (UUID), vlanid'],
            ['VLAN ID', 'vlanid', 'POST /topologies', 'Integer 1-4094'],
            ['VLAN Name', 'name', 'POST /topologies', 'Descriptive name'],
            ['L3 Interface', 'l3Config', 'POST /topologies', 'Optional IP config'],
        ]

        vlan_table = Table(vlan_mapping, colWidths=[1.5*inch, 1.8*inch, 2*inch, 1.2*inch])
        vlan_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(vlan_table)
        elements.append(Spacer(1, 0.2 * inch))

        # RADIUS Mapping
        elements.append(Paragraph("3. RADIUS Server Mapping", self.styles['SubsectionHeader']))

        radius_mapping = [
            ['XIQ Object', 'Edge Services Object', 'API Endpoint', 'Migration Notes'],
            ['RADIUS Server', 'AAA Policy', '/management/v1/aaapolicy', 'One-to-one mapping'],
            ['Server IP', 'servers[].host', 'POST /aaapolicy', 'Primary/secondary'],
            ['Auth Port', 'servers[].authenticationPort', 'POST /aaapolicy', 'Default 1812'],
            ['Acct Port', 'servers[].accountingPort', 'POST /aaapolicy', 'Default 1813'],
            ['Shared Secret', 'servers[].secret', 'POST /aaapolicy', 'MANUAL CONFIG'],
            ['Timeout', 'servers[].timeout', 'POST /aaapolicy', 'In seconds'],
        ]

        radius_table = Table(radius_mapping, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.4*inch])
        radius_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(radius_table)
        elements.append(Spacer(1, 0.15 * inch))

        elements.append(Paragraph(
            "<b>⚠️ SECURITY CRITICAL:</b> RADIUS shared secrets cannot be retrieved from XIQ API. "
            "These must be manually configured in Edge Services AAA policies before SSIDs can authenticate users.",
            self.styles['Normal']
        ))

        elements.append(Spacer(1, 0.2 * inch))

        # Profile Association Mapping
        elements.append(Paragraph("4. AP Profile & SSID Association", self.styles['SubsectionHeader']))

        elements.append(Paragraph(
            "<b>Key Concept:</b> In Edge Services, SSIDs are NOT automatically broadcast by all APs. "
            "You must explicitly assign each SSID to Associated Profiles (AP groups).<br/><br/>"

            "<b>Association Process:</b>",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))

        profile_mapping = [
            ['Step', 'Action', 'API Endpoint', 'Required Fields'],
            ['1', 'Create Service (SSID)', 'POST /management/v1/services', 'serviceName, ssid, privacy'],
            ['2', 'Get Service UUID', 'GET /management/v1/services', 'Extract id from response'],
            ['3', 'Get Profile UUIDs', 'GET /management/v1/apconfig', 'List all AP profiles'],
            ['4', 'Assign to Profile', 'PATCH /management/v1/apconfig/{id}', 'Add service UUID to radioInterfaces'],
            ['5', 'Select Radio', 'PATCH /management/v1/apconfig/{id}', 'radioIndex: 0=all, 1=2.4G, 2=5G, 3=6G'],
        ]

        profile_table = Table(profile_mapping, colWidths=[0.5*inch, 2*inch, 2.5*inch, 1.5*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(profile_table)
        elements.append(Spacer(1, 0.15 * inch))

        elements.append(Paragraph(
            "<b>Example API Call:</b>",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.05 * inch))

        example_code = """
PATCH /management/v1/apconfig/{profile-uuid}
{
  "radioInterfaces": [
    {
      "radioIndex": 0,  // 0=all radios, 1=2.4GHz, 2=5GHz, 3=6GHz
      "assignedServices": [
        "{service-uuid-1}",
        "{service-uuid-2}"
      ]
    }
  ]
}
        """

        elements.append(Paragraph(
            f'<font name="Courier" size="7">{example_code}</font>',
            self.styles['Normal']
        ))

        return elements

    def _create_edge_services_api_reference(self) -> List:
        """Create Edge Services API reference section"""
        elements = []

        elements.append(Paragraph("Edge Services API Reference", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "Complete API reference for automated migration and configuration management.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Authentication
        elements.append(Paragraph("1. Authentication (OAuth 2.0)", self.styles['SubsectionHeader']))

        auth_info = [
            ['Endpoint', 'Method', 'Body Parameters', 'Response'],
            ['{base_url}:5825/management/v1/oauth2/token', 'POST', 'grant_type=password\nusername={user}\npassword={pass}', 'access_token\ntoken_type\nexpires_in'],
        ]

        auth_table = Table(auth_info, colWidths=[2.5*inch, 0.8*inch, 2*inch, 1.2*inch])
        auth_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(auth_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Key API Endpoints
        elements.append(Paragraph("2. Key API Endpoints", self.styles['SubsectionHeader']))

        api_endpoints = [
            ['Resource', 'GET (List)', 'POST (Create)', 'PATCH (Update)', 'DELETE'],
            ['Services (SSIDs)', '/v1/services', '/v1/services', '/v1/services/{id}', '/v1/services/{id}'],
            ['Topologies (VLANs)', '/v1/topologies', '/v1/topologies', '/v1/topologies/{id}', '/v1/topologies/{id}'],
            ['AAA Policies', '/v1/aaapolicy', '/v1/aaapolicy', '/v1/aaapolicy/{id}', '/v1/aaapolicy/{id}'],
            ['AP Profiles', '/v1/apconfig', '/v1/apconfig', '/v1/apconfig/{id}', '/v1/apconfig/{id}'],
            ['Rate Limiters', '/v1/ratelimit', '/v1/ratelimit', '/v1/ratelimit/{id}', '/v1/ratelimit/{id}'],
            ['CoS Policies', '/v1/cosPolicy', '/v1/cosPolicy', '/v1/cosPolicy/{id}', '/v1/cosPolicy/{id}'],
        ]

        api_table = Table(api_endpoints, colWidths=[1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1*inch])
        api_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(api_table)
        elements.append(Spacer(1, 0.15 * inch))

        elements.append(Paragraph(
            "<b>Note:</b> All API endpoints require Bearer token authentication in the Authorization header. "
            "Base URL format: https://{controller-ip}:5825/management",
            self.styles['Normal']
        ))

        return elements

    def _create_ngc_migration_guide(self, xiq_data: Dict[str, Any]) -> List:
        """Create NGC migration guide with complete architecture details"""
        elements = []

        elements.append(Paragraph("Next-Gen Configuration (NGC) Migration Path", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "This section details the migration path from Edge Services to Extreme Platform ONE with "
            "Next-Gen Configuration, including full architecture, object hierarchy, and API structure.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # NGC Architecture Overview
        elements.append(Paragraph("NGC Architecture Overview", self.styles['SubsectionHeader']))

        elements.append(Paragraph(
            "<b>Three-Tier Architecture:</b>",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))

        arch_layers = [
            ['Plane', 'Component', 'Role', 'Interfaces'],
            ['Management', 'Extreme Platform ONE', 'Configuration, Assurance, Telemetry, Lifecycle', 'REST API, GraphQL, Web UI'],
            ['Control', 'Edge Services', 'Control plane, Policy distribution, Local survivability', 'NGC→Edge API, Device control'],
            ['Data', 'Campus OS (APs/Switches)', 'Packet forwarding, QoS, Tunneling, RRM', 'Telemetry export, Config reception'],
        ]

        arch_table = Table(arch_layers, colWidths=[1.2*inch, 2*inch, 2.3*inch, 1*inch])
        arch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(arch_table)
        elements.append(Spacer(1, 0.2 * inch))

        # NGC Object Hierarchy
        elements.append(Paragraph("NGC Object Hierarchy", self.styles['SubsectionHeader']))

        elements.append(Paragraph(
            "<b>Hierarchical Structure (Top to Bottom):</b>",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))

        hierarchy = [
            ['Level', 'Object Type', 'API Resource', 'Contains/Purpose'],
            ['1', 'MSP', '/api/v1/msp', 'Managed Service Provider container'],
            ['2', 'Organization', '/api/v1/orgs', 'Customer/tenant container'],
            ['3', 'Site', '/api/v1/sites', 'Physical location with site variables'],
            ['4', 'NGC Template', '/api/v1/ngc/templates', 'Configuration bundle for deployment'],
            ['5', 'Networks (SSIDs)', '/api/v1/ngc/networks', 'Wireless network definitions'],
            ['6', 'Policies & Roles', '/api/v1/ngc/roles', 'Access control and segmentation'],
            ['7', 'Profiles', '/api/v1/ngc/profiles', 'AP, Radio, Switch profiles'],
            ['8', 'Devices', '/api/v1/devices', 'Physical inventory items'],
            ['9', 'Global Objects', '/api/v1/ngc/servers', 'Shared services (RADIUS, DHCP, etc.)'],
        ]

        hierarchy_table = Table(hierarchy, colWidths=[0.6*inch, 1.4*inch, 1.8*inch, 2.7*inch])
        hierarchy_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        elements.append(hierarchy_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Key NGC Concepts
        elements.append(Paragraph("Key NGC Concepts", self.styles['SubsectionHeader']))

        elements.append(Paragraph(
            "<b>1. Templates:</b> Reusable configuration bundles that can be applied to organizations, "
            "site groups, or individual sites. Templates contain Networks, Policies, Roles, and Profile references.<br/><br/>"

            "<b>2. Site Variables:</b> Allow template parameterization. Instead of hardcoding VLAN IDs or "
            "server IPs, use variables that are defined per-site: {vlan_management}, {radius_primary_ip}, etc.<br/><br/>"

            "<b>3. Campus OS Foundation:</b> All NGC configurations are ultimately compiled to Campus OS "
            "primitives. NGC provides abstraction, but Campus OS is the runtime.<br/><br/>"

            "<b>4. Edge Services as Control Plane:</b> NGC configurations are pushed to Edge Services, "
            "which then distributes runtime config to Campus OS devices.",
            self.styles['Normal']
        ))

        return elements

    def _create_ngc_object_mapping(self) -> List:
        """Create detailed NGC object mapping table"""
        elements = []

        elements.append(Paragraph("Complete Object Mapping: XIQ → Edge Services → NGC", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "Comprehensive three-way mapping showing how each configuration object evolves through the migration path.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Complete mapping table
        mapping_data = [
            ['XIQ Object', 'Edge Services Object', 'NGC Object', 'NGC API Endpoint', 'Key Differences'],
            ['SSID Profile', 'Service\n(/v1/services)', 'Network\n(/v1/ngc/networks)', 'POST /api/v1/ngc/networks', 'NGC adds band selection, identity pools'],
            ['VLAN', 'Topology\n(/v1/topologies)', 'vlan_assignment\n(in Network)', 'Network.vlan_assignment', 'Can use site variable: {vlan_guest}'],
            ['RADIUS Server', 'AAA Policy\n(/v1/aaapolicy)', 'Server\n(/v1/ngc/servers)', 'POST /api/v1/ngc/servers', 'Global object, reusable across sites'],
            ['Device Profile', 'AP Config\n(/v1/apconfig)', 'AP_Profile\n(/v1/ngc/profiles)', 'POST /api/v1/ngc/profiles', 'Template-based, with inheritance'],
            ['Radio Profile', 'RRM Settings\n(in apconfig)', 'Radio_Profile\n(/v1/ngc/profiles)', 'POST /api/v1/ngc/profiles', 'Separate object in NGC'],
            ['Device', 'Onboarded AP\n(automatic)', 'Device\n(/v1/devices)', 'POST /api/v1/devices', 'Explicit site and profile assignment'],
            ['Site', 'N/A', 'Site\n(/v1/sites)', 'POST /api/v1/sites', 'New concept: site variables'],
            ['User Role', 'Role ID\n(in Service)', 'PoliciesAndRoles\n(/v1/ngc/roles)', 'POST /api/v1/ngc/roles', 'Full firewall rules, RADIUS attribute mapping'],
        ]

        mapping_table = Table(mapping_data, colWidths=[1*inch, 1.3*inch, 1.3*inch, 1.5*inch, 1.4*inch])
        mapping_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(mapping_table)
        elements.append(Spacer(1, 0.2 * inch))

        # NGC Template Structure Example
        elements.append(Paragraph("NGC Template Structure Example", self.styles['SubsectionHeader']))

        template_example = """
POST /api/v1/ngc/templates
{
  "name": "Corporate_Office_Template",
  "applies_to": "site_group",
  "target_ids": ["{site-group-uuid}"],
  "networks": [
    {
      "name": "Corp_WiFi",
      "ssid": "MyCompany-Corp",
      "authentication": "wpa2-enterprise",
      "encryption": "aes",
      "vlan_assignment": "{vlan_corporate}",  // Site variable
      "role": "{corporate_user_role}",
      "radius": "{radius_primary}",  // Server reference
      "band_selection": ["2.4", "5", "6"],
      "services": {
        "radius": "{radius_server_ref}",
        "dhcp": "{dhcp_server_ref}"
      }
    },
    {
      "name": "Guest_WiFi",
      "ssid": "MyCompany-Guest",
      "authentication": "open",
      "vlan_assignment": "{vlan_guest}",  // Different per site
      "isolation": true
    }
  ],
  "profiles": {
    "ap_profile": "{standard_ap_profile_ref}",
    "radio_profile": "{high_density_radio_profile_ref}"
  }
}

// Site Variables (defined per site):
SITE_A variables: vlan_corporate=10, vlan_guest=20, radius_primary=10.1.1.10
SITE_B variables: vlan_corporate=110, vlan_guest=120, radius_primary=10.2.1.10
        """

        elements.append(Paragraph(
            '<font name="Courier" size="6">' + template_example.replace('\n', '<br/>').replace(' ', '&nbsp;') + '</font>',
            self.styles['Normal']
        ))

        return elements

    def _create_complete_migration_timeline(self) -> List:
        """Create complete end-to-end migration timeline"""
        elements = []

        elements.append(Paragraph("Complete Migration Timeline & Workflow", self.styles['SectionHeader']))

        elements.append(Paragraph(
            "End-to-end migration strategy from XIQ through Edge Services to NGC deployment.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Phase 1: XIQ to Edge Services
        elements.append(Paragraph("Phase 1: XIQ to Edge Services (Weeks 1-4)", self.styles['SubsectionHeader']))

        phase1_timeline = [
            ['Week', 'Tasks', 'Deliverables', 'Dependencies'],
            ['1', 'Assessment & Planning\n• Run this tool\n• Document all configs\n• Identify custom settings', '• PDF Assessment Report\n• Migration Plan\n• Resource allocation', 'Access to XIQ and future Edge Services'],
            ['2', 'Edge Services Deployment\n• Install controller\n• Configure networking\n• Setup OAuth\n• Test connectivity', '• Running Edge Services\n• Authentication working\n• Network validated', 'Hardware/VM resources, IP addressing'],
            ['3', 'Configuration Migration\n• Create Topologies\n• Configure RADIUS\n• Migrate SSIDs\n• Assign Profiles', '• All configs in Edge Services\n• SSIDs disabled but ready', 'RADIUS shared secrets from security team'],
            ['4', 'Pilot & Validation\n• Onboard test APs\n• Validate all SSIDs\n• Test roaming\n• Performance baseline', '• 3-5 APs migrated\n• All tests passing\n• Rollback procedure validated', 'Test environment, test devices'],
        ]

        phase1_table = Table(phase1_timeline, colWidths=[0.6*inch, 2.5*inch, 2*inch, 1.4*inch])
        phase1_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6200EE')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(phase1_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Phase 2: Production Rollout
        elements.append(Paragraph("Phase 2: Production Rollout (Weeks 5-8)", self.styles['SubsectionHeader']))

        phase2_timeline = [
            ['Week', 'Tasks', 'Success Criteria', 'Rollback Plan'],
            ['5-6', 'Site-by-site migration\n• Priority sites first\n• Monitor 48hrs each\n• Document issues', '• 25-50% APs migrated\n• Zero critical issues\n• User satisfaction maintained', 'Re-add APs to XIQ if issues'],
            ['7-8', 'Remaining sites\n• Bulk onboarding\n• Performance monitoring\n• User support', '• 100% APs migrated\n• XIQ decommissioned\n• Documentation complete', 'Edge Services rollback if widespread issues'],
        ]

        phase2_table = Table(phase2_timeline, colWidths=[0.6*inch, 2.8*inch, 2*inch, 1.1*inch])
        phase2_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#018786')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(phase2_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Phase 3: NGC Migration (Future)
        elements.append(Paragraph("Phase 3: NGC Migration (Months 3-6, Optional)", self.styles['SubsectionHeader']))

        phase3_timeline = [
            ['Month', 'Tasks', 'Benefits Realized', 'Requirements'],
            ['3', 'NGC Assessment\n• Evaluate Extreme Platform ONE\n• Design org hierarchy\n• Plan templates', '• Cloud management capability\n• Multi-site visibility\n• Automation foundation', 'Extreme Platform ONE license, Network access'],
            ['4', 'NGC Setup\n• Deploy Platform ONE\n• Create organizations\n• Define site variables\n• Build templates', '• Centralized management\n• Template library\n• Site-specific configs', 'Admin training on NGC concepts'],
            ['5', 'Migration to NGC\n• Convert Edge configs to templates\n• Assign sites\n• Deploy templates\n• Validate', '• Template-based config\n• Reduced manual work\n• Consistent deployments', 'Maintenance window for config push'],
            ['6', 'Optimization\n• Tune site variables\n• Expand templates\n• Enable assurance\n• API automation', '• Full NGC benefits\n• Zero-touch provisioning\n• Advanced analytics\n• Programmatic control', 'API integration development'],
        ]

        phase3_table = Table(phase3_timeline, colWidths=[0.6*inch, 2.4*inch, 2.1*inch, 1.4*inch])
        phase3_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F57C00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(phase3_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Final Recommendations
        elements.append(Paragraph("Strategic Recommendations", self.styles['SubsectionHeader']))

        elements.append(Paragraph(
            "<b>1. Don't Skip Edge Services:</b> Even if NGC is the end goal, migrating to Edge Services first "
            "provides a stable intermediate state and validates your network design.<br/><br/>"

            "<b>2. Start Small, Scale Fast:</b> Begin with pilot sites, but once validated, scale quickly to "
            "avoid managing dual systems (XIQ + Edge Services) for extended periods.<br/><br/>"

            "<b>3. Document Everything:</b> This PDF is your baseline. Document any deviations, custom configs, "
            "or site-specific requirements during migration.<br/><br/>"

            "<b>4. Plan for NGC from Day 1:</b> When designing Edge Services profiles and naming conventions, "
            "consider how they'll map to NGC templates. Use consistent, descriptive names.<br/><br/>"

            "<b>5. Training is Critical:</b> NGC introduces new concepts (templates, site variables, hierarchy). "
            "Budget time for admin training before Phase 3.<br/><br/>"

            "<b>6. Leverage Automation:</b> Both Edge Services and NGC have comprehensive REST APIs. Automate "
            "repetitive tasks early to reduce errors and save time.",
            self.styles['Normal']
        ))

        return elements
