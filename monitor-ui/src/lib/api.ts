const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8142';

export interface Component {
  type: string;
  id: string;
  name?: string;
  description?: string;
}

export interface Trace {
  trace_id: string;
  name: string;
  status: string;
  start_time: string;
  duration_ms: number;
}

export interface Span {
  span_id: string;
  trace_id: string;
  name: string;
  status_code: string;
  duration_ms: number;
  attributes?: Record<string, any>;
}

export const api = {
  async getRegistry(): Promise<Component[]> {
    const res = await fetch(`${API_BASE_URL}/api/registry`);
    const data = await res.json();
    return data.components;
  },

  async getComponent(type: string, id: string): Promise<{ content: string }> {
    const res = await fetch(`${API_BASE_URL}/api/registry/${type}/${id}`);
    return res.json();
  },

  async upsertComponent(type: string, id: string, content: string): Promise<void> {
    await fetch(`${API_BASE_URL}/api/registry/${type}/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
  },

  async getTraces(): Promise<Trace[]> {
    const res = await fetch(`${API_BASE_URL}/api/traces`);
    const data = await res.json();
    return data.traces;
  },

  async getSpans(traceId: string): Promise<Span[]> {
    const res = await fetch(`${API_BASE_URL}/api/spans/${traceId}`);
    const data = await res.json();
    return data.spans;
  },

  async createJob(task: string): Promise<{ job_id: string; manifest: any }> {
    const res = await fetch(`${API_BASE_URL}/api/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task }),
    });
    return res.json();
  },

  async getArtifacts(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/artifacts`);
    return res.json();
  },

  getLogStreamUrl(jobId: string): string {
    return `${API_BASE_URL}/api/jobs/${jobId}/stream`;
  }
};
