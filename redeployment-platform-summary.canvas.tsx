import {
  Stack, H1, H2, Text, Divider, Grid, Pill,
  Callout, Card, CardHeader, CardBody, MetricsGrid, Timeline, Row, Table,
} from 'qoder/canvas';
import type { TimelineEvent, MetricItem } from 'qoder/canvas';

const platformMetrics: MetricItem[] = [
  { label: 'Total Files', value: '65', description: 'Backend + Frontend' },
  { label: 'API Endpoints', value: '15', description: 'Across 7 routers' },
  { label: 'AI Agents', value: '5', description: '4 LLM + 1 Rules Engine' },
  { label: 'DB Models', value: '7', description: 'With relationships + JSON cols' },
  { label: 'Frontend Pages', value: '10', description: 'Full user journey' },
  { label: 'Integration Tests', value: '22', description: 'Across 4 test files' },
];

const buildTimeline: TimelineEvent[] = [
  { id: 'p1', timestamp: 'Phase 1', title: 'Backend Scaffolding', description: 'FastAPI + PostgreSQL + SQLAlchemy + Alembic migrations, project structure, config, auth utilities.', state: 'completed', tone: 'success' },
  { id: 'p2', timestamp: 'Phase 2', title: 'Database Models', description: 'User, Resume, FlowSession, JobSuggestion, Grant, GrantRecommendation, Application models with enums and relationships.', state: 'completed', tone: 'success' },
  { id: 'p3', timestamp: 'Phase 3', title: 'AI Agents', description: 'Resume Parser, Job Recommender, Upskilling Planner (Claude Sonnet), Grant Matcher (rules engine), Mass Apply (two-step).', state: 'completed', tone: 'success' },
  { id: 'p4', timestamp: 'Phase 4', title: 'API Routes', description: 'Auth, Resume, Flow, Jobs, Grants, Upskilling, Apply routers with JWT auth and Pydantic validation.', state: 'completed', tone: 'success' },
  { id: 'p5', timestamp: 'Phase 5', title: 'Flow State Machine', description: 'Max 2 rounds enforced, redeployment-to-upskilling redirect, terminal exit state with external resources.', state: 'completed', tone: 'success' },
  { id: 'p6', timestamp: 'Phase 6', title: 'Frontend', description: 'React + Vite + TypeScript, 10 pages covering full user journey with auth context and API client.', state: 'completed', tone: 'success' },
  { id: 'p7', timestamp: 'Phase 7', title: 'Integration Tests', description: 'Grant matcher, flow state machine, mass apply, and auth API tests. 22 tests total.', state: 'completed', tone: 'success' },
  { id: 'p8', timestamp: 'Phase 8', title: 'Audit and Fixes', description: 'Unused imports removed, response_model annotations fixed, preview flow wired, round 2 dashboard support added.', state: 'completed', tone: 'success' },
];

const agentRows = [
  ['Agent 1: Resume Parser', 'Claude Sonnet', 'raw resume text', '[{skill, years, source}]', 'Retry once on malformed JSON'],
  ['Agent 2: Job Recommender', 'Claude Sonnet', 'structured skills + survey', '{job_suggestions: [...]}', 'No reassurance language'],
  ['Agent 3: Upskilling Planner', 'Claude Sonnet', 'goal + constraints + skills', '{course_suggestions: [...]}', 'Time/Cost/Scope constraints'],
  ['Agent 4: Grant Matcher', 'Rules Engine (no LLM)', 'user profile + course', '{eligible_grants: [...]}', 'Deterministic eligibility filter'],
  ['Agent 5: Mass Apply', 'Two-step service', 'selected targets + resume', 'audit snapshot', 'Server-side confirmation required'],
];

const specRows = [
  ['Account creation + path selection', 'POST /auth/register + POST /flow/start', 'Satisfied'],
  ['Resume upload + AI parsing (PDF)', 'POST /resume/upload (pypdf + Agent 1)', 'Satisfied'],
  ['Job recommendations + feedback loop', 'POST /jobs/recommend + POST /flow/feedback', 'Satisfied'],
  ['Liked -> mass-apply (two-step)', 'POST /apply/preview + POST /apply/confirm', 'Satisfied'],
  ['Disliked -> upskilling redirect', 'flow_service.handle_job_feedback', 'Satisfied'],
  ['Upskilling: goal + constraints -> courses', 'POST /upskilling/plan (Agent 3)', 'Satisfied'],
  ['Grant matching (NOT LLM)', 'POST /grants/match (Agent 4 rules engine)', 'Satisfied'],
  ['Max 2 rounds, no 3rd round', 'MAX_ROUNDS = 2 in flow_service.py', 'Satisfied'],
  ['Exit state: terminal + neutral copy', 'FlowStatus.exited + WSG/e2i links', 'Satisfied'],
  ['Rate/volume limit on batch apply', 'MAX_BATCH_SIZE = 20 in config.py', 'Satisfied'],
  ['Audit snapshot on confirmation', 'Application.snapshot JSON column', 'Satisfied'],
];

