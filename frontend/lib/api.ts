import {
  AnalysisRequest,
  AnalysisResponse,
  FeedbackRequest,
  FeedbackResponse,
  SampleCase,
} from './types';

// In browser, using relative path `/api/backend` works with Next.js rewrites.
// Fallback to explicit env var or default port 8000 if server-side.
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== 'undefined' ? '/api/backend' : 'http://127.0.0.1:8000/api/v1');

export class ApiError extends Error {
  statusCode: number;
  details?: any;

  constructor(message: string, statusCode: number, details?: any) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

/**
 * Submit promotional text and/or website link for authoritative risk analysis.
 */
export async function analyzeInvestment(request: AnalysisRequest): Promise<AnalysisResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
  } catch (err: any) {
    throw new ApiError(
      'Unable to connect to the risk analysis backend service. Please check that the Python server is running.',
      0,
      err
    );
  }

  if (!response.ok) {
    let errorData: any = {};
    try {
      errorData = await response.json();
    } catch {
      // Non-JSON response
    }
    const message =
      errorData.message ||
      errorData.detail ||
      (Array.isArray(errorData.details) ? errorData.details.join('; ') : null) ||
      `Analysis request failed with status ${response.status}`;
    throw new ApiError(message, response.status, errorData);
  }

  return response.json();
}

/**
 * Fetch educational benchmark sample cases.
 */
export async function fetchSampleCases(): Promise<SampleCase[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/sample-cases`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });
    if (!response.ok) {
      throw new Error(`Failed to load samples: ${response.status}`);
    }
    return response.json();
  } catch (err) {
    console.warn('Could not load sample cases from API:', err);
    return [];
  }
}

/**
 * Submit feedback on an analysis.
 */
export async function submitFeedback(feedback: FeedbackRequest): Promise<FeedbackResponse> {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(feedback),
  });

  if (!response.ok) {
    throw new Error('Failed to record feedback.');
  }

  return response.json();
}

/**
 * Check backend service health status.
 */
export async function checkBackendHealth(): Promise<{ status: string; service: string }> {
  try {
    const target = typeof window !== 'undefined' ? '/api/health' : 'http://127.0.0.1:8000/health';
    const response = await fetch(target);
    if (response.ok) {
      return response.json();
    }
    return { status: 'error', service: 'unknown' };
  } catch {
    return { status: 'unreachable', service: 'none' };
  }
}
