# Card Fraud Detection Policy

## Section 1: Transaction Amount Rules

### 1.1 High-Value Transactions
- **Transactions over €5,000 from new devices require manual review**
- Transactions over €10,000 require supervisor approval
- Any transaction over €50,000 requires executive sign-off
- Established customers (account age > 2 years) get increased thresholds

### 1.2 Micro-Transactions
- Transactions under €1 may indicate card verification attempts
- Multiple micro-transactions from same device within 24 hours is suspicious
- Legitimate merchants: subscription services, microservices

## Section 2: Geographic Risk Assessment

### 2.1 High-Risk Countries
**Tier 1 (Highest Risk):** NG, GH, VN, RU, CN
- **Risk Multiplier:** 3x
- **Additional Controls:** All transactions require context review
- **Exceptions:** Established customers (>18 months) can proceed with monitoring

**Tier 2 (Moderate Risk):** SG, JP, AE, RU, PK
- **Risk Multiplier:** 1.5x
- **Additional Controls:** Transactions over €1,000 flagged for review
- **New Device:** Automatic elevation to manual review

### 2.2 Domestic Transactions
- Lower risk baseline
- Focus on behavioral anomalies
- Trust established customer history

## Section 3: Device and Account Risk Factors

### 3.1 New Device Transactions
- **First 48 hours:** Elevated risk monitoring
- **First 7 days:** 2x risk multiplier
- **Combined with high-risk country:** Immediate escalation
- **Large amount + new device:** Manual review mandatory

### 3.2 Account Age Risk
| Account Age | Risk Level | Required Review |
|------------|-----------|-----------------|
| < 7 days | Critical | All transactions > €500 |
| 7-30 days | High | All transactions > €2,000 |
| 30-90 days | Elevated | All transactions > €5,000 |
| 90 days+ | Normal | Standard rules apply |

## Section 4: Velocity Rules

### 4.1 Transaction Velocity
- **3+ transactions in 10 minutes:** Flag for review (1x risk)
- **5+ transactions in 10 minutes:** Escalate immediately (3x risk)
- **10+ transactions in 1 hour:** Block account, escalate (5x risk)

### 4.2 Amount Velocity
- **Total > €10,000 in 24 hours for new customer:** Review required
- **Total > €20,000 in 24 hours:** Escalate immediately
- **Pattern change > 50% from customer average:** Monitor

## Section 5: Merchant Category Rules

### 5.1 High-Risk Merchant Categories
- **Crypto Exchanges, Money Transfer Services:** 2.5x risk multiplier
- **Electronics, Jewelry, Luxury Goods:** 1.5x risk multiplier
- **Unknown/Suspicious Merchant Codes:** Manual review required
- **Newly Registered Merchants (<30 days):** Additional verification

### 5.2 Low-Risk Merchant Categories
- **Utilities, Pharmacies, Groceries:** Baseline risk
- **Established Retailers:** Reduced scrutiny
- **Government Services:** Baseline risk

## Section 6: Decision Rules

### 6.1 Automatic Block Triggers
1. Transaction from Tier 1 high-risk country + new device + amount > €5,000
2. Account age < 7 days AND any transaction > €5,000 from non-US
3. Velocity > 10 transactions/hour from any channel
4. Multiple failed authentication attempts
5. Device fingerprint mismatch + amount > €3,000

### 6.2 Automatic Approve Triggers
1. Established customer (>2 years) with normal transaction pattern
2. Transaction matches customer historical behavior (amount, merchant, time)
3. Domestic transaction with card present
4. Transactions < €100 with established patterns

### 6.3 Manual Review Required
1. Transaction score between 40-70 (moderate risk)
2. Any high-amount transaction (> €5,000) with anomalies
3. First transaction of a new merchant
4. Transactions from new geographic locations

## Section 7: Risk Scoring Model

**Risk Score = Base Score + Adjustments**

- **Base Score:** 10 (low-risk transaction)
- **Geographic Adjustment:** +10 to +50 (based on country tier)
- **Device Adjustment:** +5 to +40 (age of device registration)
- **Account Adjustment:** +5 to +50 (account age)
- **Velocity Adjustment:** +5 to +40 (transaction frequency)
- **Amount Adjustment:** +5 to +30 (relative to customer average)
- **Merchant Adjustment:** +5 to +25 (category risk)

**Final Decision:**
- **Score 0-30:** APPROVE (Low Risk)
- **Score 30-60:** REVIEW (Moderate Risk - requires manual intervention)
- **Score 60-100:** ESCALATE (High Risk - escalate immediately)

## Section 8: Special Cases

### 8.1 Travel Transactions
- Customers traveling to declared destinations get reduced scrutiny
- Pre-authorization of travel improves approval rate
- Legitimate travel merchants (hotels, airlines) get lower risk weighting

### 8.2 Subscription Services
- Recurring transactions reduce risk
- Same merchant, same amount increases trust
- Failed subscriptions may indicate account compromise

### 8.3 Business Accounts
- Higher transaction thresholds
- More lenient velocity rules
- Focus on unusual merchant categories

## Section 9: Compliance and Escalation

### 9.1 Regulatory Requirements
- All high-risk transactions documented for audit
- Customer notification required for blocks > €2,000
- Manual reviews completed within 24 hours

### 9.2 Escalation Path
1. **Tier 1:** Automated system (rules-based)
2. **Tier 2:** ML model scoring
3. **Tier 3:** Manual analyst review
4. **Tier 4:** Senior analyst decision

## Section 10: Performance Targets

- **Accuracy:** > 95% on validation set
- **False Positive Rate:** < 3% (minimize customer friction)
- **False Negative Rate:** < 1% (catch fraud)
- **Average Review Time:** < 5 minutes per escalation
- **Customer Appeal Success Rate:** Monitor for bias

