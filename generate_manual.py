
import os
import asyncio
from playwright.async_api import async_playwright

import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Paths to screenshots
SCREENSHOT_PATHS = {
    "dashboard": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_dashboard_1775529097427.png",
    "features": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_features_1775529107736.png",
    "policies": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_policies_1775529119559.png",
    "events": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_events_1775529130074.png",
    "projects": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_projects_1775529141742.png",
    "knowledge": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_knowledge_1775529152781.png",
    "brochures": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_brochures_1775529164771.png",
    "livelihood": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_livelihood_feeds_1775529176466.png",
    "org": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_org_structure_1775529188145.png",
    "committee": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_committee_1775529199795.png",
    "tracking": r"C:\Users\Administrator\.gemini\antigravity\brain\f13b0cfb-6def-4e14-815d-a5e87357b6c8\admin_tracking_matrix_1775529211409.png"
}

SCREENSHOTS = {k: f"data:image/png;base64,{get_base64_image(v)}" for k, v in SCREENSHOT_PATHS.items() if os.path.exists(v)}


HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GAD Corner Admin Manual</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Outfit:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #6366f1;
            --secondary: #ec4899;
            --accent: #8b5cf6;
            --dark: #1e293b;
            --text: #334155;
            --light: #f8fafc;
            --border: #e2e8f0;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            color: var(--text);
            margin: 0;
            padding: 0;
            background: white;
            font-size: 11pt;
        }}
        .page {{
            padding: 1in;
            width: 100%;
            min-height: 10in;
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
        }}
        .page:not(:first-child) {{
            page-break-before: always;
        }}
        /* Corner accent */
        .page::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 8px;
            height: 100%;
            background: linear-gradient(to bottom, var(--primary), var(--accent));
        }}
        h1, h2, h3 {{
            font-family: 'Outfit', sans-serif;
            color: var(--dark);
            page-break-after: avoid;
        }}
        h1 {{
            font-size: 48pt;
            margin-top: 1.5in;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        h2 {{
            font-size: 24pt;
            border-bottom: 2px solid var(--border);
            padding-bottom: 8pt;
            margin-top: 40pt;
            color: var(--primary);
        }}
        h3 {{
            font-size: 16pt;
            margin-top: 25pt;
            color: var(--dark);
        }}
        .cover {{
            text-align: center;
            height: 10in;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: radial-gradient(circle at 10% 10%, #eff6ff 0%, #ffffff 100%);
        }}
        .cover::before {{ display: none; }}
        .toc {{
            background: var(--light);
            padding: 30pt;
            border-radius: 12pt;
            border: 1pt solid var(--border);
        }}
        .figure {{
            margin: 30pt 0;
            text-align: center;
            page-break-inside: avoid;
        }}
        .figure img {{
            width: 95%;
            max-width: 7.5in;
            border-radius: 8pt;
            box-shadow: 0 4pt 20pt rgba(0,0,0,0.08);
            border: 1pt solid var(--border);
        }}
        .figure-caption {{
            font-size: 9pt;
            color: #64748b;
            margin-top: 10pt;
            font-weight: 500;
        }}
        .info-box {{
            background: #f0f9ff;
            padding: 20pt;
            border-radius: 10pt;
            border-left: 5pt solid var(--primary);
            margin: 20pt 0;
        }}
        ul {{ padding-left: 20pt; }}
        li {{ margin-bottom: 6pt; }}
        code {{
            background: #f1f5f9;
            padding: 3pt 6pt;
            border-radius: 4pt;
            color: #d63384;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="page cover">
        <div style="font-size: 0.9rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em; color: var(--primary); margin-bottom: 20px;">Official Document</div>
        <h1>GAD Corner</h1>
        <p>Administrative User Manual</p>
        <div style="margin-top: 80px; text-align: center;">
            <div style="font-weight: 600; color: var(--dark);">Municipality of Montalban (Rodriguez), Rizal</div>
            <div style="color: #64748b; margin-top: 8px;">Version 1.0 • April 2026</div>
        </div>
    </div>

    <div class="page">
        <h2>Table of Contents</h2>
        <div class="toc">
            <ul>
                <li>1. Introduction</li>
                <li>2. Authentication & Access</li>
                <li>3. Dashboard Overview</li>
                <li>4. Site Features & Scraper</li>
                <li>5. Policies Management</li>
                <li>6. Calendar & Events</li>
                <li>7. Project Archives</li>
                <li>8. Knowledge Products & Brochures</li>
                <li>9. Livelihood Program Feeds</li>
                <li>10. Org Structure & Committee</li>
                <li>11. Tracking Matrix</li>
            </ul>
        </div>
    </div>

    <div class="page">
        <h2>1. Introduction</h2>
        <p>The <strong>GAD Corner Admin Panel</strong> is your central hub for managing the Gender and Development platform. This manual provides a step-by-step guide on how to update content, manage users, and monitor application health.</p>
        
        <div class="info-box">
            <strong>Key Support Formats:</strong>
            <ul>
                <li><strong>Images:</strong> PNG, JPG, WEBP, GIF (Max 5MB)</li>
                <li><strong>Documents:</strong> PDF, DOCX, DOC</li>
                <li><strong>Media:</strong> MP4, WEBM, OGG</li>
            </ul>
        </div>

        <h3>1.1 Interface Philosophy</h3>
        <p>The interface is designed to be mobile-responsive and intuitive. Navigation is handled via the sidebar on the left, while actions like "Add" or "Edit" typically happen within distinct modals or dedicated forms.</p>
    </div>

    <div class="page">
        <h2>2. Authentication & Access</h2>
        <p>Security is paramount. Only authorized technical officers should possess administrative credentials.</p>
        
        <h3>2.1 Login Portal</h3>
        <p>Access the portal at <code>/admin/login</code>. Enter your username and password as configured in the system environment.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['dashboard']}" alt="Dashboard">
            <div class="figure-caption">Figure 1: The Administrative Dashboard Interface</div>
        </div>
    </div>

    <div class="page">
        <h2>3. Dashboard Overview</h2>
        <p>Upon successful login, you are presented with the Dashboard. This page highlights active events and system counts.</p>
        <ul>
            <li><strong>Total Events:</strong> Lifetime count of events.</li>
            <li><strong>Upcoming:</strong> Events scheduled for future dates.</li>
            <li><strong>This Month:</strong> Activities specifically for the current period.</li>
        </ul>
        <p>The "Upcoming List" allows you to quickly verify the next 5 programmed activities without leaving the home screen.</p>
    </div>

    <div class="page">
        <h2>4. Site Features & Scraper</h2>
        <p>Use the **Features** tab to manage the public-facing homepage and automated background tasks.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['features']}" alt="Features">
            <div class="figure-caption">Figure 2: Site Features and Scraper Configuration</div>
        </div>

        <h3>4.1 Home Carousel</h3>
        <p>Add URLs of high-quality images to appear in the homepage slider. Note that the order is strictly enforced by the "Order" index.</p>
        
        <h3>4.2 News Scraper</h3>
        <p>The system includes a Playwright-based scraper. You can set it to run at low-traffic hours (e.g., 02:00 AM) to keep the "GAD News" section fresh with the latest developments from external sources.</p>
    </div>

    <div class="page">
        <h2>5. Policies Management</h2>
        <p>The Policies module manages all legal and administrative documents relevant to GAD.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['policies']}" alt="Policies">
            <div class="figure-caption">Figure 3: Policy Repository Management</div>
        </div>

        <h3>5.1 Adding a Policy</h3>
        <p>When adding a policy, ensure the category is correct (Circulars vs. Memos). You can upload a file directly or link to an external source. If a video explanation is available, the "Video URL" field will embed it on the public site.</p>
    </div>

    <div class="page">
        <h2>6. Calendar & Events</h2>
        <p>Manage the community calendar from this module.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['events']}" alt="Events">
            <div class="figure-caption">Figure 4: Event Scheduling Tool</div>
        </div>

        <p>Events are automatically sorted by date. Past events will remain in the database but are filtered out of the "Upcoming" views on the public site.</p>
    </div>

    <div class="page">
        <h2>7. Project Archives</h2>
        <p>The Project Archive module showcases the impact of GAD initiatives over the years.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['projects']}" alt="Projects">
            <div class="figure-caption">Figure 5: GAD Project Listing and Tracking</div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Meaning</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Ongoing</td><td>Currently being implemented.</td></tr>
                <tr><td>Completed</td><td>Fully realized projects.</td></tr>
                <tr><td>Proposed</td><td>Planned initiatives awaiting approval.</td></tr>
            </tbody>
        </table>
    </div>

    <div class="page">
        <h2>8. Knowledge Products & Brochures</h2>
        <p>These sections handle the "Resource Center" of the website.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['knowledge']}" alt="Knowledge">
            <div class="figure-caption">Figure 6: Knowledge Products Management</div>
        </div>

        <h3>8.1 Brochures</h3>
        <div class="figure">
            <img src="{SCREENSHOTS['brochures']}" alt="Brochures">
            <div class="figure-caption">Figure 7: Digital Brochures and Flyers</div>
        </div>
        <p>Upload compact flyers or brochures that citizens can download for offline reading.</p>
    </div>

    <div class="page">
        <h2>9. Livelihood Program Feeds</h2>
        <p>Bridge the gap between social media and the official portal by linking direct feeds.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['livelihood']}" alt="Livelihood">
            <div class="figure-caption">Figure 8: Social Media Feed Integration for Livelihood Projects</div>
        </div>
        
        <p>Input the URL of a Facebook post or Reel, and the system will automatically generate a secure, sanitized embed frame for the public view.</p>
    </div>

    <div class="page">
        <h2>10. Org Structure & Committee</h2>
        <p>Managed specifically for transparency in governance.</p>
        
        <h3>10.1 Organizational Chart</h3>
        <div class="figure">
            <img src="{SCREENSHOTS['org']}" alt="Org Structure">
            <div class="figure-caption">Figure 9: Hierarchy and Structure Management</div>
        </div>

        <h3>10.2 GAD Committee</h3>
        <div class="figure">
            <img src="{SCREENSHOTS['committee']}" alt="Committee">
            <div class="figure-caption">Figure 10: GFPS Committee Members</div>
        </div>
    </div>

    <div class="page">
        <h2>11. Tracking Matrix</h2>
        <p>The Tracking Matrix is your internal audit trail. It logs every action made by admin accounts.</p>
        
        <div class="figure">
            <img src="{SCREENSHOTS['tracking']}" alt="Tracking Matrix">
            <div class="figure-caption">Figure 11: Real-time Action Tracking and Audit Logs</div>
        </div>

        <p>This allows for accountability and provides a "Digital Footprint" required for official government reporting on digital asset management.</p>
    </div>

    <div class="page" style="text-align: center; justify-content: center; display: flex; flex-direction: column;">
        <h2 style="border: none;">End of Manual</h2>
        <p>For further assistance, please contact the GAD Technical Support Team.</p>
        <div style="margin-top: 50px; font-size: 0.8rem; color: #94a3b8;">
            Generated by Antigravity AI Systems<br>
            Municipality of Montalban GAD Corner Platform
        </div>
    </div>
</body>
</html>
"""

async def generate_pdf():
    async with async_playwright() as p:
        # Launch browser with specific args to allow file access if needed
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set content
        await page.set_content(HTML_CONTENT)
        
        # Wait for fonts and images to load
        # Wait until there are no network connections for 500ms
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000) # Safety buffer for renders
        
        pdf_path = os.path.join(os.getcwd(), "GAD_Admin_User_Manual.pdf")
        
        # Generate PDF with A4 format and margins
        await page.pdf(
            path=pdf_path, 
            format="A4", 
            print_background=True,
            display_header_footer=True,
            header_template='<div style="font-size: 8px; margin-left: 20px; color: #94a3b8;">GAD Corner • Admin Manual</div>',
            footer_template='<div style="font-size: 8px; margin-left: auto; margin-right: 20px; color: #94a3b8;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
            margin={"top": "60px", "right": "20px", "bottom": "60px", "left": "20px"}
        )
        
        await browser.close()
        print(f"Update: PDF with screenshots generated successfully at: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(generate_pdf())
