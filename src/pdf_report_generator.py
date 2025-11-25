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
