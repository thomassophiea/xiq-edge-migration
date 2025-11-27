# References & Documentation Links

## Project Repositories

### Primary Projects
- **XIQ Edge Migration Tool**
  - GitHub: https://github.com/thomassophiea/xiq-edge-migration
  - Railway Deployment: [Your Railway URL]
  - Local Development: `http://localhost:5000`

- **Edge Services Site**
  - GitHub: https://github.com/thomassophiea/edge-services-site
  - [Your deployment URL if applicable]

## Official API Documentation

### ExtremeCloud IQ (XIQ)
- **Main API Documentation**
  - Base URL: https://api.extremecloudiq.com
  - API Docs: https://extremecloudiq.com/api-docs/
  - Developer Portal: https://developer.aerohive.com/
  - API Swagger UI: https://api.extremecloudiq.com/swagger-ui/

- **Regional Endpoints**
  - Global: https://api.extremecloudiq.com
  - EU: https://api-eu.extremecloudiq.com
  - APAC: https://api-apac.extremecloudiq.com
  - California: https://api-ca.extremecloudiq.com

- **Authentication**
  - OAuth 2.0 Documentation: https://extremecloudiq.com/api-docs/#section/Authentication
  - Token Management: XIQ Global Settings > API Token Management

### Extreme Edge Services
- **API Documentation**
  - Default Port: 5825
  - Base Path: `/management`
  - API Version: v5.26
  - Endpoints: `/management/v1/*` and `/management/v3/*`

- **Key Endpoints**
  - OAuth Token: `/management/v1/oauth2/token`
  - Services (SSIDs): `/management/v1/services`
  - Topologies (VLANs): `/management/v1/topologies`
  - AAA Policies: `/management/v1/aaapolicy`
  - Associated Profiles: `/management/v3/profiles`
  - Access Points: `/management/v1/aps`
  - Rate Limiters: `/management/v1/ratelimiters`
  - CoS Policies: `/management/v1/cos`

- **Official Resources**
  - Extreme Networks Documentation Portal: https://documentation.extremenetworks.com/
  - Edge Services Admin Guide: https://documentation.extremenetworks.com/edge/
  - Release Notes: https://documentation.extremenetworks.com/release_notes/

## Technology Stack Documentation

### Backend - Python/Flask
- **Flask Framework**
  - Official Docs: https://flask.palletsprojects.com/
  - Quickstart: https://flask.palletsprojects.com/quickstart/
  - API Reference: https://flask.palletsprojects.com/api/

- **Flask Extensions**
  - Flask-CORS: https://flask-cors.readthedocs.io/
  - Session Management: https://flask.palletsprojects.com/sessions/

- **Python Libraries**
  - Requests: https://requests.readthedocs.io/
  - ReportLab (PDF): https://www.reportlab.com/docs/reportlab-userguide.pdf
  - UUID: https://docs.python.org/3/library/uuid.html
  - Threading: https://docs.python.org/3/library/threading.html
  - Collections (deque): https://docs.python.org/3/library/collections.html

### Frontend - JavaScript/HTML/CSS
- **JavaScript**
  - MDN Web Docs: https://developer.mozilla.org/en-US/docs/Web/JavaScript
  - Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
  - LocalStorage: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

- **HTML5**
  - MDN HTML Reference: https://developer.mozilla.org/en-US/docs/Web/HTML
  - Semantic HTML: https://developer.mozilla.org/en-US/docs/Glossary/Semantics#semantics_in_html

- **CSS3**
  - MDN CSS Reference: https://developer.mozilla.org/en-US/docs/Web/CSS
  - CSS Variables: https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
  - Flexbox: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout
  - Grid: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout

- **Material Design**
  - Material Design 3: https://m3.material.io/
  - Color System: https://m3.material.io/styles/color/system/overview
  - Components: https://m3.material.io/components

## Deployment & DevOps

### Railway
- **Platform Documentation**
  - Railway Docs: https://docs.railway.app/
  - Deploy from GitHub: https://docs.railway.app/deploy/deployments
  - Environment Variables: https://docs.railway.app/develop/variables
  - Custom Domains: https://docs.railway.app/deploy/exposing-your-app

### Git/GitHub
- **Version Control**
  - Git Documentation: https://git-scm.com/doc
  - GitHub Guides: https://guides.github.com/
  - GitHub Actions: https://docs.github.com/en/actions

## Project Documentation (Local)

