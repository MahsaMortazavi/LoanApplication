export interface Borrower {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  ssn: string;
  address_street: string;
  city: string;
  state: string;
  zip_code: string;
}

export interface ApplicationRequest {
  borrower: Borrower;
  requested_amount: string;
}

export interface ApplicationResponse {
  application_id: string;
  decision: "approved" | "denied";
  offer?: {
    total_amount: string;
    interest_rate: number;
    term_months: number;
    monthly_payment: string;
  };
  reason?: string;
}

// Validation helper
function validatePhoneNumber(phone: string): boolean {
  if (!phone) return true;
  const cleaned = phone.replace(/\D/g, "");
  return cleaned.length === 10;
}

export async function createApplication(req: ApplicationRequest): Promise<ApplicationResponse> {
  // Validate phone number before sending to API
  if (req.borrower.phone && !validatePhoneNumber(req.borrower.phone)) {
    const error: any = new Error("Invalid phone number format. Please use a 10-digit US phone number.");
    error.status = 400;
    throw error;
  }

  try {
    const response = await fetch("/api/applications", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    });

    // Handle non-OK responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      const error: any = new Error(
        errorData.message ||
        errorData.error ||
        errorData.detail ||
        `Request failed with status ${response.status}`
      );
      error.status = response.status;
      error.response = response;
      throw error;
    }

    return await response.json();
  } catch (err: any) {
    if (err.status) {
      throw err;
    }

    // Network error or other unexpected error
    const error: any = new Error("Network error. Please check your connection and try again.");
    error.status = 500;
    throw error;
  }
}
