Specification Blueprint: Master CEO Tenure Map Construction
Version: 1.0 Status: Draft Objective: Transform the raw "CEO Dismissal" dataset into a continuous, chronological "Master Tenure Map" that defines precise start and end dates for every CEO tenure. This map is the foundational "truth" source for assigning CEOs to conference calls in downstream fixed-effects analysis.

1. Data Source Definition
The process consumes the provided raw dataset (CSV). The following columns are critical for processing:

Entity Identifiers:

gvkey: The primary unique identifier for the Company.

coname: Company Name (used for validation/debugging).

exec_fullname: The CEO's full name.

co_per_rol: The unique Person ID (from ExecuComp). This is the primary identifier for the CEO entity.

Temporal Markers:

leftofc: The specific date the CEO left office (End Date).

Still There: A textual marker indicating if the CEO was active at the time of data collection (e.g., "17nov2020").

year: The fiscal year associated with the record (used for sorting if exact dates are ambiguous).

Status Indicators:

Interim & Co-CEO: Flags for non-standard tenure types.

tenure_no: Differentiates multiple distinct spells of the same CEO at the same company.

2. Processing Logic & Transformation Rules
The developer must implement a pipeline consisting of the following sequential stages:

Stage A: Data Cleaning and Normalization

Date Parsing:

Parse the leftofc column into a standard Date format (YYYY-MM-DD).

Parse the Still There column. If a date is present (e.g., "17nov2020"), treat this as the "Last Observed Active Date" but not a dismissal date.

Status Standardization:

Normalize the Interim & Co-CEO column to a standard boolean or categorical flag (e.g., is_interim, is_co_ceo). Treat nan as standard tenure.

Deduplication:

Identify and resolve duplicate records. If a Company (gvkey) + CEO (co_per_rol) + Tenure Number (tenure_no) combination appears multiple times, retain the record with the most complete date information.

Stage B: Timeline Reconstruction (The Chaining Logic) Context: The dataset explicitly provides Dismissal (End) dates but implies Start dates based on the sequence of events.

Grouping: Partition the data by Company (gvkey).

Sorting: Within each company, sort records chronologically. The primary sort key is leftofc (ascending). The secondary sort key is year (ascending) to handle cases where leftofc is missing or identical.

Start Date Inference (Chaining):

Iterate through the sorted records for each company.

Rule 1 (Sequential Tenure): The Start_Date of the current CEO is defined as the End_Date of the immediate predecessor plus one day.

Rule 2 (First Recorded CEO): For the first CEO in the dataset for a given company, the Start_Date is "Left Censored" (Unknown). It should be set to a default floor date (e.g., start of dataset coverage) or marked as NULL, depending on downstream strictness.

Rule 3 (Gaps): If there is a significant gap between the provided records (implying missing data), the inferred Start Date may be incorrect. Flag tenures where the implied Start Date is significantly separated from the record's year (e.g., > 2 years difference) for manual review.

Stage C: Active CEO Handling

If leftofc is NULL:

Check the Still There column.

If Still There indicates the CEO is active, set the End_Date to a specialized "Future/Active" sentinel value (e.g., 2100-01-01) or NULL. This ensures that when merging with conference calls, any call after the start date is successfully matched.

Stage D: Conflict Resolution

Co-CEOs: If Interim & Co-CEO indicates "Co-CEO", allow the time window to overlap with the peer CEO.

Interim: Flag these records. Downstream analysis (Equation 4) requires filtering out short-tenured interims (e.g., < 5 calls), so they must be preserved in the map but flagged.

3. Output Schema: The Master Tenure Map
The final output must be a relational table with the following structure. This table will serve as the "Join Target" for the earnings call data.

Field Name	Type	Description
company_id	Integer	The gvkey of the firm.
ceo_id	Integer	The co_per_rol unique identifier for the person.
ceo_name	String	exec_fullname for human readability.
tenure_start_date	Date	The derived start date (Predecessor End + 1).
tenure_end_date	Date	The explicit leftofc date. If active, set to NULL or Sentinel.
is_interim	Boolean	True if the tenure was flagged as Interim.
is_active	Boolean	True if the CEO was still in office at dataset end.
tenure_seq	Integer	The chronological order of this CEO for this firm (1, 2, 3...).

Export to Sheets

4. Acceptance Criteria
Continuity Check: For any given company, the tenure_start_date of CEO N must match tenure_end_date of CEO N-1 (+1 day), unless it is the first record.

Date Integrity: tenure_end_date must always be greater than or equal to tenure_start_date.

Coverage: Every valid row in the source CSV must have a corresponding entry in the Tenure Map.