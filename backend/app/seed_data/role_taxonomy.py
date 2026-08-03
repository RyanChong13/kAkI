"""Role/task taxonomy for the career redesign tool.

Each role lists its core tasks so the LLM can reason about which tasks
are AI-augmentable, automatable, or transformable.  This is a bootstrap
taxonomy — it should be refined with real usage data and manual review
over time.

Roles are organised by ``category`` to power a grouped dropdown in the UI.
"""

ROLE_TAXONOMY: list[dict] = [
    # ── Technology & IT ───────────────────────────────────────────────
    {"id": "software-engineer", "title": "Software Engineer", "category": "Technology & IT",
     "core_tasks": ["Write and maintain application code", "Review pull requests and debug issues",
                    "Design software architecture and APIs", "Collaborate with product and QA teams",
                    "Deploy and monitor applications in production"]},
    {"id": "data-analyst", "title": "Data Analyst", "category": "Technology & IT",
     "core_tasks": ["Query databases to extract business data", "Build dashboards and visual reports",
                    "Clean and validate datasets", "Identify trends and present insights to stakeholders",
                    "Automate recurring reporting workflows"]},
    {"id": "data-scientist", "title": "Data Scientist", "category": "Technology & IT",
     "core_tasks": ["Build and train predictive models", "Perform exploratory data analysis",
                    "Deploy ML models to production", "Communicate findings to non-technical stakeholders",
                    "Experiment with new algorithms and techniques"]},
    {"id": "cybersecurity-analyst", "title": "Cybersecurity Analyst", "category": "Technology & IT",
     "core_tasks": ["Monitor security alerts and SIEM dashboards", "Investigate and respond to incidents",
                    "Conduct vulnerability assessments and pentests", "Review and update security policies",
                    "Educate staff on security best practices"]},
    {"id": "cloud-engineer", "title": "Cloud Engineer", "category": "Technology & IT",
     "core_tasks": ["Provision and manage cloud infrastructure", "Implement CI/CD pipelines",
                    "Monitor cloud costs and performance", "Troubleshoot infrastructure issues",
                    "Design scalable and resilient architectures"]},
    {"id": "devops-engineer", "title": "DevOps Engineer", "category": "Technology & IT",
     "core_tasks": ["Maintain CI/CD pipelines and automation", "Manage containerised deployments",
                    "Monitor system health and uptime", "Implement infrastructure as code",
                    "Support development teams with tooling"]},
    {"id": "it-support-specialist", "title": "IT Support Specialist", "category": "Technology & IT",
     "core_tasks": ["Resolve hardware and software support tickets", "Set up and configure workstations",
                    "Manage user accounts and access permissions", "Troubleshoot network connectivity issues",
                    "Maintain IT inventory and documentation"]},
    {"id": "network-engineer", "title": "Network Engineer", "category": "Technology & IT",
     "core_tasks": ["Design and configure network infrastructure", "Monitor network performance and uptime",
                    "Troubleshoot network outages", "Implement network security measures",
                    "Plan network capacity and upgrades"]},
    {"id": "ux-ui-designer", "title": "UX/UI Designer", "category": "Technology & IT",
     "core_tasks": ["Conduct user research and interviews", "Create wireframes and prototypes",
                    "Design user interfaces in Figma", "Run usability testing sessions",
                    "Collaborate with developers on implementation"]},
    {"id": "product-manager", "title": "Product Manager", "category": "Technology & IT",
     "core_tasks": ["Define product roadmap and priorities", "Gather and analyse user feedback",
                    "Write product requirements documents", "Coordinate with engineering and design teams",
                    "Track product metrics and KPIs"]},
    {"id": "business-analyst", "title": "Business Analyst", "category": "Technology & IT",
     "core_tasks": ["Gather and document business requirements", "Analyse business processes and workflows",
                    "Create functional specifications for IT projects", "Facilitate stakeholder workshops",
                    "Support user acceptance testing"]},
    {"id": "ai-ml-engineer", "title": "AI/ML Engineer", "category": "Technology & IT",
     "core_tasks": ["Design and train machine learning models", "Build data pipelines for ML workflows",
                    "Deploy and monitor models in production", "Fine-tune LLMs for specific use cases",
                    "Evaluate model performance and bias"]},
    {"id": "full-stack-developer", "title": "Full Stack Developer", "category": "Technology & IT",
     "core_tasks": ["Build frontend interfaces with React/Vue", "Develop backend APIs and services",
                    "Manage databases and data models", "Integrate third-party services and APIs",
                    "Optimise application performance"]},
    {"id": "mobile-app-developer", "title": "Mobile App Developer", "category": "Technology & IT",
     "core_tasks": ["Build iOS/Android applications", "Integrate with backend APIs",
                    "Optimise app performance and battery usage", "Implement push notifications and in-app purchases",
                    "Publish apps to App Store and Google Play"]},
    {"id": "qa-test-engineer", "title": "QA/Test Engineer", "category": "Technology & IT",
     "core_tasks": ["Write and execute test plans and test cases", "Automate regression tests",
                    "Report and track software defects", "Perform load and performance testing",
                    "Ensure release quality standards"]},

    # ── Finance & Accounting ──────────────────────────────────────────
    {"id": "accountant", "title": "Accountant", "category": "Finance & Accounting",
     "core_tasks": ["Prepare financial statements and reports", "Manage accounts payable and receivable",
                    "Reconcile bank and ledger accounts", "Ensure compliance with tax regulations",
                    "Support audit processes"]},
    {"id": "financial-analyst", "title": "Financial Analyst", "category": "Finance & Accounting",
     "core_tasks": ["Build financial models and forecasts", "Analyse company performance and trends",
                    "Prepare investment recommendations", "Monitor market conditions and risks",
                    "Present findings to management"]},
    {"id": "auditor", "title": "Auditor", "category": "Finance & Accounting",
     "core_tasks": ["Plan and execute audit engagements", "Test internal controls and financial records",
                    "Identify compliance issues and risks", "Prepare audit reports and recommendations",
                    "Follow up on remediation actions"]},
    {"id": "tax-specialist", "title": "Tax Specialist", "category": "Finance & Accounting",
     "core_tasks": ["Prepare and file tax returns", "Advise on tax planning strategies",
                    "Monitor changes in tax legislation", "Liaise with tax authorities",
                    "Conduct tax risk assessments"]},
    {"id": "bank-officer", "title": "Bank Officer", "category": "Finance & Accounting",
     "core_tasks": ["Process customer transactions and applications", "Assess loan and credit applications",
                    "Provide product advice to customers", "Resolve customer complaints",
                    "Ensure KYC and AML compliance"]},
    {"id": "investment-analyst", "title": "Investment Analyst", "category": "Finance & Accounting",
     "core_tasks": ["Research and evaluate investment opportunities", "Build valuation models",
                    "Monitor portfolio performance", "Prepare investment memos and presentations",
                    "Track industry and macroeconomic trends"]},
    {"id": "payroll-specialist", "title": "Payroll Specialist", "category": "Finance & Accounting",
     "core_tasks": ["Process monthly payroll for employees", "Calculate CPF contributions and taxes",
                    "Maintain payroll records and reports", "Handle payroll enquiries from staff",
                    "Ensure compliance with employment laws"]},

    # ── Marketing & Communications ────────────────────────────────────
    {"id": "digital-marketer", "title": "Digital Marketer", "category": "Marketing & Communications",
     "core_tasks": ["Plan and execute digital marketing campaigns", "Manage social media channels and content",
                    "Run paid advertising on Google and Meta", "Analyse campaign performance metrics",
                    "Optimise conversion funnels"]},
    {"id": "content-writer", "title": "Content Writer", "category": "Marketing & Communications",
     "core_tasks": ["Write blog posts, articles, and marketing copy", "Research topics and keywords",
                    "Edit and proofread content", "Optimise content for SEO",
                    "Collaborate with designers on visual content"]},
    {"id": "social-media-manager", "title": "Social Media Manager", "category": "Marketing & Communications",
     "core_tasks": ["Create and schedule social media posts", "Engage with followers and manage communities",
                    "Analyse social media metrics", "Run social media ad campaigns",
                    "Monitor brand sentiment online"]},
    {"id": "pr-executive", "title": "PR Executive", "category": "Marketing & Communications",
     "core_tasks": ["Draft press releases and media kits", "Build relationships with journalists",
                    "Organise press events and media briefings", "Monitor media coverage",
                    "Manage crisis communications"]},
    {"id": "brand-manager", "title": "Brand Manager", "category": "Marketing & Communications",
     "core_tasks": ["Develop and execute brand strategy", "Manage brand guidelines and identity",
                    "Plan brand campaigns and activations", "Conduct market research on brand perception",
                    "Coordinate with creative and marketing teams"]},
    {"id": "seo-specialist", "title": "SEO Specialist", "category": "Marketing & Communications",
     "core_tasks": ["Conduct keyword research and analysis", "Optimise on-page and technical SEO",
                    "Build backlinks and monitor link profile", "Track search rankings and organic traffic",
                    "Report on SEO performance"]},
    {"id": "graphic-designer", "title": "Graphic Designer", "category": "Marketing & Communications",
     "core_tasks": ["Create visual designs for digital and print", "Design marketing collateral and social media assets",
                    "Work with brand guidelines", "Prepare files for production",
                    "Collaborate with marketing and product teams"]},

    # ── Business & Administration ─────────────────────────────────────
    {"id": "hr-executive", "title": "HR Executive", "category": "Business & Administration",
     "core_tasks": ["Manage recruitment and onboarding", "Handle employee relations and grievances",
                    "Administer payroll and benefits", "Maintain HR policies and compliance",
                    "Support performance management processes"]},
    {"id": "admin-officer", "title": "Admin Officer", "category": "Business & Administration",
     "core_tasks": ["Manage office operations and supplies", "Handle correspondence and filings",
                    "Coordinate meetings and schedules", "Maintain administrative records",
                    "Support other departments with admin tasks"]},
    {"id": "operations-manager", "title": "Operations Manager", "category": "Business & Administration",
     "core_tasks": ["Oversee daily business operations", "Optimise operational processes and workflows",
                    "Manage operational budgets", "Coordinate across departments",
                    "Ensure compliance with regulations"]},
    {"id": "project-manager", "title": "Project Manager", "category": "Business & Administration",
     "core_tasks": ["Plan and scope project deliverables", "Manage project timelines and budgets",
                    "Coordinate project teams and stakeholders", "Track risks and issues",
                    "Report project status to sponsors"]},
    {"id": "office-manager", "title": "Office Manager", "category": "Business & Administration",
     "core_tasks": ["Manage office facilities and vendors", "Oversee administrative staff",
                    "Handle office budget and expenses", "Ensure workplace health and safety",
                    "Organise company events"]},
    {"id": "executive-assistant", "title": "Executive Assistant", "category": "Business & Administration",
     "core_tasks": ["Manage executive calendars and schedules", "Prepare meeting materials and minutes",
                    "Handle travel and expense arrangements", "Screen communications and requests",
                    "Support special projects"]},
    {"id": "customer-service-officer", "title": "Customer Service Officer", "category": "Business & Administration",
     "core_tasks": ["Handle customer enquiries via phone and email", "Resolve complaints and escalate issues",
                    "Process orders and returns", "Maintain customer records in CRM",
                    "Collect and report customer feedback"]},
    {"id": "sales-executive", "title": "Sales Executive", "category": "Business & Administration",
     "core_tasks": ["Generate and qualify sales leads", "Conduct product demos and presentations",
                    "Negotiate and close deals", "Maintain CRM records and pipeline",
                    "Build and maintain client relationships"]},

    # ── Healthcare ────────────────────────────────────────────────────
    {"id": "registered-nurse", "title": "Registered Nurse", "category": "Healthcare",
     "core_tasks": ["Provide direct patient care and monitoring", "Administer medications and treatments",
                    "Document patient conditions and progress", "Coordinate with doctors and care teams",
                    "Educate patients and families on care"]},
    {"id": "healthcare-administrator", "title": "Healthcare Administrator", "category": "Healthcare",
     "core_tasks": ["Manage clinic or hospital operations", "Oversee staff scheduling and rosters",
                    "Handle patient feedback and complaints", "Ensure regulatory compliance",
                    "Manage healthcare budgets and procurement"]},
    {"id": "medical-technologist", "title": "Medical Technologist", "category": "Healthcare",
     "core_tasks": ["Perform laboratory tests and analyses", "Operate and maintain lab equipment",
                    "Quality control and calibration of instruments", "Record and report test results",
                    "Ensure lab safety and compliance"]},
    {"id": "pharmacy-technician", "title": "Pharmacy Technician", "category": "Healthcare",
     "core_tasks": ["Prepare and dispense medications", "Manage pharmacy inventory",
                    "Process prescriptions and insurance claims", "Assist pharmacists with patient counselling",
                    "Maintain pharmacy records"]},
    {"id": "allied-health-professional", "title": "Allied Health Professional", "category": "Healthcare",
     "core_tasks": ["Assess and treat patients", "Develop care plans",
                    "Conduct therapy sessions", "Document patient progress",
                    "Collaborate with multidisciplinary teams"]},
    {"id": "care-coordinator", "title": "Care Coordinator", "category": "Healthcare",
     "core_tasks": ["Coordinate patient care across providers", "Schedule appointments and follow-ups",
                    "Communicate with patients and families", "Maintain care plans and records",
                    "Liaise with community resources"]},

    # ── Manufacturing & Engineering ───────────────────────────────────
    {"id": "mechanical-engineer", "title": "Mechanical Engineer", "category": "Manufacturing & Engineering",
     "core_tasks": ["Design mechanical systems and components", "Run simulations and stress analysis",
                    "Prepare technical drawings and specifications", "Oversee manufacturing processes",
                    "Troubleshoot mechanical failures"]},
    {"id": "electrical-engineer", "title": "Electrical Engineer", "category": "Manufacturing & Engineering",
     "core_tasks": ["Design electrical systems and circuits", "Perform load calculations and power studies",
                    "Oversee installation and commissioning", "Conduct safety inspections",
                    "Maintain electrical documentation"]},
    {"id": "quality-inspector", "title": "Quality Inspector", "category": "Manufacturing & Engineering",
     "core_tasks": ["Inspect products and materials for defects", "Conduct quality tests and measurements",
                    "Document inspection findings", "Identify and report quality issues",
                    "Maintain calibration of inspection tools"]},
    {"id": "production-supervisor", "title": "Production Supervisor", "category": "Manufacturing & Engineering",
     "core_tasks": ["Supervise production line operations", "Manage production schedules and targets",
                    "Ensure quality and safety standards", "Train and mentor production staff",
                    "Troubleshoot production issues"]},
    {"id": "facilities-manager", "title": "Facilities Manager", "category": "Manufacturing & Engineering",
     "core_tasks": ["Oversee building maintenance and repairs", "Manage facilities budget and vendors",
                    "Ensure workplace safety compliance", "Coordinate renovations and upgrades",
                    "Manage security and access systems"]},

    # ── Retail & Hospitality ──────────────────────────────────────────
    {"id": "retail-store-manager", "title": "Retail Store Manager", "category": "Retail & Hospitality",
     "core_tasks": ["Manage store operations and staff", "Oversee inventory and visual merchandising",
                    "Drive sales targets and KPIs", "Handle customer complaints", "Manage store budget and P&L"]},
    {"id": "fnb-supervisor", "title": "F&B Supervisor", "category": "Retail & Hospitality",
     "core_tasks": ["Supervise restaurant service operations", "Manage staff scheduling and training",
                    "Ensure food safety and hygiene standards", "Handle customer feedback",
                    "Monitor inventory and supplies"]},
    {"id": "hotel-front-desk-officer", "title": "Hotel Front Desk Officer", "category": "Retail & Hospitality",
     "core_tasks": ["Check in and check out guests", "Handle reservations and enquiries",
                    "Resolve guest complaints", "Process payments", "Coordinate with housekeeping and concierge"]},
    {"id": "tour-guide", "title": "Tour Guide", "category": "Retail & Hospitality",
     "core_tasks": ["Lead guided tours and share local knowledge", "Ensure tourist safety and comfort",
                    "Manage tour logistics and timing", "Handle tourist enquiries", "Promote local attractions"]},
    {"id": "event-coordinator", "title": "Event Coordinator", "category": "Retail & Hospitality",
     "core_tasks": ["Plan and execute events", "Coordinate vendors and suppliers",
                    "Manage event budgets", "Handle guest registrations", "Ensure event safety compliance"]},

    # ── Education & Training ──────────────────────────────────────────
    {"id": "teacher", "title": "Teacher", "category": "Education & Training",
     "core_tasks": ["Plan and deliver lessons", "Assess and grade student work",
                    "Manage classroom behaviour", "Communicate with parents", "Develop curriculum materials"]},
    {"id": "training-coordinator", "title": "Training Coordinator", "category": "Education & Training",
     "core_tasks": ["Plan and schedule training programmes", "Coordinate with trainers and venues",
                    "Manage training materials and LMS", "Track attendance and completion", "Evaluate training effectiveness"]},
    {"id": "curriculum-developer", "title": "Curriculum Developer", "category": "Education & Training",
     "core_tasks": ["Design course curricula and learning materials", "Develop assessments and rubrics",
                    "Align content with learning outcomes", "Incorporate educational technology",
                    "Review and update existing curricula"]},

    # ── Logistics & Supply Chain ──────────────────────────────────────
    {"id": "warehouse-manager", "title": "Warehouse Manager", "category": "Logistics & Supply Chain",
     "core_tasks": ["Oversee warehouse operations and inventory", "Manage receiving and dispatch",
                    "Optimise storage and layout", "Supervise warehouse staff", "Ensure safety compliance"]},
    {"id": "procurement-officer", "title": "Procurement Officer", "category": "Logistics & Supply Chain",
     "core_tasks": ["Source and evaluate suppliers", "Negotiate contracts and pricing",
                    "Process purchase orders", "Monitor supplier performance", "Manage procurement budget"]},
    {"id": "supply-chain-analyst", "title": "Supply Chain Analyst", "category": "Logistics & Supply Chain",
     "core_tasks": ["Analyse supply chain data and metrics", "Forecast demand and inventory needs",
                    "Identify supply chain risks", "Optimise logistics routes and costs",
                    "Build supply chain dashboards"]},
    {"id": "logistics-coordinator", "title": "Logistics Coordinator", "category": "Logistics & Supply Chain",
     "core_tasks": ["Coordinate shipments and deliveries", "Manage freight forwarders and carriers",
                    "Track shipments and resolve delays", "Prepare shipping documents", "Optimise delivery routes"]},

    # ── Construction & Built Environment ───────────────────────────────
    {"id": "civil-engineer", "title": "Civil Engineer", "category": "Construction & Built Environment",
     "core_tasks": ["Design and supervise construction projects", "Conduct site inspections",
                    "Prepare engineering calculations and drawings", "Manage project budgets and timelines",
                    "Ensure building code compliance"]},
    {"id": "quantity-surveyor", "title": "Quantity Surveyor", "category": "Construction & Built Environment",
     "core_tasks": ["Estimate project costs and prepare bills of quantities", "Manage tender processes",
                    "Track project costs and variations", "Conduct cost analysis and reporting",
                    "Administer contracts and claims"]},
    {"id": "safety-officer", "title": "Workplace Safety Officer", "category": "Construction & Built Environment",
     "core_tasks": ["Conduct safety inspections and audits", "Investigate accidents and incidents",
                    "Develop safety procedures and toolbox talks", "Ensure WSH compliance",
                    "Train staff on safety practices"]},
]


def list_roles() -> list[dict]:
    """Return all roles in the taxonomy."""
    return ROLE_TAXONOMY


def list_categories() -> list[str]:
    """Return distinct category names, sorted."""
    return sorted({r["category"] for r in ROLE_TAXONOMY})


def get_role(role_id_or_title: str) -> dict | None:
    """Look up a role by its id (exact) or title (case-insensitive)."""
    key = role_id_or_title.strip().lower()
    for r in ROLE_TAXONOMY:
        if r["id"].lower() == key or r["title"].lower() == key:
            return r
    return None


def search_roles(query: str, limit: int = 10) -> list[dict]:
    """Fuzzy-search roles by title or category."""
    q = query.strip().lower()
    if not q:
        return ROLE_TAXONOMY[:limit]
    scored: list[tuple[int, dict]] = []
    for r in ROLE_TAXONOMY:
        title_l = r["title"].lower()
        cat_l = r["category"].lower()
        if title_l == q:
            scored.append((100, r))
        elif title_l.startswith(q):
            scored.append((80, r))
        elif q in title_l:
            scored.append((60, r))
        elif q in cat_l:
            scored.append((40, r))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [r for _, r in scored[:limit]]
