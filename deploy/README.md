# FootyhubAws — EC2 Deployment Guide

## Prerequisites
- EC2 t3.micro, Ubuntu 22.04
- Security group: port 22 (SSH, your IP only), port 80 (HTTP, 0.0.0.0/0)
- IAM role `footyhub-ec2-role` attached (see Stage 4)
- RDS PostgreSQL instance in the same VPC

---

## 1. Upload the project

```bash
# From your local machine
scp -r /path/to/FootyhubAws ubuntu@<ec2-ip>:~/FootyhubAws
```

---

## 2. Install dependencies

```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx

cd ~/FootyhubAws
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

---

## 3. Set environment variables

```bash
cp .env.example .env
nano .env   # fill in all values
```

---

## 4. Create the PostgreSQL schema

```bash
psql -h <rds-endpoint> -U footyhub_user -d footyhub -f sql/postgres_schema.sql
```

---

## 5. Install systemd services

```bash
sudo cp deploy/footyhub-web.service      /etc/systemd/system/
sudo cp deploy/footyhub-scheduler.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable footyhub-web footyhub-scheduler
sudo systemctl start  footyhub-web footyhub-scheduler
```

Check status:
```bash
sudo systemctl status footyhub-web
sudo systemctl status footyhub-scheduler
```

---

## 6. Configure nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/footyhub
sudo ln -s /etc/nginx/sites-available/footyhub /etc/nginx/sites-enabled/footyhub
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

---

## 7. Verify

```bash
curl http://localhost       # should return the feed HTML
curl http://<ec2-public-ip> # same from outside
```

---

## 8. IAM setup (do this before going live)

See `deploy/iam.md` for the full walkthrough. Short version:
1. Create IAM policy from `deploy/iam-policy.json` (replace `YOUR_ACCOUNT_ID`)
2. Create IAM role `footyhub-ec2-role` with that policy, trusted entity = EC2
3. Attach the role to your EC2 instance (Actions → Security → Modify IAM role)
4. Remove `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from `.env` — boto3 uses the role automatically

---

## Useful commands

| Command | Purpose |
|---------|---------|
| `sudo journalctl -u footyhub-web -f` | Stream web logs |
| `sudo journalctl -u footyhub-scheduler -f` | Stream scheduler logs |
| `sudo systemctl restart footyhub-web` | Restart after code change |
| `sudo nginx -t` | Test nginx config before reload |
