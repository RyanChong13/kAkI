import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUpskillingPlan } from '../api/client';
import { CourseSuggestion } from '../types';

const UpskillingPage: React.FC = () => {
  const [goal, setGoal] = useState('');
  const [time, setTime] = useState('');
  const [cost, setCost] = useState('');
  const [scope, setScope] = useState('');
  const [courses, setCourses] = useState<CourseSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<string>('');
  const navigate = useNavigate();

  const handlePlan = async () => {
    setLoading(true);
    try {
      const res = await getUpskillingPlan({ goal, time, cost, scope });
      setCourses(res.data.course_suggestions || []);
    } catch {
      // ignore
    }
    setLoading(false);
  };

  const handleContinueToGrants = () => {
    if (selectedCourse) {
      navigate(`/grants?course=${encodeURIComponent(selectedCourse)}`);
    }
  };

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', padding: 24 }}>
      <h1>Upskilling Planner</h1>
      <p>Describe your learning goal and constraints to get personalised course recommendations.</p>

      {courses.length === 0 && (
        <div>
          <div style={{ marginBottom: 12 }}>
            <label>What do you want to achieve?</label>
            <textarea value={goal} onChange={e => setGoal(e.target.value)} rows={3}
              style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
              placeholder="e.g. Transition into a data analyst role" />
          </div>
          <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
            <div style={{ flex: 1 }}>
              <label>Time available</label>
              <input value={time} onChange={e => setTime(e.target.value)}
                style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
                placeholder="e.g. 3 months" />
            </div>
            <div style={{ flex: 1 }}>
              <label>Budget</label>
              <input value={cost} onChange={e => setCost(e.target.value)}
                style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
                placeholder="e.g. Under $1000" />
            </div>
            <div style={{ flex: 1 }}>
              <label>Scope</label>
              <input value={scope} onChange={e => setScope(e.target.value)}
                style={{ display: 'block', width: '100%', padding: 8, marginTop: 4 }}
                placeholder="e.g. Data analysis, Python" />
            </div>
          </div>
          <button onClick={handlePlan} disabled={loading || !goal}
            style={{ padding: '10px 24px' }}>
            {loading ? 'Generating...' : 'Get Course Recommendations'}
          </button>
        </div>
      )}

      {courses.length > 0 && (
        <div>
          <h3>Recommended Courses</h3>
          <p>Select a course to see matching grants.</p>
          {courses.map((c, i) => (
            <div key={i} style={{
              padding: 16, border: '1px solid #ddd', borderRadius: 8, marginBottom: 12,
              cursor: 'pointer',
              background: selectedCourse === c.name ? '#e3f2fd' : '#fff',
            }} onClick={() => setSelectedCourse(c.name)}>
              <h4 style={{ margin: '0 0 4px' }}>{c.name}</h4>
              <p style={{ margin: '2px 0' }}><strong>Provider:</strong> {c.provider}</p>
              <p style={{ margin: '2px 0' }}><strong>Duration:</strong> {c.duration}</p>
              <p style={{ margin: '2px 0' }}><strong>Cost:</strong> {c.cost}</p>
              <p style={{ margin: '2px 0' }}><strong>Skill gap:</strong> {c.skill_gap_addressed}</p>
            </div>
          ))}
          <button onClick={handleContinueToGrants} disabled={!selectedCourse}
            style={{ padding: '10px 24px', marginTop: 8 }}>
            Find Matching Grants
          </button>
        </div>
      )}
    </div>
  );
};

export default UpskillingPage;
