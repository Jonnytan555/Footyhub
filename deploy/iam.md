# Stage 4 — IAM Setup

## Why this matters
boto3 resolves AWS credentials in this order:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. `~/.aws/credentials` file
3. **EC2 instance metadata** (IAM role attached to the instance)

When you attach an IAM role to the EC2 instance, boto3 automatically fetches temporary credentials from the instance metadata service. No AWS keys in `.env` — nothing to rotate, nothing to leak.

---

## Step 1 — Create the IAM policy

In the AWS Console → IAM → Policies → Create policy → JSON tab.

Paste the contents of `deploy/iam-policy.json`, replacing `YOUR_ACCOUNT_ID` with your 12-digit AWS account ID and the queue name if you used a different one.

Name it: `footyhub-sqs-policy`

**Why scope to the specific queue ARN?**  
Using `"Resource": "*"` would allow the EC2 instance to read/write any SQS queue in your account. Scoping to the queue ARN means a compromised instance can only touch the one queue it needs.

---

## Step 2 — Create the IAM role

IAM → Roles → Create role

- **Trusted entity type:** AWS service
- **Use case:** EC2
- **Permissions:** attach `footyhub-sqs-policy`
- **Role name:** `footyhub-ec2-role`

---

## Step 3 — Attach the role to your EC2 instance

EC2 Console → select your instance → Actions → Security → Modify IAM role → select `footyhub-ec2-role` → Update.

You can do this to a running instance — no restart needed.

---

## Step 4 — Remove AWS keys from .env

Once the role is attached, open `.env` on the EC2 instance and remove these lines if present:

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

boto3 will now use the instance role automatically. Restart the services:

```bash
sudo systemctl restart footyhub-web footyhub-scheduler
```

---

## Step 5 — Verify

```bash
# From the EC2 instance — should print temporary credentials from the role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/footyhub-ec2-role
```

Then run a publisher job and confirm messages appear in the SQS console:

AWS Console → SQS → footyhub-articles → Send and receive messages → Poll for messages

---

## SQS queue settings (recommended)

| Setting | Value | Why |
|---------|-------|-----|
| Visibility timeout | 300s | Gives the subscriber 5 minutes to process a batch before a message reappears |
| Message retention | 4 days | Failed messages stay in the queue long enough to investigate |
| Access policy | Allow only `footyhub-ec2-role` | No other principal can read or write the queue |

To set the access policy, go to SQS → your queue → Access policy → Edit and paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:role/footyhub-ec2-role"
      },
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:ChangeMessageVisibility"
      ],
      "Resource": "arn:aws:sqs:eu-west-2:YOUR_ACCOUNT_ID:footyhub-articles"
    }
  ]
}
```
