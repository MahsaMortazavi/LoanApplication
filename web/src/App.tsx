import { useState, useEffect } from "react";
import { createApplication, type ApplicationRequest, type ApplicationResponse, type ApplicationsPage } from "./api";
import { currencyFmt, parseMoney, toMoneyString, formatSSN, validateEmail, required, twoLetterState } from "./format";
import "./styles.css";

const initBorrower = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  ssn: "",
  address_street: "",
  city: "",
  state: "",
  zip_code: "",
};

function formatPhone(value: string): string {
  const cleaned = value.replace(/\D/g, "");
  const limited = cleaned.slice(0, 10);
  if (limited.length <= 3) return limited;
  if (limited.length <= 6) return `(${limited.slice(0, 3)}) ${limited.slice(3)}`;
  return `(${limited.slice(0, 3)}) ${limited.slice(3, 6)}-${limited.slice(6)}`;
}

function validatePhone(phone: string): boolean {
  if (!phone) return true;
  const cleaned = phone.replace(/\D/g, "");
  return cleaned.length === 10;
}

export default function App() {
  const [borrower, setBorrower] = useState(initBorrower);
  const [amount, setAmount] = useState("25000.00");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ApplicationResponse | null>(null);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  function onBorrowerChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    let next = value;
    if (name === "ssn") next = formatSSN(value);
    if (name === "phone") next = formatPhone(value);
    if (name === "state") next = value.toUpperCase().slice(0, 2);
    setBorrower((b) => ({ ...b, [name]: next }));
  }

  function onAmountChange(e: React.ChangeEvent<HTMLInputElement>) {
    const cleaned = parseMoney(e.target.value);
    setAmount(cleaned);
  }

  function onBlur(e: React.FocusEvent<HTMLInputElement>) {
    setTouched((t) => ({ ...t, [e.target.name]: true }));
  }

  const errors = getErrors(borrower, amount);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(allFieldsTouched(borrower));
    setResult(null);

    if (Object.keys(errors).length) {
      setError("Please fix the highlighted fields.");
      return;
    }

    setLoading(true); setError(null);
    try {
      const payload: ApplicationRequest = {
        borrower,
        requested_amount: normalizeAmount(amount),
      };
      const resp = await createApplication(payload);
      setResult(resp);

    } catch (err: any) {
      setError(err.message ?? "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setBorrower(initBorrower);
    setAmount("25000.00");
    setResult(null);
    setError(null);
    setTouched({});
  }

  return (
    <div className="container">
      <h1>Loan Application</h1>

      <div className="app-layout">
        <form className="card" onSubmit={submit}>
          <Section title="Enter Your Information Please">
            <Row>
              <Field name="first_name" label="First name" value={borrower.first_name} onChange={onBorrowerChange} onBlur={onBlur} error={touched.first_name && errors.first_name} />
              <Field name="last_name"  label="Last name"  value={borrower.last_name}  onChange={onBorrowerChange} onBlur={onBlur} error={touched.last_name  && errors.last_name} />
            </Row>
            <Row>
              <Field name="email" label="Email" type="email" value={borrower.email} onChange={onBorrowerChange} onBlur={onBlur} error={touched.email && errors.email} />
              <Field name="phone" label="Phone" placeholder="(555) 123-4567" value={borrower.phone} onChange={onBorrowerChange} onBlur={onBlur} error={touched.phone && errors.phone} />
            </Row>
            <Row>
              <Field name="ssn" label="SSN" type="password" placeholder="123-45-6789" value={borrower.ssn} onChange={onBorrowerChange} onBlur={onBlur} error={touched.ssn && errors.ssn} autoComplete="off" />
              <Field name="address_street" label="Street" value={borrower.address_street} onChange={onBorrowerChange} onBlur={onBlur} error={touched.address_street && errors.address_street} />
            </Row>
            <Row>
              <Field name="city" label="City" value={borrower.city} onChange={onBorrowerChange} onBlur={onBlur} error={touched.city && errors.city} />
              <Field name="state" label="State" placeholder="NY" value={borrower.state} onChange={onBorrowerChange} onBlur={onBlur} error={touched.state && errors.state} />
              <Field name="zip_code" label="ZIP" value={borrower.zip_code} onChange={onBorrowerChange} onBlur={onBlur} error={touched.zip_code && errors.zip_code} />
            </Row>
          </Section>

          <Section>
            <Row>
              <Field name="requested_amount" label="Requested Amount" value={toMoneyString(amount)} onChange={onAmountChange} onBlur={onBlur} error={touched.requested_amount && errors.requested_amount} inputMode="decimal" />
            </Row>
          </Section>

          <div className="alert-container">
            {error && <Alert type="error">{error}</Alert>}
          </div>

          <div className="actions">
            <button type="submit" disabled={loading}>{loading ? "Submitting..." : "Submit Application"}</button>
            <button type="button" className="secondary" onClick={reset}>Reset</button>
          </div>
        </form>

        {result && (
          <div className="card result-card">
            <div className="result-header">
              <DecisionBadge decision={result.decision} />
            </div>

            {result.offer ? (
              <OfferCard total={result.offer.total_amount} rate={result.offer.interest_rate} term={result.offer.term_months} monthly={result.offer.monthly_payment} />
            ) : (
              <DeniedCard reason={result.reason ?? "Denied"} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function normalizeAmount(a: string) {
  const cleaned = parseMoney(a);
  return cleaned.includes(".") ? cleaned : `${cleaned}.00`;
}

function getErrors(b: typeof initBorrower, amount: string) {
  const errs: Record<string, string> = {};
  if (!required(b.first_name)) errs.first_name = "Required";
  if (!required(b.last_name))  errs.last_name = "Required";
  if (!validateEmail(b.email)) errs.email = "Invalid email";
  if (b.phone && !validatePhone(b.phone)) errs.phone = "10-digit phone required";
  if (!/^\d{3}-\d{2}-\d{4}$/.test(b.ssn)) errs.ssn = "Format: 123-45-6789";
  if (!required(b.address_street)) errs.address_street = "Required";
  if (!required(b.city)) errs.city = "Required";
  if (!twoLetterState(b.state)) errs.state = "2-letter code";
  if (!required(b.zip_code)) errs.zip_code = "Required";
  const n = parseFloat(amount);
  if (!(n > 0)) errs.requested_amount = "Enter a positive amount";
  return errs;
}

function allFieldsTouched(b: typeof initBorrower) {
  const names = ["first_name","last_name","email","phone","ssn","address_street","city","state","zip_code","requested_amount"];
  return Object.fromEntries(names.map(n => [n, true]));
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (<section><h2>{title}</h2>{children}</section>);
}

function Row({ children }: { children: React.ReactNode }) {
  return <div className="row">{children}</div>;
}

type FieldProps = React.InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string | false; };
function Field({ label, error, ...rest }: FieldProps) {
  return (
    <label className={`field ${error ? "has-error" : ""}`}>
      <span>{label}</span>
      <input {...rest} />
      <em>{error || '\u00A0'}</em>
    </label>
  );
}

function Alert({ type = "error", children }: { type?: "error" | "info"; children: React.ReactNode }) {
  return <div className={`alert ${type}`}>{children}</div>;
}

function DecisionBadge({ decision }: { decision: "approved" | "denied" }) {
  const ok = decision === "approved";
  return <span className={`badge ${ok ? "approved" : "denied"}`}>{ok ? "Approved" : "Denied"}</span>;
}

function OfferCard({ total, rate, term, monthly }: { total: string; rate: number; term: number; monthly: string }) {
  return (
    <div className="offer-card">
      <div><small>Total Amount</small><div>{currencyFmt.format(parseFloat(total))}</div></div>
      <div><small>APR</small><div>{rate}%</div></div>
      <div><small>Term</small><div>{term} months</div></div>
      <div><small>Monthly Payment</small><div>{currencyFmt.format(parseFloat(monthly))}</div></div>
    </div>
  );
}

function DeniedCard({ reason }: { reason: string }) {
  return (
    <div className="offer-card denied-card">
      <p>{reason}</p>
    </div>
  );
}