"""Role/task taxonomy for the career redesign tool.

Each role lists its core tasks so the LLM can reason about which tasks
are AI-augmentable, automatable, or transformable.  This is a bootstrap
taxonomy — it should be refined with real usage data and manual review
over time.

Roles are organised by ``category`` to power a grouped dropdown in the UI.

Phase 2 additions:
- ``task_keywords``: 5-12 resume-friendly skill phrases per role, used by
  the resume analyser to score skill-to-role overlap.
- ``ai_augmentable``: a heuristic 0-100 score per core task indicating how
  strongly current AI can augment or automate the task.
    High (70-100)   data processing, writing, scheduling, coding, patterns
    Medium (40-69)  analysis with judgment, design iteration, testing,
                    customer interaction
    Low (0-39)      physical work, in-person care, complex negotiation,
                    ethical/safety judgment
"""

ROLE_TAXONOMY: list[dict] = [
    # ── Technology & IT ───────────────────────────────────────────────
    {"id": "software-engineer", "title": "Software Engineer", "category": "Technology & IT",
     "task_keywords": ["coding", "programming", "debugging", "software architecture", "api design", "code review", "deployment", "testing"],
     "core_tasks": [
         {"task": "Write and maintain application code", "ai_augmentable": 85},
         {"task": "Review pull requests and debug issues", "ai_augmentable": 75},
         {"task": "Design software architecture and APIs", "ai_augmentable": 55},
         {"task": "Collaborate with product and QA teams", "ai_augmentable": 35},
         {"task": "Deploy and monitor applications in production", "ai_augmentable": 70}]},
    {"id": "data-analyst", "title": "Data Analyst", "category": "Technology & IT",
     "task_keywords": ["data analysis", "sql", "dashboards", "data visualisation", "reporting", "excel", "statistics", "data cleaning"],
     "core_tasks": [
         {"task": "Query databases to extract business data", "ai_augmentable": 85},
         {"task": "Build dashboards and visual reports", "ai_augmentable": 80},
         {"task": "Clean and validate datasets", "ai_augmentable": 85},
         {"task": "Identify trends and present insights to stakeholders", "ai_augmentable": 60},
         {"task": "Automate recurring reporting workflows", "ai_augmentable": 80}]},
    {"id": "data-scientist", "title": "Data Scientist", "category": "Technology & IT",
     "task_keywords": ["machine learning", "python", "statistics", "predictive modelling", "data analysis", "feature engineering", "model evaluation"],
     "core_tasks": [
         {"task": "Build and train predictive models", "ai_augmentable": 70},
         {"task": "Perform exploratory data analysis", "ai_augmentable": 80},
         {"task": "Deploy ML models to production", "ai_augmentable": 65},
         {"task": "Communicate findings to non-technical stakeholders", "ai_augmentable": 55},
         {"task": "Experiment with new algorithms and techniques", "ai_augmentable": 60}]},
    {"id": "cybersecurity-analyst", "title": "Cybersecurity Analyst", "category": "Technology & IT",
     "task_keywords": ["security monitoring", "incident response", "vulnerability assessment", "penetration testing", "siem", "risk assessment", "security policies"],
     "core_tasks": [
         {"task": "Monitor security alerts and SIEM dashboards", "ai_augmentable": 80},
         {"task": "Investigate and respond to incidents", "ai_augmentable": 55},
         {"task": "Conduct vulnerability assessments and pentests", "ai_augmentable": 65},
         {"task": "Review and update security policies", "ai_augmentable": 75},
         {"task": "Educate staff on security best practices", "ai_augmentable": 40}]},
    {"id": "cloud-engineer", "title": "Cloud Engineer", "category": "Technology & IT",
     "task_keywords": ["cloud infrastructure", "aws", "azure", "ci/cd", "infrastructure as code", "terraform", "cost optimisation", "scalability"],
     "core_tasks": [
         {"task": "Provision and manage cloud infrastructure", "ai_augmentable": 75},
         {"task": "Implement CI/CD pipelines", "ai_augmentable": 75},
         {"task": "Monitor cloud costs and performance", "ai_augmentable": 80},
         {"task": "Troubleshoot infrastructure issues", "ai_augmentable": 60},
         {"task": "Design scalable and resilient architectures", "ai_augmentable": 50}]},
    {"id": "devops-engineer", "title": "DevOps Engineer", "category": "Technology & IT",
     "task_keywords": ["ci/cd", "automation", "docker", "kubernetes", "monitoring", "infrastructure as code", "release management"],
     "core_tasks": [
         {"task": "Maintain CI/CD pipelines and automation", "ai_augmentable": 75},
         {"task": "Manage containerised deployments", "ai_augmentable": 70},
         {"task": "Monitor system health and uptime", "ai_augmentable": 85},
         {"task": "Implement infrastructure as code", "ai_augmentable": 75},
         {"task": "Support development teams with tooling", "ai_augmentable": 45}]},
    {"id": "it-support-specialist", "title": "IT Support Specialist", "category": "Technology & IT",
     "task_keywords": ["technical support", "troubleshooting", "helpdesk", "hardware", "windows", "user administration", "it operations"],
     "core_tasks": [
         {"task": "Resolve hardware and software support tickets", "ai_augmentable": 65},
         {"task": "Set up and configure workstations", "ai_augmentable": 45},
         {"task": "Manage user accounts and access permissions", "ai_augmentable": 80},
         {"task": "Troubleshoot network connectivity issues", "ai_augmentable": 55},
         {"task": "Maintain IT inventory and documentation", "ai_augmentable": 80}]},
    {"id": "network-engineer", "title": "Network Engineer", "category": "Technology & IT",
     "task_keywords": ["networking", "routing", "switching", "firewalls", "network security", "tcp/ip", "network monitoring"],
     "core_tasks": [
         {"task": "Design and configure network infrastructure", "ai_augmentable": 50},
         {"task": "Monitor network performance and uptime", "ai_augmentable": 85},
         {"task": "Troubleshoot network outages", "ai_augmentable": 55},
         {"task": "Implement network security measures", "ai_augmentable": 60},
         {"task": "Plan network capacity and upgrades", "ai_augmentable": 65}]},
    {"id": "ux-ui-designer", "title": "UX/UI Designer", "category": "Technology & IT",
     "task_keywords": ["user experience", "user interface", "wireframing", "figma", "prototyping", "user research", "usability testing"],
     "core_tasks": [
         {"task": "Conduct user research and interviews", "ai_augmentable": 45},
         {"task": "Create wireframes and prototypes", "ai_augmentable": 70},
         {"task": "Design user interfaces in Figma", "ai_augmentable": 70},
         {"task": "Run usability testing sessions", "ai_augmentable": 50},
         {"task": "Collaborate with developers on implementation", "ai_augmentable": 35}]},
    {"id": "product-manager", "title": "Product Manager", "category": "Technology & IT",
     "task_keywords": ["product management", "roadmapping", "user feedback", "requirements", "prioritisation", "kpi tracking", "stakeholder management"],
     "core_tasks": [
         {"task": "Define product roadmap and priorities", "ai_augmentable": 45},
         {"task": "Gather and analyse user feedback", "ai_augmentable": 75},
         {"task": "Write product requirements documents", "ai_augmentable": 85},
         {"task": "Coordinate with engineering and design teams", "ai_augmentable": 40},
         {"task": "Track product metrics and KPIs", "ai_augmentable": 80}]},
    {"id": "business-analyst", "title": "Business Analyst", "category": "Technology & IT",
     "task_keywords": ["requirements gathering", "process analysis", "functional specifications", "stakeholder workshops", "uat", "documentation"],
     "core_tasks": [
         {"task": "Gather and document business requirements", "ai_augmentable": 75},
         {"task": "Analyse business processes and workflows", "ai_augmentable": 65},
         {"task": "Create functional specifications for IT projects", "ai_augmentable": 85},
         {"task": "Facilitate stakeholder workshops", "ai_augmentable": 30},
         {"task": "Support user acceptance testing", "ai_augmentable": 60}]},
    {"id": "ai-ml-engineer", "title": "AI/ML Engineer", "category": "Technology & IT",
     "task_keywords": ["machine learning", "deep learning", "llm", "python", "data pipelines", "model deployment", "prompt engineering", "model evaluation"],
     "core_tasks": [
         {"task": "Design and train machine learning models", "ai_augmentable": 65},
         {"task": "Build data pipelines for ML workflows", "ai_augmentable": 75},
         {"task": "Deploy and monitor models in production", "ai_augmentable": 70},
         {"task": "Fine-tune LLMs for specific use cases", "ai_augmentable": 60},
         {"task": "Evaluate model performance and bias", "ai_augmentable": 65}]},
    {"id": "full-stack-developer", "title": "Full Stack Developer", "category": "Technology & IT",
     "task_keywords": ["react", "javascript", "node.js", "api development", "databases", "frontend development", "backend development"],
     "core_tasks": [
         {"task": "Build frontend interfaces with React/Vue", "ai_augmentable": 80},
         {"task": "Develop backend APIs and services", "ai_augmentable": 80},
         {"task": "Manage databases and data models", "ai_augmentable": 75},
         {"task": "Integrate third-party services and APIs", "ai_augmentable": 70},
         {"task": "Optimise application performance", "ai_augmentable": 65}]},
    {"id": "mobile-app-developer", "title": "Mobile App Developer", "category": "Technology & IT",
     "task_keywords": ["ios", "android", "swift", "kotlin", "mobile development", "app store", "api integration"],
     "core_tasks": [
         {"task": "Build iOS/Android applications", "ai_augmentable": 80},
         {"task": "Integrate with backend APIs", "ai_augmentable": 70},
         {"task": "Optimise app performance and battery usage", "ai_augmentable": 60},
         {"task": "Implement push notifications and in-app purchases", "ai_augmentable": 70},
         {"task": "Publish apps to App Store and Google Play", "ai_augmentable": 50}]},
    {"id": "qa-test-engineer", "title": "QA/Test Engineer", "category": "Technology & IT",
     "task_keywords": ["test automation", "test planning", "selenium", "regression testing", "performance testing", "defect tracking", "quality assurance"],
     "core_tasks": [
         {"task": "Write and execute test plans and test cases", "ai_augmentable": 80},
         {"task": "Automate regression tests", "ai_augmentable": 85},
         {"task": "Report and track software defects", "ai_augmentable": 75},
         {"task": "Perform load and performance testing", "ai_augmentable": 70},
         {"task": "Ensure release quality standards", "ai_augmentable": 50}]},

    # ── Finance & Accounting ──────────────────────────────────────────
    {"id": "accountant", "title": "Accountant", "category": "Finance & Accounting",
     "task_keywords": ["financial reporting", "accounts payable", "accounts receivable", "reconciliation", "tax compliance", "audit support", "accounting software"],
     "core_tasks": [
         {"task": "Prepare financial statements and reports", "ai_augmentable": 80},
         {"task": "Manage accounts payable and receivable", "ai_augmentable": 85},
         {"task": "Reconcile bank and ledger accounts", "ai_augmentable": 90},
         {"task": "Ensure compliance with tax regulations", "ai_augmentable": 55},
         {"task": "Support audit processes", "ai_augmentable": 65}]},
    {"id": "financial-analyst", "title": "Financial Analyst", "category": "Finance & Accounting",
     "task_keywords": ["financial modelling", "forecasting", "budgeting", "variance analysis", "excel", "financial reporting", "risk analysis"],
     "core_tasks": [
         {"task": "Build financial models and forecasts", "ai_augmentable": 70},
         {"task": "Analyse company performance and trends", "ai_augmentable": 75},
         {"task": "Prepare investment recommendations", "ai_augmentable": 55},
         {"task": "Monitor market conditions and risks", "ai_augmentable": 80},
         {"task": "Present findings to management", "ai_augmentable": 50}]},
    {"id": "auditor", "title": "Auditor", "category": "Finance & Accounting",
     "task_keywords": ["audit", "internal controls", "compliance", "risk assessment", "audit reporting", "ifrs", "sampling"],
     "core_tasks": [
         {"task": "Plan and execute audit engagements", "ai_augmentable": 50},
         {"task": "Test internal controls and financial records", "ai_augmentable": 75},
         {"task": "Identify compliance issues and risks", "ai_augmentable": 65},
         {"task": "Prepare audit reports and recommendations", "ai_augmentable": 80},
         {"task": "Follow up on remediation actions", "ai_augmentable": 45}]},
    {"id": "tax-specialist", "title": "Tax Specialist", "category": "Finance & Accounting",
     "task_keywords": ["tax filing", "tax planning", "gst", "corporate tax", "transfer pricing", "tax advisory", "iras"],
     "core_tasks": [
         {"task": "Prepare and file tax returns", "ai_augmentable": 85},
         {"task": "Advise on tax planning strategies", "ai_augmentable": 50},
         {"task": "Monitor changes in tax legislation", "ai_augmentable": 85},
         {"task": "Liaise with tax authorities", "ai_augmentable": 30},
         {"task": "Conduct tax risk assessments", "ai_augmentable": 60}]},
    {"id": "bank-officer", "title": "Bank Officer", "category": "Finance & Accounting",
     "task_keywords": ["customer service", "loan processing", "credit assessment", "kyc", "aml", "banking products", "sales"],
     "core_tasks": [
         {"task": "Process customer transactions and applications", "ai_augmentable": 85},
         {"task": "Assess loan and credit applications", "ai_augmentable": 70},
         {"task": "Provide product advice to customers", "ai_augmentable": 45},
         {"task": "Resolve customer complaints", "ai_augmentable": 40},
         {"task": "Ensure KYC and AML compliance", "ai_augmentable": 75}]},
    {"id": "investment-analyst", "title": "Investment Analyst", "category": "Finance & Accounting",
     "task_keywords": ["equity research", "valuation", "portfolio analysis", "financial modelling", "due diligence", "market research"],
     "core_tasks": [
         {"task": "Research and evaluate investment opportunities", "ai_augmentable": 70},
         {"task": "Build valuation models", "ai_augmentable": 70},
         {"task": "Monitor portfolio performance", "ai_augmentable": 85},
         {"task": "Prepare investment memos and presentations", "ai_augmentable": 85},
         {"task": "Track industry and macroeconomic trends", "ai_augmentable": 85}]},
    {"id": "payroll-specialist", "title": "Payroll Specialist", "category": "Finance & Accounting",
     "task_keywords": ["payroll processing", "cpf", "compensation", "benefits administration", "hris", "statutory compliance"],
     "core_tasks": [
         {"task": "Process monthly payroll for employees", "ai_augmentable": 90},
         {"task": "Calculate CPF contributions and taxes", "ai_augmentable": 90},
         {"task": "Maintain payroll records and reports", "ai_augmentable": 85},
         {"task": "Handle payroll enquiries from staff", "ai_augmentable": 55},
         {"task": "Ensure compliance with employment laws", "ai_augmentable": 55}]},

    # ── Marketing & Communications ────────────────────────────────────
    {"id": "digital-marketer", "title": "Digital Marketer", "category": "Marketing & Communications",
     "task_keywords": ["digital marketing", "campaign management", "google ads", "meta ads", "analytics", "conversion optimisation", "email marketing"],
     "core_tasks": [
         {"task": "Plan and execute digital marketing campaigns", "ai_augmentable": 65},
         {"task": "Manage social media channels and content", "ai_augmentable": 80},
         {"task": "Run paid advertising on Google and Meta", "ai_augmentable": 75},
         {"task": "Analyse campaign performance metrics", "ai_augmentable": 85},
         {"task": "Optimise conversion funnels", "ai_augmentable": 70}]},
    {"id": "content-writer", "title": "Content Writer", "category": "Marketing & Communications",
     "task_keywords": ["copywriting", "content writing", "seo", "editing", "storytelling", "content strategy", "keyword research"],
     "core_tasks": [
         {"task": "Write blog posts, articles, and marketing copy", "ai_augmentable": 85},
         {"task": "Research topics and keywords", "ai_augmentable": 85},
         {"task": "Edit and proofread content", "ai_augmentable": 90},
         {"task": "Optimise content for SEO", "ai_augmentable": 80},
         {"task": "Collaborate with designers on visual content", "ai_augmentable": 35}]},
    {"id": "social-media-manager", "title": "Social Media Manager", "category": "Marketing & Communications",
     "task_keywords": ["social media", "community management", "content calendar", "social listening", "influencer marketing", "engagement analytics"],
     "core_tasks": [
         {"task": "Create and schedule social media posts", "ai_augmentable": 85},
         {"task": "Engage with followers and manage communities", "ai_augmentable": 55},
         {"task": "Analyse social media metrics", "ai_augmentable": 85},
         {"task": "Run social media ad campaigns", "ai_augmentable": 70},
         {"task": "Monitor brand sentiment online", "ai_augmentable": 85}]},
    {"id": "pr-executive", "title": "PR Executive", "category": "Marketing & Communications",
     "task_keywords": ["media relations", "press releases", "public relations", "crisis communication", "event management", "media monitoring"],
     "core_tasks": [
         {"task": "Draft press releases and media kits", "ai_augmentable": 85},
         {"task": "Build relationships with journalists", "ai_augmentable": 25},
         {"task": "Organise press events and media briefings", "ai_augmentable": 45},
         {"task": "Monitor media coverage", "ai_augmentable": 90},
         {"task": "Manage crisis communications", "ai_augmentable": 35}]},
    {"id": "brand-manager", "title": "Brand Manager", "category": "Marketing & Communications",
     "task_keywords": ["brand strategy", "brand management", "market research", "campaign planning", "positioning", "creative direction"],
     "core_tasks": [
         {"task": "Develop and execute brand strategy", "ai_augmentable": 45},
         {"task": "Manage brand guidelines and identity", "ai_augmentable": 60},
         {"task": "Plan brand campaigns and activations", "ai_augmentable": 55},
         {"task": "Conduct market research on brand perception", "ai_augmentable": 75},
         {"task": "Coordinate with creative and marketing teams", "ai_augmentable": 35}]},
    {"id": "seo-specialist", "title": "SEO Specialist", "category": "Marketing & Communications",
     "task_keywords": ["seo", "keyword research", "technical seo", "link building", "google analytics", "search console", "on-page optimisation"],
     "core_tasks": [
         {"task": "Conduct keyword research and analysis", "ai_augmentable": 90},
         {"task": "Optimise on-page and technical SEO", "ai_augmentable": 75},
         {"task": "Build backlinks and monitor link profile", "ai_augmentable": 60},
         {"task": "Track search rankings and organic traffic", "ai_augmentable": 90},
         {"task": "Report on SEO performance", "ai_augmentable": 85}]},
    {"id": "graphic-designer", "title": "Graphic Designer", "category": "Marketing & Communications",
     "task_keywords": ["graphic design", "adobe creative suite", "illustrator", "photoshop", "visual design", "layout", "print production"],
     "core_tasks": [
         {"task": "Create visual designs for digital and print", "ai_augmentable": 70},
         {"task": "Design marketing collateral and social media assets", "ai_augmentable": 75},
         {"task": "Work with brand guidelines", "ai_augmentable": 60},
         {"task": "Prepare files for production", "ai_augmentable": 70},
         {"task": "Collaborate with marketing and product teams", "ai_augmentable": 35}]},

    # ── Business & Administration ─────────────────────────────────────
    {"id": "hr-executive", "title": "HR Executive", "category": "Business & Administration",
     "task_keywords": ["recruitment", "onboarding", "employee relations", "hr administration", "performance management", "hris", "talent acquisition"],
     "core_tasks": [
         {"task": "Manage recruitment and onboarding", "ai_augmentable": 70},
         {"task": "Handle employee relations and grievances", "ai_augmentable": 25},
         {"task": "Administer payroll and benefits", "ai_augmentable": 85},
         {"task": "Maintain HR policies and compliance", "ai_augmentable": 75},
         {"task": "Support performance management processes", "ai_augmentable": 60}]},
    {"id": "admin-officer", "title": "Admin Officer", "category": "Business & Administration",
     "task_keywords": ["office administration", "data entry", "filing", "scheduling", "correspondence", "microsoft office", "records management"],
     "core_tasks": [
         {"task": "Manage office operations and supplies", "ai_augmentable": 55},
         {"task": "Handle correspondence and filings", "ai_augmentable": 85},
         {"task": "Coordinate meetings and schedules", "ai_augmentable": 85},
         {"task": "Maintain administrative records", "ai_augmentable": 85},
         {"task": "Support other departments with admin tasks", "ai_augmentable": 55}]},
    {"id": "operations-manager", "title": "Operations Manager", "category": "Business & Administration",
     "task_keywords": ["operations management", "process improvement", "budget management", "team leadership", "vendor management", "compliance"],
     "core_tasks": [
         {"task": "Oversee daily business operations", "ai_augmentable": 45},
         {"task": "Optimise operational processes and workflows", "ai_augmentable": 60},
         {"task": "Manage operational budgets", "ai_augmentable": 65},
         {"task": "Coordinate across departments", "ai_augmentable": 40},
         {"task": "Ensure compliance with regulations", "ai_augmentable": 55}]},
    {"id": "project-manager", "title": "Project Manager", "category": "Business & Administration",
     "task_keywords": ["project management", "agile", "scrum", "stakeholder management", "risk management", "budgeting", "scheduling"],
     "core_tasks": [
         {"task": "Plan and scope project deliverables", "ai_augmentable": 60},
         {"task": "Manage project timelines and budgets", "ai_augmentable": 70},
         {"task": "Coordinate project teams and stakeholders", "ai_augmentable": 35},
         {"task": "Track risks and issues", "ai_augmentable": 70},
         {"task": "Report project status to sponsors", "ai_augmentable": 85}]},
    {"id": "office-manager", "title": "Office Manager", "category": "Business & Administration",
     "task_keywords": ["facilities management", "vendor management", "budget management", "team supervision", "event planning", "workplace safety"],
     "core_tasks": [
         {"task": "Manage office facilities and vendors", "ai_augmentable": 50},
         {"task": "Oversee administrative staff", "ai_augmentable": 30},
         {"task": "Handle office budget and expenses", "ai_augmentable": 70},
         {"task": "Ensure workplace health and safety", "ai_augmentable": 40},
         {"task": "Organise company events", "ai_augmentable": 55}]},
    {"id": "executive-assistant", "title": "Executive Assistant", "category": "Business & Administration",
     "task_keywords": ["calendar management", "travel arrangements", "meeting coordination", "minute taking", "expense management", "correspondence"],
     "core_tasks": [
         {"task": "Manage executive calendars and schedules", "ai_augmentable": 85},
         {"task": "Prepare meeting materials and minutes", "ai_augmentable": 90},
         {"task": "Handle travel and expense arrangements", "ai_augmentable": 85},
         {"task": "Screen communications and requests", "ai_augmentable": 75},
         {"task": "Support special projects", "ai_augmentable": 55}]},
    {"id": "customer-service-officer", "title": "Customer Service Officer", "category": "Business & Administration",
     "task_keywords": ["customer service", "complaint handling", "crm", "order processing", "call centre", "service recovery"],
     "core_tasks": [
         {"task": "Handle customer enquiries via phone and email", "ai_augmentable": 65},
         {"task": "Resolve complaints and escalate issues", "ai_augmentable": 40},
         {"task": "Process orders and returns", "ai_augmentable": 85},
         {"task": "Maintain customer records in CRM", "ai_augmentable": 85},
         {"task": "Collect and report customer feedback", "ai_augmentable": 80}]},
    {"id": "sales-executive", "title": "Sales Executive", "category": "Business & Administration",
     "task_keywords": ["sales", "lead generation", "negotiation", "crm", "client relationship management", "presentations", "pipeline management"],
     "core_tasks": [
         {"task": "Generate and qualify sales leads", "ai_augmentable": 75},
         {"task": "Conduct product demos and presentations", "ai_augmentable": 50},
         {"task": "Negotiate and close deals", "ai_augmentable": 30},
         {"task": "Maintain CRM records and pipeline", "ai_augmentable": 85},
         {"task": "Build and maintain client relationships", "ai_augmentable": 30}]},

    # ── Healthcare ────────────────────────────────────────────────────
    {"id": "registered-nurse", "title": "Registered Nurse", "category": "Healthcare",
     "task_keywords": ["patient care", "medication administration", "clinical documentation", "care coordination", "patient education", "wound care"],
     "core_tasks": [
         {"task": "Provide direct patient care and monitoring", "ai_augmentable": 20},
         {"task": "Administer medications and treatments", "ai_augmentable": 30},
         {"task": "Document patient conditions and progress", "ai_augmentable": 80},
         {"task": "Coordinate with doctors and care teams", "ai_augmentable": 40},
         {"task": "Educate patients and families on care", "ai_augmentable": 45}]},
    {"id": "healthcare-administrator", "title": "Healthcare Administrator", "category": "Healthcare",
     "task_keywords": ["healthcare operations", "staff scheduling", "regulatory compliance", "budget management", "patient experience", "procurement"],
     "core_tasks": [
         {"task": "Manage clinic or hospital operations", "ai_augmentable": 45},
         {"task": "Oversee staff scheduling and rosters", "ai_augmentable": 80},
         {"task": "Handle patient feedback and complaints", "ai_augmentable": 40},
         {"task": "Ensure regulatory compliance", "ai_augmentable": 55},
         {"task": "Manage healthcare budgets and procurement", "ai_augmentable": 60}]},
    {"id": "medical-technologist", "title": "Medical Technologist", "category": "Healthcare",
     "task_keywords": ["laboratory testing", "sample analysis", "quality control", "lab equipment", "result reporting", "laboratory safety"],
     "core_tasks": [
         {"task": "Perform laboratory tests and analyses", "ai_augmentable": 60},
         {"task": "Operate and maintain lab equipment", "ai_augmentable": 35},
         {"task": "Quality control and calibration of instruments", "ai_augmentable": 55},
         {"task": "Record and report test results", "ai_augmentable": 85},
         {"task": "Ensure lab safety and compliance", "ai_augmentable": 40}]},
    {"id": "pharmacy-technician", "title": "Pharmacy Technician", "category": "Healthcare",
     "task_keywords": ["medication dispensing", "inventory management", "prescription processing", "claims processing", "pharmacy operations"],
     "core_tasks": [
         {"task": "Prepare and dispense medications", "ai_augmentable": 50},
         {"task": "Manage pharmacy inventory", "ai_augmentable": 80},
         {"task": "Process prescriptions and insurance claims", "ai_augmentable": 85},
         {"task": "Assist pharmacists with patient counselling", "ai_augmentable": 30},
         {"task": "Maintain pharmacy records", "ai_augmentable": 85}]},
    {"id": "allied-health-professional", "title": "Allied Health Professional", "category": "Healthcare",
     "task_keywords": ["therapy", "patient assessment", "care planning", "rehabilitation", "clinical documentation", "multidisciplinary teamwork"],
     "core_tasks": [
         {"task": "Assess and treat patients", "ai_augmentable": 25},
         {"task": "Develop care plans", "ai_augmentable": 55},
         {"task": "Conduct therapy sessions", "ai_augmentable": 20},
         {"task": "Document patient progress", "ai_augmentable": 80},
         {"task": "Collaborate with multidisciplinary teams", "ai_augmentable": 35}]},
    {"id": "care-coordinator", "title": "Care Coordinator", "category": "Healthcare",
     "task_keywords": ["care coordination", "appointment scheduling", "patient communication", "care plans", "community resources", "case management"],
     "core_tasks": [
         {"task": "Coordinate patient care across providers", "ai_augmentable": 55},
         {"task": "Schedule appointments and follow-ups", "ai_augmentable": 90},
         {"task": "Communicate with patients and families", "ai_augmentable": 40},
         {"task": "Maintain care plans and records", "ai_augmentable": 80},
         {"task": "Liaise with community resources", "ai_augmentable": 35}]},

    # ── Manufacturing & Engineering ───────────────────────────────────
    {"id": "mechanical-engineer", "title": "Mechanical Engineer", "category": "Manufacturing & Engineering",
     "task_keywords": ["mechanical design", "cad", "simulation", "stress analysis", "manufacturing processes", "technical drawings", "troubleshooting"],
     "core_tasks": [
         {"task": "Design mechanical systems and components", "ai_augmentable": 55},
         {"task": "Run simulations and stress analysis", "ai_augmentable": 70},
         {"task": "Prepare technical drawings and specifications", "ai_augmentable": 75},
         {"task": "Oversee manufacturing processes", "ai_augmentable": 35},
         {"task": "Troubleshoot mechanical failures", "ai_augmentable": 45}]},
    {"id": "electrical-engineer", "title": "Electrical Engineer", "category": "Manufacturing & Engineering",
     "task_keywords": ["electrical design", "power systems", "circuit design", "load calculations", "commissioning", "safety inspection"],
     "core_tasks": [
         {"task": "Design electrical systems and circuits", "ai_augmentable": 55},
         {"task": "Perform load calculations and power studies", "ai_augmentable": 75},
         {"task": "Oversee installation and commissioning", "ai_augmentable": 25},
         {"task": "Conduct safety inspections", "ai_augmentable": 40},
         {"task": "Maintain electrical documentation", "ai_augmentable": 80}]},
    {"id": "quality-inspector", "title": "Quality Inspector", "category": "Manufacturing & Engineering",
     "task_keywords": ["quality inspection", "quality control", "measurement", "defect analysis", "calibration", "inspection reporting"],
     "core_tasks": [
         {"task": "Inspect products and materials for defects", "ai_augmentable": 65},
         {"task": "Conduct quality tests and measurements", "ai_augmentable": 60},
         {"task": "Document inspection findings", "ai_augmentable": 85},
         {"task": "Identify and report quality issues", "ai_augmentable": 70},
         {"task": "Maintain calibration of inspection tools", "ai_augmentable": 35}]},
    {"id": "production-supervisor", "title": "Production Supervisor", "category": "Manufacturing & Engineering",
     "task_keywords": ["production management", "team supervision", "scheduling", "quality standards", "lean manufacturing", "troubleshooting"],
     "core_tasks": [
         {"task": "Supervise production line operations", "ai_augmentable": 35},
         {"task": "Manage production schedules and targets", "ai_augmentable": 75},
         {"task": "Ensure quality and safety standards", "ai_augmentable": 45},
         {"task": "Train and mentor production staff", "ai_augmentable": 30},
         {"task": "Troubleshoot production issues", "ai_augmentable": 45}]},
    {"id": "facilities-manager", "title": "Facilities Manager", "category": "Manufacturing & Engineering",
     "task_keywords": ["facilities management", "maintenance management", "vendor management", "budget management", "building systems", "safety compliance"],
     "core_tasks": [
         {"task": "Oversee building maintenance and repairs", "ai_augmentable": 35},
         {"task": "Manage facilities budget and vendors", "ai_augmentable": 55},
         {"task": "Ensure workplace safety compliance", "ai_augmentable": 50},
         {"task": "Coordinate renovations and upgrades", "ai_augmentable": 40},
         {"task": "Manage security and access systems", "ai_augmentable": 60}]},

    # ── Retail & Hospitality ──────────────────────────────────────────
    {"id": "retail-store-manager", "title": "Retail Store Manager", "category": "Retail & Hospitality",
     "task_keywords": ["store management", "inventory management", "visual merchandising", "sales targets", "team management", "p&l management"],
     "core_tasks": [
         {"task": "Manage store operations and staff", "ai_augmentable": 40},
         {"task": "Oversee inventory and visual merchandising", "ai_augmentable": 65},
         {"task": "Drive sales targets and KPIs", "ai_augmentable": 55},
         {"task": "Handle customer complaints", "ai_augmentable": 35},
         {"task": "Manage store budget and P&L", "ai_augmentable": 60}]},
    {"id": "fnb-supervisor", "title": "F&B Supervisor", "category": "Retail & Hospitality",
     "task_keywords": ["restaurant operations", "staff scheduling", "food safety", "customer service", "inventory management", "staff training"],
     "core_tasks": [
         {"task": "Supervise restaurant service operations", "ai_augmentable": 30},
         {"task": "Manage staff scheduling and training", "ai_augmentable": 70},
         {"task": "Ensure food safety and hygiene standards", "ai_augmentable": 40},
         {"task": "Handle customer feedback", "ai_augmentable": 50},
         {"task": "Monitor inventory and supplies", "ai_augmentable": 75}]},
    {"id": "hotel-front-desk-officer", "title": "Hotel Front Desk Officer", "category": "Retail & Hospitality",
     "task_keywords": ["guest services", "reservations", "check-in/check-out", "payment processing", "concierge", "property management systems"],
     "core_tasks": [
         {"task": "Check in and check out guests", "ai_augmentable": 60},
         {"task": "Handle reservations and enquiries", "ai_augmentable": 75},
         {"task": "Resolve guest complaints", "ai_augmentable": 30},
         {"task": "Process payments", "ai_augmentable": 85},
         {"task": "Coordinate with housekeeping and concierge", "ai_augmentable": 45}]},
    {"id": "tour-guide", "title": "Tour Guide", "category": "Retail & Hospitality",
     "task_keywords": ["tour guiding", "storytelling", "customer service", "itinerary planning", "local knowledge", "group management"],
     "core_tasks": [
         {"task": "Lead guided tours and share local knowledge", "ai_augmentable": 30},
         {"task": "Ensure tourist safety and comfort", "ai_augmentable": 20},
         {"task": "Manage tour logistics and timing", "ai_augmentable": 70},
         {"task": "Handle tourist enquiries", "ai_augmentable": 55},
         {"task": "Promote local attractions", "ai_augmentable": 50}]},
    {"id": "event-coordinator", "title": "Event Coordinator", "category": "Retail & Hospitality",
     "task_keywords": ["event planning", "vendor coordination", "budget management", "registration management", "logistics", "event marketing"],
     "core_tasks": [
         {"task": "Plan and execute events", "ai_augmentable": 50},
         {"task": "Coordinate vendors and suppliers", "ai_augmentable": 45},
         {"task": "Manage event budgets", "ai_augmentable": 65},
         {"task": "Handle guest registrations", "ai_augmentable": 85},
         {"task": "Ensure event safety compliance", "ai_augmentable": 40}]},

    # ── Education & Training ──────────────────────────────────────────
    {"id": "teacher", "title": "Teacher", "category": "Education & Training",
     "task_keywords": ["lesson planning", "curriculum delivery", "assessment", "classroom management", "parent communication", "edtech"],
     "core_tasks": [
         {"task": "Plan and deliver lessons", "ai_augmentable": 65},
         {"task": "Assess and grade student work", "ai_augmentable": 75},
         {"task": "Manage classroom behaviour", "ai_augmentable": 15},
         {"task": "Communicate with parents", "ai_augmentable": 45},
         {"task": "Develop curriculum materials", "ai_augmentable": 75}]},
    {"id": "training-coordinator", "title": "Training Coordinator", "category": "Education & Training",
     "task_keywords": ["training administration", "lms", "scheduling", "logistics coordination", "attendance tracking", "training evaluation"],
     "core_tasks": [
         {"task": "Plan and schedule training programmes", "ai_augmentable": 80},
         {"task": "Coordinate with trainers and venues", "ai_augmentable": 55},
         {"task": "Manage training materials and LMS", "ai_augmentable": 80},
         {"task": "Track attendance and completion", "ai_augmentable": 90},
         {"task": "Evaluate training effectiveness", "ai_augmentable": 70}]},
    {"id": "curriculum-developer", "title": "Curriculum Developer", "category": "Education & Training",
     "task_keywords": ["instructional design", "curriculum development", "assessment design", "learning outcomes", "elearning", "content development"],
     "core_tasks": [
         {"task": "Design course curricula and learning materials", "ai_augmentable": 70},
         {"task": "Develop assessments and rubrics", "ai_augmentable": 80},
         {"task": "Align content with learning outcomes", "ai_augmentable": 60},
         {"task": "Incorporate educational technology", "ai_augmentable": 65},
         {"task": "Review and update existing curricula", "ai_augmentable": 70}]},

    # ── Logistics & Supply Chain ──────────────────────────────────────
    {"id": "warehouse-manager", "title": "Warehouse Manager", "category": "Logistics & Supply Chain",
     "task_keywords": ["warehouse operations", "inventory management", "wms", "team supervision", "dispatch", "safety compliance"],
     "core_tasks": [
         {"task": "Oversee warehouse operations and inventory", "ai_augmentable": 55},
         {"task": "Manage receiving and dispatch", "ai_augmentable": 65},
         {"task": "Optimise storage and layout", "ai_augmentable": 60},
         {"task": "Supervise warehouse staff", "ai_augmentable": 25},
         {"task": "Ensure safety compliance", "ai_augmentable": 40}]},
    {"id": "procurement-officer", "title": "Procurement Officer", "category": "Logistics & Supply Chain",
     "task_keywords": ["procurement", "sourcing", "supplier management", "contract negotiation", "purchase orders", "cost analysis"],
     "core_tasks": [
         {"task": "Source and evaluate suppliers", "ai_augmentable": 65},
         {"task": "Negotiate contracts and pricing", "ai_augmentable": 30},
         {"task": "Process purchase orders", "ai_augmentable": 90},
         {"task": "Monitor supplier performance", "ai_augmentable": 75},
         {"task": "Manage procurement budget", "ai_augmentable": 60}]},
    {"id": "supply-chain-analyst", "title": "Supply Chain Analyst", "category": "Logistics & Supply Chain",
     "task_keywords": ["supply chain analysis", "demand forecasting", "data analysis", "inventory planning", "dashboards", "risk analysis"],
     "core_tasks": [
         {"task": "Analyse supply chain data and metrics", "ai_augmentable": 85},
         {"task": "Forecast demand and inventory needs", "ai_augmentable": 80},
         {"task": "Identify supply chain risks", "ai_augmentable": 70},
         {"task": "Optimise logistics routes and costs", "ai_augmentable": 75},
         {"task": "Build supply chain dashboards", "ai_augmentable": 85}]},
    {"id": "logistics-coordinator", "title": "Logistics Coordinator", "category": "Logistics & Supply Chain",
     "task_keywords": ["shipment coordination", "freight forwarding", "delivery tracking", "shipping documentation", "route optimisation", "customs"],
     "core_tasks": [
         {"task": "Coordinate shipments and deliveries", "ai_augmentable": 70},
         {"task": "Manage freight forwarders and carriers", "ai_augmentable": 50},
         {"task": "Track shipments and resolve delays", "ai_augmentable": 75},
         {"task": "Prepare shipping documents", "ai_augmentable": 90},
         {"task": "Optimise delivery routes", "ai_augmentable": 85}]},

    # ── Construction & Built Environment ───────────────────────────────
    {"id": "civil-engineer", "title": "Civil Engineer", "category": "Construction & Built Environment",
     "task_keywords": ["structural design", "site supervision", "engineering calculations", "autocad", "project management", "building codes"],
     "core_tasks": [
         {"task": "Design and supervise construction projects", "ai_augmentable": 45},
         {"task": "Conduct site inspections", "ai_augmentable": 35},
         {"task": "Prepare engineering calculations and drawings", "ai_augmentable": 75},
         {"task": "Manage project budgets and timelines", "ai_augmentable": 60},
         {"task": "Ensure building code compliance", "ai_augmentable": 55}]},
    {"id": "quantity-surveyor", "title": "Quantity Surveyor", "category": "Construction & Built Environment",
     "task_keywords": ["cost estimation", "bills of quantities", "tender management", "cost control", "contract administration", "variations"],
     "core_tasks": [
         {"task": "Estimate project costs and prepare bills of quantities", "ai_augmentable": 75},
         {"task": "Manage tender processes", "ai_augmentable": 70},
         {"task": "Track project costs and variations", "ai_augmentable": 80},
         {"task": "Conduct cost analysis and reporting", "ai_augmentable": 80},
         {"task": "Administer contracts and claims", "ai_augmentable": 55}]},
    {"id": "safety-officer", "title": "Workplace Safety Officer", "category": "Construction & Built Environment",
     "task_keywords": ["safety audits", "incident investigation", "wsh compliance", "risk assessment", "safety training", "toolbox talks"],
     "core_tasks": [
         {"task": "Conduct safety inspections and audits", "ai_augmentable": 45},
         {"task": "Investigate accidents and incidents", "ai_augmentable": 40},
         {"task": "Develop safety procedures and toolbox talks", "ai_augmentable": 75},
         {"task": "Ensure WSH compliance", "ai_augmentable": 55},
         {"task": "Train staff on safety practices", "ai_augmentable": 35}]},
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


def get_role_task_titles(role: dict) -> list[str]:
    """Return just the task strings for a role (for LLM prompts)."""
    return [t["task"] for t in role.get("core_tasks", [])]


def get_role_task_scores(role_id: str) -> list[dict]:
    """Return ``[{task, ai_augmentable}]`` for a role, or [] if unknown."""
    role = get_role(role_id)
    if not role:
        return []
    return role.get("core_tasks", [])