### Created Documentation
- `README.md` - Project overview and setup instructions
- `ARCHITECTURE_DIAGRAM.md` - Visual architecture diagrams
- `DEPLOYMENT.md` - Deployment instructions
- `REFERENCES.md` - This file
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies (if applicable)

### Code Documentation
- `src/config.py` - Configuration constants
- `src/xiq_api_client.py` - XIQ API client with docstrings
- `src/campus_controller_client.py` - Edge Services client with docstrings
- `src/config_converter.py` - Configuration converter with docstrings
- `src/pdf_report_generator.py` - PDF generator with docstrings
- `web_ui.py` - Flask routes and endpoints

## Networking & Security Standards

### OAuth 2.0
- **Specification**
  - RFC 6749: https://datatracker.ietf.org/doc/html/rfc6749
  - OAuth 2.0 Guide: https://oauth.net/2/

### Wireless Standards
- **IEEE 802.11**
  - 802.11 Standards: https://www.ieee802.org/11/
  - WPA2/WPA3: https://www.wi-fi.org/discover-wi-fi/security
  - 802.1X: https://1.ieee802.org/security/802-1x/

### REST API Best Practices
- **RESTful API Design**
  - REST API Tutorial: https://restfulapi.net/
  - HTTP Status Codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
  - JSON:API: https://jsonapi.org/

## Helpful Tools & Resources

### Development Tools
- **VS Code**
  - Download: https://code.visualstudio.com/
  - Python Extension: https://marketplace.visualstudio.com/items?itemName=ms-python.python
  - Markdown PDF: https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf

- **API Testing**
  - Postman: https://www.postman.com/
  - Insomnia: https://insomnia.rest/
  - curl Documentation: https://curl.se/docs/

### Code Quality
- **Python**
  - PEP 8 Style Guide: https://peps.python.org/pep-0008/
  - Black Formatter: https://black.readthedocs.io/
  - Pylint: https://pylint.pycqa.org/

- **JavaScript**
  - ESLint: https://eslint.org/
  - Prettier: https://prettier.io/
  - Airbnb Style Guide: https://github.com/airbnb/javascript

## Learning Resources

### Flask Development
- **Tutorials**
  - Flask Mega-Tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
  - Real Python Flask: https://realpython.com/tutorials/flask/
  - Flask by Example: https://www.flaskapi.org/

### REST API Development
- **Guides**
  - Building REST APIs with Flask: https://realpython.com/flask-connexion-rest-api/
  - REST API Tutorial: https://www.restapitutorial.com/
  - API Design Patterns: https://cloud.google.com/apis/design

### Network Automation
- **Resources**
  - Network Automation: https://pynet.twb-tech.com/
  - NAPALM: https://napalm.readthedocs.io/
  - Netmiko: https://github.com/ktbyers/netmiko

## Support & Community

### Extreme Networks
- **Support Portal**
  - Support: https://extremeportal.force.com/ExtrSupportHome
  - Community Forums: https://community.extremenetworks.com/
  - Knowledge Base: https://extremeportal.force.com/ExtrArticleList

### Stack Overflow Tags
- `#flask` - https://stackoverflow.com/questions/tagged/flask
- `#python` - https://stackoverflow.com/questions/tagged/python
- `#rest-api` - https://stackoverflow.com/questions/tagged/rest-api
- `#oauth-2.0` - https://stackoverflow.com/questions/tagged/oauth-2.0

## Report Issues

### Project Issues
- GitHub Issues (XIQ Migration): https://github.com/thomassophiea/xiq-edge-migration/issues
- GitHub Issues (Edge Services Site): https://github.com/thomassophiea/edge-services-site/issues

## Additional Resources

### PDF Generation
- **ReportLab**
  - User Guide: https://www.reportlab.com/docs/reportlab-userguide.pdf
  - API Reference: https://www.reportlab.com/documentation/
  - Examples: https://github.com/MrBitBucket/reportlab-mirror

### Web Security
- **OWASP**
  - Top 10: https://owasp.org/www-project-top-ten/
  - CSRF Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
  - Session Management: https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html

### Performance Optimization
- **Web Performance**
  - Google Web Fundamentals: https://developers.google.com/web/fundamentals/performance
  - MDN Performance: https://developer.mozilla.org/en-US/docs/Web/Performance

## Version Information

- **Python Version**: 3.8+
- **Flask Version**: 2.3.0+
- **Edge Services API**: v5.26
- **XIQ API**: Latest (OAuth 2.0)

---

**Last Updated**: November 26, 2024
**Maintainer**: Thomas Sophiea
**License**: [Your License Here]
