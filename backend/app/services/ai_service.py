"""AI-powered services: growth plans, learning journeys, auto listing generation, and multilingual chatbot.

All AI features are simulated locally with mock logic so the prototype
works without external API keys. Each function returns structured data
matching the schemas consumed by the routers.
"""

import hashlib
import random
import re
from datetime import datetime, timedelta, timezone


# ── AI Growth Planner ──────────────────────────────────────────────────────────

_GROWTH_EXPLANATIONS = [
    "Recommended because it strengthens your {skill} skills before the next milestone.",
    "This activity complements your goal by building practical experience.",
    "Attending this will expand your professional network in the field.",
    "Builds foundational knowledge required for advanced topics later.",
    "Provides hands-on practice to solidify what you've learned.",
    "A great opportunity to apply your new skills in a real-world setting.",
    "Networking here connects you with mentors and peers in the industry.",
    "This balances your technical learning with soft skills development.",
]

_COURSE_CATEGORIES = [
    "AI & Machine Learning",
    "Software Engineering",
    "Cybersecurity",
    "Cloud Computing",
    "Data Science",
    "Digital Marketing",
    "Design",
    "Leadership",
    "Project Management",
    "Finance",
    "Entrepreneurship",
    "Career Development",
]


def generate_growth_plan(
    user: "object",
    days: int = 7,
) -> list[dict]:
    """Generate a personalised daily growth plan."""
    user_interests = getattr(user, "interests", "") or "technology, leadership"
    user_goals = getattr(user, "career_goals", "") or "career growth"

    plan_days = []
    used_topics = set()

    for day_num in range(1, days + 1):
        day_date = datetime.now(timezone.utc) + timedelta(days=day_num)
        activities = []

        # Pick 1-2 activities per day
        num_activities = 1 if day_num % 3 != 0 else 2

        for _ in range(num_activities):
            # Find an unused topic
            topic = None
            for cat in _COURSE_CATEGORIES:
                if cat not in used_topics:
                    topic = cat
                    used_topics.add(cat)
                    break

            if topic is None:
                topic = random.choice(_COURSE_CATEGORIES)

            skill = topic.split("&")[0].strip() if "&" in topic else topic.split()[0]
            explanation = random.choice(_GROWTH_EXPLANATIONS).replace("{skill}", skill)

            activities.append({
                "event_id": 0,
                "title": f"{topic} Workshop",
                "type": "Course",
                "time": f"{random.choice(['09:00', '10:00', '14:00', '18:00', '19:00'])}",
                "duration_hours": random.choice([2, 3, 4, 6, 8]),
                "location": "Online",
                "explanation": explanation,
                "category": topic,
            })

        plan_days.append({
            "day": day_num,
            "date_label": day_date.strftime("%a %b %d"),
            "activities": activities,
        })

    return plan_days


# ── AI Learning Journey ────────────────────────────────────────────────────────

def generate_learning_journey(
    user: "object",
    goal: str,
    weeks: int = 4,
) -> list[dict]:
    """Generate a week-by-week learning roadmap towards a goal."""
    roadmap = []
    week_focuses = [
        "Foundation & Core Concepts",
        "Practical Application & Hands-on",
        "Networking & Community",
        "Advanced Topics & Specialisation",
        "Capstone & Real-World Projects",
        "Industry Deep Dive",
        "Mentorship & Collaboration",
        "Integration & Mastery",
        "Career Application",
        "Leadership & Giving Back",
        "Cross-Disciplinary Skills",
        "Future Trends & Innovation",
    ]

    for week_num in range(1, weeks + 1):
        focus = week_focuses[(week_num - 1) % len(week_focuses)]
        roadmap.append({
            "week": week_num,
            "title": f"Week {week_num}: {focus}",
            "focus": focus,
        })

    return roadmap


# ── AI Auto Listing Generator ─────────────────────────────────────────────────

