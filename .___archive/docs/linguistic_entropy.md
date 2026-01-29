This is the complete technical blueprint for constructing **Uncertainty Entropy** (specifically **Shannon Entropy of the Uncertainty Distribution**).

This metric answers a different question than your current count.

* **LM Count:** "How *much* uncertainty is there?" (Quantity).
* **Entropy:** "How *diffused* is the uncertainty?" (Quality).

If a CEO is worried about **one specific thing** (e.g., "tariffs"), the entropy is **Low** (Focused).
If a CEO is throwing a **word salad** of different vague terms to hide the truth, the entropy is **High** (Diffused). High entropy flattens the Quantum Potential well.

Here is the construction from start to finish.

### Phase 1: The Theoretical Logic

We are not calculating the entropy of the whole document. That just measures vocabulary richness.
We are calculating the **Entropy of the Uncertainty Bag**.

1. **Isolate:** Throw away all words *except* those in the Loughran-McDonald (LM) Uncertainty Dictionary.
2. **Vectorize:** Count the frequency of each remaining unique uncertainty word.
3. **Compute:** Calculate how "flat" this histogram is.

### Phase 2: The Step-by-Step Algorithm

#### Step 1: Pre-processing (The Filter)

Take the raw Q&A text.

* **Tokenize:** Split into words.
* **Lemmatize:** Convert "doubting", "doubted", "doubts"  "doubt". (Crucial so you don't artificially inflate entropy).
* **Filter:** Keep **only** words found in the LM Uncertainty Dictionary.
* *Result:* `['volatility', 'risk', 'volatility', 'unsure', 'fluctuation', 'risk']`



#### Step 2: Probability Distribution ()

Create a frequency distribution of these words.
Let  be the total count of uncertainty words found.
Let  be the count of specific unique word .

* *Example:* If "volatility" appears 5 times and total uncertainty words is 10, then .

#### Step 3: Shannon Entropy Calculation ()

Plug the probabilities into the Shannon formula:

*  is the number of *unique* uncertainty words used.
*  is the natural logarithm.

#### Step 4: Normalization (Crucial)

You must normalize this score. If a CEO speaks for 1 hour, their entropy will naturally be higher than a CEO who speaks for 5 minutes, simply because they had more chances to use different words.
We use **Normalized Entropy ()**:

* Range: 0 to 1.
* **0:** The CEO used the *same* uncertainty word over and over. (Hyper-focused).
* **1:** The CEO used every uncertainty word in their vocabulary exactly once. (Maximum diffusion/confusion).

---

### Phase 3: A Concrete Example

Imagine two CEOs. Both use exactly **4 uncertainty words**. Your current LM Count method sees them as **identical**. Entropy sees them as **opposites**.

**CEO A (The Honest One):**
*"The **risk** of the merger is high. This **risk** is our main focus. We manage this **risk** daily. The **risk** is priced in."*

* Bag: `[risk, risk, risk, risk]`
* Unique words: 1 ("risk").
* Probability: .
* Entropy: .
* **Result:** **Zero Entropy.** (The market knows exactly what the problem is. The Quantum Potential Well is steep/stable).

**CEO B (The Vague Talker):**
*"We see **volatility** in Asia. There is **ambiguity** in pricing. The **fluctuation** is concerning. We are **unsure** of the outcome."*

* Bag: `[volatility, ambiguity, fluctuation, unsure]`
* Unique words: 4.
* Probability:  for each.
* Entropy: .
* **Result:** **High Entropy.** (The market is confused about *what* the problem is. The Quantum Potential Well flattens. Tunneling is likely).

