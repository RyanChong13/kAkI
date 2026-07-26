"""AI-powered services: recommendations, growth plans, learning journeys,
substitute finder, auto listing generation, and multilingual chatbot.

All AI features are simulated locally with mock logic so the prototype
works without external API keys. Each function returns structured data
matching the schemas consumed by the routers.
"""

import hashlib
import json
import math
import random
import re
from datetime import datetime, timedelta, timezone

from app.models import Event


# ── Mock embedding helper ──────────────────────────────────────────────────────

def _hash_embedding(text: str) -> list[float]:
    """Generate a deterministic mock embedding vector from text."""
    h = hashlib.md5(text.lower().encode()).hexdigest()
    return [int(h[i:i+2], 16) / 255.0 for i in range(0, 16)]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1
    norm_b = math.sqrt(sum(x * x for x in b)) or 1
    return dot / (norm_a * norm_b)


def _event_text(ev: Event) -> str:
    return f"{ev.title} {ev.description} {ev.skills} {ev.tags} {ev.category} {ev.organiser}"


def _user_text(interests: str, goals: str, linkedin_url: str) -> str:
    return f"{interests} {goals} {linkedin_url}"


# ── AI Smart Recommendation Engine ─────────────────────────────────────────────

_RECOMMENDATION_REASONS = [
    "Because you attended similar events in {category}",
    "Matches your LinkedIn skills and interests",
    "Complements your learning journey in {category}",
    "Popular among users with similar goals",
    "Recommended because it strengthens skills you're developing",
    "Similar users enjoyed this event",
    "Aligns with your stated career goals",
    "High engagement from professionals in your network",
    "Fills a skill gap identified in your profile",
    "Trending in {category} this month",
]


def recommend_events(
    user: "object",
    events: list[Event],
    saved_ids: set[int] = None,
    completed_ids: set[int] = None,
    limit: int = 12,
) -> list[dict]:
    """Semantic similarity-based event recommendations."""
    saved_ids = saved_ids or set()
    completed_ids = completed_ids or set()

    user_emb = _hash_embedding(_user_text(
        getattr(user, "interests", ""),
        getattr(user, "career_goals", ""),
        getattr(user, "linkedin_url", ""),
    ))

    scored = []
    for ev in events:
        if ev.id in saved_ids or ev.id in completed_ids:
            continue
        if ev.is_cancelled:
            continue

        ev_emb = _hash_embedding(_event_text(ev))
        sim = _cosine_similarity(user_emb, ev_emb)

        # Boost for skill overlap with user interests
        user_skills = set(s.strip().lower() for s in getattr(user, "interests", "").split(",") if s.strip())
        ev_skills = set(s.strip().lower() for s in ev.skills.split(",") if s.strip())
        skill_overlap = user_skills & ev_skills
        skill_boost = len(skill_overlap) * 0.05

        final_score = min(sim + skill_boost, 1.0)
        reason = random.choice(_RECOMMENDATION_REASONS).replace("{category}", ev.category)
        matched = [s.strip() for s in ev.skills.split(",") if s.strip().lower() in skill_overlap] if skill_overlap else [s.strip() for s in ev.skills.split(",")[:2]]

        scored.append({
            "event": ev,
            "match_score": round(final_score, 3),
            "matched_skills": matched[:4],
            "reason": reason,
        })

    scored.sort(key=lambda x: x["match_score"], reverse=True)

    # Cold start: if no good matches, return diverse selection
    if scored and scored[0]["match_score"] < 0.3:
        random.shuffle(scored)

    return scored[:limit]


# ── AI Growth Planner ──────────────────────────────────────────────────────────

_ACTIVITY_TYPES = ["Course", "Workshop", "Networking Event", "Conference", "Hackathon", "Volunteering", "Hobby Activity"]

_GROWTH_EXPLANATIONS = [
    "Recommended because it strengthens your {skill} skills before the next milestone.",
    "This event complements your goal by building practical experience.",
    "Attending this will expand your professional network in the field.",
    "Builds foundational knowledge required for advanced topics later.",
    "Provides hands-on practice to solidify what you've learned.",
    "A great opportunity to apply your new skills in a real-world setting.",
    "Networking here connects you with mentors and peers in the industry.",
    "This balances your technical learning with soft skills development.",
]


