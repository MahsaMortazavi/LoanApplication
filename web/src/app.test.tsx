// app.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';
import * as api from './api';

// Mock the API module
vi.mock('./api');

describe('Loan Application Form', () => {
  it('renders the form with all fields', () => {
    render(<App />);

    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/ssn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/street/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/city/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/state/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/zip/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/requested amount/i)).toBeInTheDocument();
  });

  it('shows validation errors when submitting empty form', async () => {
    render(<App />);

    const submitButton = screen.getByRole('button', { name: /submit application/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please fix the highlighted fields/i)).toBeInTheDocument();
    });
  });

  it('validates SSN format', async () => {
    render(<App />);

    const ssnInput = screen.getByLabelText(/ssn/i);
    // Enter incomplete SSN (only 8 digits instead of 9)
    fireEvent.change(ssnInput, { target: { value: '12345678' } });
    fireEvent.blur(ssnInput);

    const submitButton = screen.getByRole('button', { name: /submit application/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      // Look for the error message that shows up when SSN is invalid
      const errorMessage = screen.getByText(/format/i);
      expect(errorMessage).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    render(<App />);

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);

    const submitButton = screen.getByRole('button', { name: /submit application/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    });
  });

  it('formats phone number as user types', () => {
    render(<App />);

    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(phoneInput, { target: { value: '5551234567' } });

    expect(phoneInput).toHaveValue('(555) 123-4567');
  });

  it('formats SSN as user types', () => {
    render(<App />);

    const ssnInput = screen.getByLabelText(/ssn/i);
    fireEvent.change(ssnInput, { target: { value: '123456789' } });

    // Should auto-format to XXX-XX-XXXX
    expect(ssnInput).toHaveValue('123-45-6789');
  });

  it('submits form successfully and shows approval', async () => {
    const mockResponse = {
      application_id: 'test-123',
      decision: 'approved' as const,
      offer: {
        total_amount: '25000.00',
        interest_rate: 10,
        term_months: 36,
        monthly_payment: '806.67'
      }
    };

    vi.mocked(api.createApplication).mockResolvedValueOnce(mockResponse);

    render(<App />);

    // Fill in all required fields
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.change(screen.getByLabelText(/ssn/i), { target: { value: '123-45-6789' } });
    fireEvent.change(screen.getByLabelText(/street/i), { target: { value: '123 Main St' } });
    fireEvent.change(screen.getByLabelText(/city/i), { target: { value: 'New York' } });
    fireEvent.change(screen.getByLabelText(/state/i), { target: { value: 'NY' } });
    fireEvent.change(screen.getByLabelText(/zip/i), { target: { value: '10001' } });

    // Submit form
    const submitButton = screen.getByRole('button', { name: /submit application/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/approved/i)).toBeInTheDocument();
      expect(screen.getByText(/\$25,000\.00/i)).toBeInTheDocument();
      expect(screen.getByText(/10%/i)).toBeInTheDocument();
    });
  });

  it('shows error message on 500 error', async () => {
    const mockError = { status: 500, message: 'Server error' };
    vi.mocked(api.createApplication).mockRejectedValueOnce(mockError);

    render(<App />);

    // Fill in required fields
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.change(screen.getByLabelText(/ssn/i), { target: { value: '123-45-6789' } });
    fireEvent.change(screen.getByLabelText(/street/i), { target: { value: '123 Main St' } });
    fireEvent.change(screen.getByLabelText(/city/i), { target: { value: 'New York' } });
    fireEvent.change(screen.getByLabelText(/state/i), { target: { value: 'NY' } });
    fireEvent.change(screen.getByLabelText(/zip/i), { target: { value: '10001' } });

    const submitButton = screen.getByRole('button', { name: /submit application/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/something went wrong.*try again later/i)).toBeInTheDocument();
    });
  });

  it('clears previous result when new submission has validation errors', async () => {
    const mockResponse = {
      application_id: 'test-123',
      decision: 'approved' as const,
      offer: {
        total_amount: '25000.00',
        interest_rate: 10,
        term_months: 36,
        monthly_payment: '806.67'
      }
    };

    vi.mocked(api.createApplication).mockResolvedValueOnce(mockResponse);

    render(<App />);

    // Submit valid form first
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });
    fireEvent.change(screen.getByLabelText(/ssn/i), { target: { value: '123-45-6789' } });
    fireEvent.change(screen.getByLabelText(/street/i), { target: { value: '123 Main St' } });
    fireEvent.change(screen.getByLabelText(/city/i), { target: { value: 'New York' } });
    fireEvent.change(screen.getByLabelText(/state/i), { target: { value: 'NY' } });
    fireEvent.change(screen.getByLabelText(/zip/i), { target: { value: '10001' } });

    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      expect(screen.getByText(/approved/i)).toBeInTheDocument();
    });

    // Now clear SSN and submit again (invalid)
    fireEvent.change(screen.getByLabelText(/ssn/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /submit application/i }));

    await waitFor(() => {
      // Previous approval should be cleared
      expect(screen.queryByText(/\$25,000\.00/i)).not.toBeInTheDocument();
      expect(screen.getByText(/please fix the highlighted fields/i)).toBeInTheDocument();
    });
  });

  it('resets form when reset button is clicked', async () => {
    render(<App />);

    // Fill in some fields
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'john@example.com' } });

    // Click reset
    const resetButton = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetButton);

    // Fields should be empty
    expect(screen.getByLabelText(/first name/i)).toHaveValue('');
    expect(screen.getByLabelText(/email/i)).toHaveValue('');
  });
});