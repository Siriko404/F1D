
We have a massive list of conference calls where we know *what* was said (the uncertainty words), but we don't explicitly know *who* the CEO was at that exact moment. Since we are trying to measure a specific person's "communication style," knowing the company isn't enough—we have to know exactly which person was holding the microphone.

Here is the conceptual breakdown of what we are doing in Step 2:

### 1. Inputs (The Raw Materials)
We are starting with two completely separate "books" of information:
* **The "History Book" (Tenure Map):** This is a timeline of leadership. For every company, it tells us the exact reigns of their CEOs. For example: *"Steve Jobs ran Apple from Date A to Date B."* It defines the windows of time when a specific person was in charge.
* **The "Event Log" (Enriched Calls):** This is a list of every earnings call that ever happened. It knows the date of the call and the uncertainty score, but it doesn't know the CEO. It looks like: *"Apple had a call on January 25, 2010, and it was 15% uncertain."*

### 2. Process (The Time-Travel Match)
We are going to take every single event from the **Event Log** and cross-reference it with the **History Book**.

Imagine picking up one specific conference call record. We look at the date of that call. Then, we look at the timeline for that company. We ask: **"On this specific day, who was sitting in the CEO's chair?"**

* If the call happened on **Jan 25, 2010**, and the History Book says Steve Jobs was CEO from **1997 to 2011**, then that call belongs to Steve Jobs.
* We slap a "Steve Jobs" nametag on that call record.
* **The "Gap" Check:** If we find a call date that doesn't fit into *anyone's* timeline (maybe it was an interim CEO or a transition period we don't have data for), we mark it as "Unassigned." We don't guess; we just flag it.

### 3. Outputs (The "Tagged" Dataset)
The result is a new, enriched version of our Event Log. It looks exactly like the list of calls we started with, but now **every row has a specific Person ID attached to it.**

* **Why this matters:** Before this step, we could only calculate the average uncertainty for *Apple*.
* **After this step:** We can group all the calls tagged "Steve Jobs" (across his whole career) and calculate **Steve Jobs' personal average uncertainty**.

This output is the prerequisite for the "Fixed Effects" math. We cannot mathematically isolate the "person" from the "company" until we have successfully tagged every single call with the correct person's ID.