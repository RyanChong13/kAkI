from app.models import Course, CourseSource, Job
from app.services.matching_service import match_courses, match_jobs


def make_job(**overrides) -> Job:
    defaults = dict(
        id=1,
        external_id="job-x",
        source="seeded",
        title="Data Analyst",
        company="Test Co",
        category="Data & Analytics",
        skills_required="SQL, Python, Tableau",
        salary_min_sgd=4000,
        salary_max_sgd=5000,
    )
    defaults.update(overrides)
    return Job(**defaults)


def make_course(**overrides) -> Course:
    defaults = dict(
        id=1,
        external_id="c-x",
        source=CourseSource.SKILLSFUTURE,
        title="Data Analytics with Python",
        provider="NTUC LearningHub",
        category="Data & Analytics",
        description="Learn Python and Pandas for data analysis.",
        price_sgd=1800,
        skills="Python, Pandas, Data Analysis",
    )
    defaults.update(overrides)
    return Course(**defaults)


class TestMatchJobs:
    def test_ranks_higher_skill_overlap_first(self):
        strong_match = make_job(id=1, skills_required="SQL, Python, Tableau")
        weak_match = make_job(id=2, skills_required="SQL, Java, Kubernetes")

        results = match_jobs(user_skills=["SQL", "Python", "Tableau"], jobs=[weak_match, strong_match])

        assert results[0][0].id == 1
        assert results[0][1] > results[1][1]

    def test_matched_skills_are_reported(self):
        job = make_job(skills_required="SQL, Python, Tableau")
        results = match_jobs(user_skills=["python", "sql"], jobs=[job])

        job_out, score, matched = results[0]
        assert set(matched) == {"SQL", "Python"}
        assert score == round(2 / 3, 3)

    def test_falls_back_to_unscored_list_when_no_overlap(self):
        job = make_job(skills_required="Welding, Forklift Operation")
        results = match_jobs(user_skills=["Python"], jobs=[job])

        assert len(results) == 1
        assert results[0][1] == 0.0

    def test_jobs_without_skills_required_are_skipped_from_scored_matches(self):
        job_no_skills = make_job(skills_required="")
        job_with_skills = make_job(id=2, skills_required="Python")

        results = match_jobs(user_skills=["Python"], jobs=[job_no_skills, job_with_skills])

        assert len(results) == 1
        assert results[0][0].id == 2


class TestMatchCourses:
    def test_keyword_overlap_with_goal_text_boosts_score(self):
        python_course = make_course(id=1, title="Data Analytics with Python", skills="Python, Pandas")
        design_course = make_course(id=2, title="Graphic Design Basics", category="Design", skills="Photoshop")

        results = match_courses(
            goal_text="I want to learn Python for data analytics",
            scope="",
            user_skills=[],
            courses=[design_course, python_course],
        )

        assert results[0][0].id == 1

    def test_respects_max_cost_filter(self):
        cheap = make_course(id=1, price_sgd=500)
        expensive = make_course(id=2, price_sgd=5000)

        results = match_courses(goal_text="python", scope="", user_skills=[], courses=[cheap, expensive], max_cost_sgd=1000)

        ids = [c.id for c, _, _ in results]
        assert 2 not in ids

    def test_empty_goal_falls_back_to_cost_filtered_list_not_crash(self):
        course = make_course()
        results = match_courses(goal_text="", scope="", user_skills=[], courses=[course])
        assert len(results) == 1