def generate_growth_plan(
    user: "object",
    events: list[Event],
    days: int = 7,
) -> list[dict]:
    """Generate a personalised daily growth plan."""
    user_interests = getattr(user, "interests", "") or "technology, leadership"
    user_goals = getattr(user, "career_goals", "") or "career growth"
    budget = getattr(user, "budget_sgd", 200.0)

    # Filter affordable events
    affordable = [e for e in events if e.price_sgd <= budget and not e.is_cancelled]
    if not affordable:
        affordable = events[:20]

    # Score events by relevance
    user_emb = _hash_embedding(f"{user_interests} {user_goals}")
    scored_events = []
    for ev in affordable:
        ev_emb = _hash_embedding(_event_text(ev))
        score = _cosine_similarity(user_emb, ev_emb)
        scored_events.append((ev, score))
    scored_events.sort(key=lambda x: x[1], reverse=True)

    plan_days = []
    used_events = set()

    for day_num in range(1, days + 1):
        day_date = datetime.now(timezone.utc) + timedelta(days=day_num)
        activities = []

        # Pick 1-2 activities per day, mixing types
        num_activities = 1 if day_num % 3 != 0 else 2

        for _ in range(num_activities):
            # Find an unused event
            event = None
            for ev, score in scored_events:
                if ev.id not in used_events:
                    event = ev
                    used_events.add(ev.id)
                    break

            if event is None:
                break

            activity_type = random.choice(_ACTIVITY_TYPES)
            skill = event.skills.split(",")[0].strip() if event.skills else "general"
            explanation = random.choice(_GROWTH_EXPLANATIONS).replace("{skill}", skill)

            activities.append({
                "event_id": event.id,
                "title": event.title,
                "type": activity_type,
                "time": f"{random.choice(['09:00', '10:00', '14:00', '18:00', '19:00'])}",
                "duration_hours": event.duration_hours or 2,
                "location": event.location,
                "explanation": explanation,
                "category": event.category,
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
    events: list[Event],
    goal: str,
    weeks: int = 4,
) -> list[dict]:
    """Generate a week-by-week learning roadmap towards a goal."""
    goal_emb = _hash_embedding(goal)
    user_interests = getattr(user, "interests", "")

    # Score events by relevance to goal
    scored = []
    for ev in events:
        if ev.is_cancelled:
            continue
        ev_emb = _hash_embedding(_event_text(ev))
        score = _cosine_similarity(goal_emb, ev_emb)
        scored.append((ev, score))
    scored.sort(key=lambda x: x[1], reverse=True)

    roadmap = []
    used = set()
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
        week_events = []

        # Pick 2-3 events per week
        for _ in range(random.randint(2, 3)):
            for ev, score in scored:
                if ev.id not in used:
                    used.add(ev.id)
                    week_events.append(ev)
                    break

        roadmap.append({
            "week": week_num,
            "title": f"Week {week_num}: {focus}",
            "events": week_events,
            "focus": focus,
        })

    return roadmap


# ── AI Substitute Finder ───────────────────────────────────────────────────────

def find_substitutes(
    target_event: Event,
    all_events: list[Event],
    limit: int = 5,
) -> list[dict]:
    """Find alternative events that teach similar skills."""
    target_skills = set(s.strip().lower() for s in target_event.skills.split(",") if s.strip())
    target_emb = _hash_embedding(_event_text(target_event))

    alternatives = []
    for ev in all_events:
        if ev.id == target_event.id or ev.is_cancelled:
            continue

        ev_skills = set(s.strip().lower() for s in ev.skills.split(",") if s.strip())
        skill_overlap = target_skills & ev_skills
        skill_match_pct = len(skill_overlap) / len(target_skills) * 100 if target_skills else 0

        ev_emb = _hash_embedding(_event_text(ev))
        semantic_sim = _cosine_similarity(target_emb, ev_emb)

        score = 0.6 * skill_match_pct / 100 + 0.4 * semantic_sim

        if score > 0.15:
            if ev.price_sgd < target_event.price_sgd:
                reason = f"This {ev.price_sgd == 0 and 'free' or 'more affordable'} event covers {int(skill_match_pct)}% of the same skills."
            else:
                reason = f"Similar event available {ev.date and 'within the same timeframe' or 'soon'}. Covers {int(skill_match_pct)}% of overlapping topics."

            alternatives.append({
                "event": ev,
                "match_score": round(score, 3),
                "matched_skills": [s.strip() for s in ev.skills.split(",") if s.strip().lower() in skill_overlap][:4],
                "reason": reason,
            })

    alternatives.sort(key=lambda x: x["match_score"], reverse=True)
    return alternatives[:limit]


# ── AI Auto Listing Generator ──────────────────────────────────────────────────

def generate_listing(input_text: str) -> dict:
    """Generate a complete event listing from a description or URL."""
    text_lower = input_text.lower()

    # Detect category from keywords
    category_map = {
        "ai": ["ai", "machine learning", "ml", "neural", "deep learning", "llm", "gpt", "model"],
        "software engineering": ["code", "programming", "software", "developer", "engineering", "web", "app", "api", "react", "python", "javascript"],
        "cybersecurity": ["security", "hacking", "cyber", "penetration", "vulnerability", "encryption"],
        "entrepreneurship": ["startup", "founder", "business", "entrepreneur", "venture", "pitch"],
        "marketing": ["marketing", "seo", "ads", "brand", "content", "social media", "growth"],
        "finance": ["finance", "invest", "trading", "crypto", "banking", "fintech", "wealth"],
        "design": ["design", "ui", "ux", "figma", "creative", "art", "branding"],
        "leadership": ["leader", "management", "executive", "team", "strategy", "ceo"],
        "public speaking": ["speaking", "presentation", "toastmasters", "speech", "pitch", "communication"],
        "networking": ["network", "meetup", "mixer", "connect", "community"],
        "volunteering": ["volunteer", "community service", "charity", "give back", "social impact"],
        "sports": ["sport", "running", "fitness", "yoga", "climbing", "swimming", "health"],
        "hobbies": ["hobby", "craft", "cooking", "photography", "music", "game", "art"],
        "career development": ["career", "resume", "interview", "job", "upskilling", "professional"],
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
    title = first_line if len(first_line) > 10 else f"{detected_category} Workshop: {first_line}"

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
        "description": input_text[:500] if len(input_text) > 100 else f"Join us for an engaging {detected_category.lower()} event. {input_text}",
        "category": detected_category,
        "tags": tags[:6],
        "skills": all_skills[:6],
        "seo_keywords": [f"{detected_category.lower()} Singapore", f"{detected_category.lower()} workshop", f"{tags[0]} course" if tags else "workshop Singapore"],
        "difficulty": difficulty,
        "recommended_audience": f"Professionals interested in {detected_category.lower()}",
        "duration_hours": 4.0 if "workshop" in text_lower else 8.0 if "bootcamp" in text_lower else 3.0,
        "price_suggestion_sgd": 0.0 if "free" in text_lower else 50.0 if "beginner" in text_lower else 150.0,
    }


# ── AI Multilingual Chatbot ────────────────────────────────────────────────────

_TRANSLATIONS = {
    "en": {
        "greeting": "Hello! I'm your Nexa AI assistant. I can help you find events, plan your learning journey, or answer questions about courses and workshops. How can I help you today?",
        "default": "I'd be happy to help you with that! Based on your interests, I'd recommend exploring our upcoming events in {category}. Would you like me to generate a personalised recommendation?",
    },
    "zh": {
        "greeting": "你好！我是您的 Nexa AI 助手。我可以帮助您查找活动、规划学习路径，或回答有关课程和研讨会的问题。今天我能帮您什么？",
        "default": "我很乐意帮助您！根据您的兴趣，我建议您探索我们在{category}领域的即将到来的活动。您想让我生成个性化推荐吗？",
    },
    "ms": {
        "greeting": "Hai! Saya pembantu AI Nexa anda. Saya boleh membantu anda mencari acara, merancang perjalanan pembelajaran, atau menjawab soalan tentang kursus dan bengkel. Bagaimana saya boleh membantu anda hari ini?",
        "default": "Saya dengan senang hati membantu anda! Berdasarkan minat anda, saya mengesyorkan meneroka acara akan datang dalam {category}. Adakah anda mahu saya menjana cadangan peribadi?",
    },
    "ta": {
        "greeting": "வணக்கம்! நான் உங்கள் Nexa AI உதவியாளர். நிகழ்வுகளைக் கண்டறிய, கற்றல் பயணத்தைத் திட்டமிட அல்லது பாடநெறிகள் பற்றிய கேள்விகளுக்கு பதிலளிக்க உதவ முடியும். இன்று நான் எப்படி உதவ முடியும்?",
        "default": "உங்களுக்கு உதவ நான் மகிழ்ச்சியடைகிறேன்! உங்கள் ஆர்வங்களின் அடிப்படையில், {category} இல் வரவிருக்கும் நிகழ்வுகளை ஆராய பரிந்துரைக்கிறேன்.",
    },
}

_RESPONSE_TEMPLATES = {
    "event": "Based on your interests, here are some great upcoming events:\n\n{events}\n\nWould you like more details about any of these?",
    "journey": "I can generate a personalised learning journey for you! What's your goal? For example:\n- Become an AI Product Manager\n- Transition to cybersecurity\n- Build leadership skills\n\nTell me your goal and I'll create a week-by-week roadmap.",
    "plan": "I can create a personalised {days}-day growth plan for you. What areas would you like to focus on? I'll consider your interests, availability, and budget.",
    "general": "That's a great question! Here's what I can help with:\n\n1. **Find events** - Search and get AI recommendations\n2. **Learning journey** - Generate a roadmap to your goal\n3. **Growth plan** - Get a 7/14/30 day personalised plan\n4. **Substitute finder** - Find alternatives for full/cancelled events\n\nWhat would you like to explore?",
}


def chat_response(message: str, language: str = "en", user: "object" = None) -> dict:
    """Generate AI chatbot response with multilingual support."""
    lang = language if language in _TRANSLATIONS else "en"
    msg_lower = message.lower()

    # Detect intent
    if any(w in msg_lower for w in ["hello", "hi", "hey", "你好", "hai", "வணக்கம்"]):
        return {"reply": _TRANSLATIONS[lang]["greeting"], "language": lang}

    if any(w in msg_lower for w in ["event", "find", "search", "recommend", "活动", "cari", "நிகழ்வு"]):
        category = "Technology" if user is None else getattr(user, "interests", "Technology").split(",")[0].strip()
        reply = _RESPONSE_TEMPLATES["event"].replace("{events}", f"• AI Fundamentals Bootcamp\n• Generative AI Workshop\n• {category} Networking Night")
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

def generate_mock_analytics(event: Event) -> dict:
    """Generate realistic mock analytics for an event."""
    base_views = (event.attendees_count or 20) * random.randint(8, 15)
    base_regs = event.attendees_count or random.randint(15, 50)

    return {
        "event_id": event.id,
        "title": event.title,
        "views": base_views,
        "registrations": base_regs,
        "attendance_rate": round(random.uniform(0.65, 0.92), 2),
        "avg_rating": round(random.uniform(3.8, 4.9), 1),
        "demographics": {
            "age_groups": {"18-24": 15, "25-34": 40, "35-44": 30, "45+": 15},
            "gender": {"Male": 55, "Female": 42, "Other": 3},
            "industries": {"Technology": 35, "Finance": 20, "Education": 15, "Healthcare": 10, "Other": 20},
        },
    }


def generate_organiser_dashboard_stats(events: list[Event]) -> dict:
    """Generate mock dashboard stats for an organiser."""
    total_attendees = sum(e.attendees_count for e in events)
    upcoming = sum(1 for e in events if e.date and e.date > datetime.now(timezone.utc))

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
        "total_events": len(events),
        "total_attendees": total_attendees,
        "avg_rating": round(random.uniform(4.0, 4.8), 1),
        "upcoming_events": upcoming,
        "revenue_sgd": round(total_attendees * random.uniform(25, 75), 0),
        "monthly_growth": months,
    }