const fileBreakdownRows = [
  ['Backend Python', '40', 'Models, agents, routers, services, tests, config'],
  ['Frontend TSX/TS', '16', 'Pages, API client, context, types, config'],
  ['Config/Data', '9', 'JSON seed, env, alembic, package.json, HTML'],
];

export default function RedeploymentPlatformSummary() {
  return (
    <Stack gap={24}>
      <H1>Redeployment / Upskilling Platform</H1>
      <Text tone="secondary">
        Full-stack implementation of the end-to-end user journey from account creation through
        AI-powered resume parsing, path selection, job/course recommendations, and mass-apply
        for jobs or grants. Built from spec to working prototype.
      </Text>

      <MetricsGrid items={platformMetrics} columns={3} variant="card" />

      <Divider />

      <H2>Tech Stack</H2>
      <Grid columns={2} gap={16}>
        <Card size="md">
          <CardHeader>Backend</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Row gap={8} wrap>
                <Pill tone="primary">Python 3.11+</Pill>
                <Pill tone="primary">FastAPI</Pill>
                <Pill tone="primary">SQLAlchemy</Pill>
                <Pill tone="primary">Alembic</Pill>
                <Pill tone="primary">PostgreSQL</Pill>
              </Row>
              <Text size="small" tone="secondary">
                JWT auth via python-jose + passlib/bcrypt. Anthropic SDK for Claude Sonnet agents.
                pypdf for PDF text extraction. Pydantic v2 for schema validation.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card size="md">
          <CardHeader>Frontend</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Row gap={8} wrap>
                <Pill tone="info">React 18</Pill>
                <Pill tone="info">Vite</Pill>
                <Pill tone="info">TypeScript</Pill>
                <Pill tone="info">React Router</Pill>
                <Pill tone="info">Axios</Pill>
              </Row>
              <Text size="small" tone="secondary">
                Auth context with JWT localStorage. API proxy via Vite dev server config.
                sessionStorage for mass-apply preview data between pages.
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Divider />

      <H2>AI Agent Architecture</H2>
      <Callout tone="info">
        All LLM agents use structured JSON I/O with schema validation and one retry on malformed output.
        The Grant Matcher is explicitly a rules engine, not an LLM agent, per spec requirement.
      </Callout>
      <Table
        headers={['Agent', 'Implementation', 'Input', 'Output', 'Key Constraint']}
        rows={agentRows}
        density="compact"
      />

      <Divider />

      <H2>Flow State Machine</H2>
      <Text>
        The core orchestration logic enforces a maximum of 2 rounds with proper path transitions
        and a terminal exit state. No third round is possible under any circumstance.
      </Text>
      <Grid columns={3} gap={12}>
        <Card size="sm">
          <CardHeader>Round 1</CardHeader>
          <CardBody>
            <Text size="small">
              Job Redeployment path. AI recommends jobs (Agent 2). User provides feedback.
              Liked: proceed to mass-apply. Disliked: redirect to upskilling.
            </Text>
          </CardBody>
        </Card>
        <Card size="sm">
          <CardHeader>Round 2 (Upskilling)</CardHeader>
          <CardBody>
            <Text size="small">
              Courses (Agent 3) + Grants (Agent 4) + re-run Agent 2 with updated skills.
              Liked: mass-apply. Disliked: terminal exit.
            </Text>
          </CardBody>
        </Card>
        <Card size="sm">
          <CardHeader>Exit State</CardHeader>
          <CardBody>
            <Text size="small">
              Terminal, not an error. Session logged as exited. Profile retained.
              Neutral UX copy with static links to WSG/e2i.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <Divider />

      <H2>Spec Compliance Audit</H2>
      <Table
        headers={['Acceptance Criterion', 'Implementation', 'Status']}
        rows={specRows}
        density="compact"
        rowTone={specRows.map(r => r[2] === 'Satisfied' ? 'positive' as const : 'caution' as const)}
      />

      <Divider />

      <H2>Build Phases</H2>
      <Timeline events={buildTimeline} density="compact" />

      <Divider />

      <H2>File Breakdown</H2>
      <Table
        headers={['Category', 'Count', 'Description']}
        rows={fileBreakdownRows}
        density="compact"
      />

      <Text tone="quaternary" size="small">
        Generated for Qoder goal completion report.
      </Text>
    </Stack>
  );
}