def generate_listing(input_text: str) -> dict:
    """Generate a complete course listing from a description or URL."""
    text_lower = input_text.lower()

    # Detect category from keywords
    category_map = {
        "AI": ["ai", "machine learning", "ml", "neural", "deep learning", "llm", "gpt", "model"],
        "Software Engineering": ["code", "programming", "software", "developer", "engineering", "web", "app", "api", "react", "python", "javascript"],
        "Cybersecurity": ["security", "hacking", "cyber", "penetration", "vulnerability", "encryption"],
        "Cloud Computing": ["cloud", "aws", "azure", "gcp", "infrastructure", "devops", "kubernetes"],
        "Data Science": ["data", "analytics", "statistics", "visualization", "pandas", "sql"],
        "Digital Marketing": ["marketing", "seo", "ads", "brand", "content", "social media", "growth"],
        "Design": ["design", "ui", "ux", "figma", "creative", "art", "branding"],
        "Leadership": ["leader", "management", "executive", "team", "strategy", "ceo"],
        "Project Management": ["project", "agile", "scrum", "kanban", "planning", "delivery"],
        "Finance": ["finance", "invest", "trading", "crypto", "banking", "fintech", "wealth"],
        "Entrepreneurship": ["startup", "founder", "business", "entrepreneur", "venture", "pitch"],
        "Career Development": ["career", "resume", "interview", "job", "upskilling", "professional"],
    }

    detected_category = "AI"
    max_matches = 0
    for cat, keywords in category_map.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches > max_matches:
            max_matches = matches
            detected_category = cat.title()

    # Generate title from first sentence or extract key concepts
    first_line = input_text.strip().split("\n")[0][:100]
    title = first_line if len(first_line) > 10 else f"{detected_category} Course: {first_line}"

    # Extract skills
    all_skills = []
    for cat, keywords in category_map.items():
        for kw in keywords:
            if kw in text_lower and kw.title() not in all_skills:
                all_skills.append(kw.title())
    if not all_skills:
        all_skills = [detected_category, "Professional Development"]

    # Generate tags
    tags = [w.strip() for w in re.findall(r'\b\w{4,}\b', text_lower) if w not in {"this", "that", "with", "from", "have", "will", "about"}][:8]

    difficulty = "Beginner" if any(w in text_lower for w in ["beginner", "intro", "basics", "fundamentals", "101"]) else \
                 "Advanced" if any(w in text_lower for w in ["advanced", "expert", "senior", "deep dive"]) else "Intermediate"

    return {
        "title": title.strip(),
        "description": input_text[:500] if len(input_text) > 100 else f"Join us for an engaging {detected_category.lower()} course. {input_text}",
        "category": detected_category,
        "tags": tags[:6],
        "skills": all_skills[:6],
        "seo_keywords": [f"{detected_category.lower()} Singapore", f"{detected_category.lower()} course", f"{tags[0]} training" if tags else "course Singapore"],
        "difficulty": difficulty,
        "recommended_audience": f"Professionals interested in {detected_category.lower()}",
        "duration_hours": 4.0 if "workshop" in text_lower else 8.0 if "bootcamp" in text_lower else 3.0,
        "price_suggestion_sgd": 0.0 if "free" in text_lower else 50.0 if "beginner" in text_lower else 150.0,
    }


# ── AI Multilingual Chatbot ────────────────────────────────────────────────────

_TRANSLATIONS = {
    "en": {
        "greeting": "Hello! I'm your Nexa AI assistant. I can help you find courses, plan your learning journey, or answer questions about upskilling. How can I help you today?",
        "default": "I'd be happy to help you with that! Based on your interests, I'd recommend exploring our courses in {category}. Would you like me to generate a personalised recommendation?",
    },
    "zh": {
        "greeting": "你好！我是您的 Nexa AI 助手。我可以帮助您查找课程、规划学习路径，或回答有关提升技能的问题。今天我能帮您什么？",
        "default": "我很乐意帮助您！根据您的兴趣，我建议您探索我们在{category}领域的课程。您想让我生成个性化推荐吗？",
    },
    "ms": {
        "greeting": "Hai! Saya pembantu AI Nexa anda. Saya boleh membantu anda mencari kursus, merancang perjalanan pembelajaran, atau menjawab soalan tentang peningkatan kemahiran. Bagaimana saya boleh membantu anda hari ini?",
        "default": "Saya dengan senang hati membantu anda! Berdasarkan minat anda, saya mengesyorkan meneroka kursus dalam {category}. Adakah anda mahu saya menjana cadangan peribadi?",
    },
    "ta": {
        "greeting": "வணக்கம்! நான் உங்கள் Nexa AI உதவியாளர். பாடநெறிகளைக் கண்டறிய, கற்றல் பயணத்தைத் திட்டமிட அல்லது திறன் மேம்பாடு பற்றிய கேள்விகளுக்கு பதிலளிக்க உதவ முடியும். இன்று நான் எப்படி உதவ முடியும்?",
        "default": "உங்களுக்கு உதவ நான் மகிழ்ச்சியடைகிறேன்! உங்கள் ஆர்வங்களின் அடிப்படையில், {category} இல் பாடநெறிகளை ஆராய பரிந்துரைக்கிறேன்.",
    },
}

_RESPONSE_TEMPLATES = {
    "course": "Based on your interests, here are some great courses:\n\n{courses}\n\nWould you like more details about any of these?",
    "journey": "I can generate a personalised learning journey for you! What's your goal? For example:\n- Become an AI Product Manager\n- Transition to cybersecurity\n- Build leadership skills\n\nTell me your goal and I'll create a week-by-week roadmap.",
    "plan": "I can create a personalised {days}-day growth plan for you. What areas would you like to focus on? I'll consider your interests, availability, and budget.",
    "general": "That's a great question! Here's what I can help with:\n\n1. **Find courses** - Search and get AI recommendations\n2. **Learning journey** - Generate a roadmap to your goal\n3. **Growth plan** - Get a 7/14/30 day personalised plan\n\nWhat would you like to explore?",
}


def chat_response(message: str, language: str = "en", user: "object" = None) -> dict:
    """Generate AI chatbot response with multilingual support."""
    lang = language if language in _TRANSLATIONS else "en"
    msg_lower = message.lower()

    # Detect intent
    if any(w in msg_lower for w in ["hello", "hi", "hey", "你好", "hai", "வணக்கம்"]):
        return {"reply": _TRANSLATIONS[lang]["greeting"], "language": lang}

    if any(w in msg_lower for w in ["course", "find", "search", "recommend", "课程", "cari", "பாடநெறி"]):
        category = "Technology" if user is None else getattr(user, "interests", "Technology").split(",")[0].strip()
        reply = _RESPONSE_TEMPLATES["course"].replace("{courses}", f"• AI Fundamentals Course\n• Generative AI Workshop\n• {category} Training")
        return {"reply": reply, "language": lang}

    if any(w in msg_lower for w in ["journey", "roadmap", "path", "路径", "laluan", "பயணம்"]):
        return {"reply": _RESPONSE_TEMPLATES["journey"], "language": lang}

    if any(w in msg_lower for w in ["plan", "schedule", "week", "month", "day", "计划", "jadual", "திட்டம்"]):
        days = "7" if "7" in msg_lower else "14" if "14" in msg_lower else "30"
        return {"reply": _RESPONSE_TEMPLATES["plan"].replace("{days}", days), "language": lang}

    # Default response
    category = "your field" if user is None else getattr(user, "interests", "Technology").split(",")[0].strip()
    default = _TRANSLATIONS[lang]["default"].replace("{category}", category)
    return {"reply": default, "language": lang}


# ── Mock Analytics ─────────────────────────────────────────────────────────────

def generate_organiser_dashboard_stats() -> dict:
    """Generate mock dashboard stats for an organiser."""
    months = []
    for i in range(6):
        month_date = datetime.now(timezone.utc) - timedelta(days=30 * (5 - i))
        months.append({
            "month": month_date.strftime("%b %Y"),
            "events": random.randint(2, 8),
            "attendees": random.randint(50, 300),
            "revenue": round(random.uniform(1000, 15000), 0),
        })

    return {
        "total_events": random.randint(10, 50),
        "total_attendees": random.randint(200, 1000),
        "avg_rating": round(random.uniform(4.0, 4.8), 1),
        "upcoming_events": random.randint(3, 10),
        "revenue_sgd": round(random.uniform(5000, 25000), 0),
        "monthly_growth": months,
    }
