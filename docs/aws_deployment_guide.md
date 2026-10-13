# FlakyGuard-AI: AWS EC2 Production Deployment & Cloud Infrastructure Guide

**Course:** CSE 4011 — Intelligent Developer Tools and AI DevOps Workflows  
**Academic Year:** 2026–27  
**Module Lead:** Rahul Yadav  
**Document Classification:** A3 Cloud Operations Deliverable (Criteria C14)  

---

## 1. Cloud Architecture & Topology Overview

FlakyGuard-AI is deployed on Amazon Web Services (AWS) in the `ap-south-1` (Mumbai) region to minimize network roundtrip latency for local development and live defense demonstrations.

```text
       Internet / GitHub CI Webhook / Prometheus Alerts
                              │
                              ▼
            AWS Internet Gateway & VPC (ap-south-1)
                              │
                    Security Group (Firewall)
       ┌──────────────────────┬────────────────────────┐
       │ Inbound Rules:       │ Port 8000: FlakyGuard  │
       │ Port 22: Admin SSH   │ Port 7080: Sourcegraph │
       │ Port 9090: Prometheus│ Port 3000: Grafana     │
       └──────────────────────┴────────────────────────┘
                              │
                              ▼
               Amazon EC2 Instance (t3.xlarge / g4dn.xlarge)
       ┌──────────────────────────────────────────────┐
       │ Docker Compose Multi-Profile Stack           │
       │  • api: FastAPI Core Engine (:8000)          │
       │  • redis: Fast State Blackboard (:6379)      │
       │  • postgres: Incident Archive DB (:5432)     │
       │  • prometheus: Metrics Scraper (:9090)       │
       │  • sourcegraph: Code Intelligence (:7080)    │
       │  • ollama: Local LLM Runner (:11434)         │
       └──────────────────────────────────────────────┘
```

---

## 2. Instance Sizing & Cost Analysis

| Deployment Tier | Instance Type | vCPU | RAM | Storage (GP3) | Purpose / Workload | Estimated Cost (ap-south-1) |
|---|---|---|---|---|---|---|
| **Development** | Local Machine | Any | 16 GB | 20 GB | Sprints 1.1–2.4 (`--profile lite`) | Free |
| **Benchmarking (CPU)** | `t3.xlarge` | 4 | 16 GB | 80 GB | Sprint 3.3 multi-model evaluation | ~$0.1664 / hour |
| **Benchmarking (GPU)** | `g4dn.xlarge` | 4 | 16 GB (T4 16GB VRAM) | 100 GB | Low-latency 7B parameter inference | ~$0.526 / hour |
| **Production Demo** | `t3.large` | 2 | 8 GB | 50 GB | Live viva demonstration & web console | ~$0.0832 / hour |

---

## 3. Security Group Firewall Specification

Configure AWS Security Group `flakyguard-sg`:

| Rule Type | Port Range | Protocol | Source CIDR | Justification & Security Policy |
|---|---|---|---|---|
| **Inbound** | `22` | TCP | `Your_Admin_IP/32` | Secure SSH management access. Disallow `0.0.0.0/0`. |
| **Inbound** | `8000` | TCP | `0.0.0.0/0` | Public webhook intake from GitHub Actions and Web Console. |
| **Inbound** | `7080` | TCP | `Your_Admin_IP/32` | Sourcegraph OSS web interface restricted to team. |
| **Inbound** | `9090` | TCP | `Your_Admin_IP/32` | Prometheus observability metrics dashboard. |
| **Inbound** | `3000` | TCP | `Your_Admin_IP/32` | Optional Grafana analytics dashboard. |
| **Outbound** | All | All | `0.0.0.0/0` | Outbound HTTPS for GitHub REST API & package repositories. |

---

## 4. EC2 Provisioning & Launch Runbook

### Step 1: Launch EC2 Instance via AWS CLI
```bash
aws ec2 run-instances \
    --region ap-south-1 \
    --image-id ami-03f4878e83d3e3101 \
    --instance-type t3.xlarge \
    --key-name flakyguard-key \
    --security-group-ids sg-0abc123def456 \
    --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":80,"VolumeType":"gp3"}}]' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=flakyguard-production}]'
```

### Step 2: System Bootstrapping
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git curl
sudo usermod -aG docker ubuntu
sudo systemctl enable --now docker
```

### Step 3: Clone Repository & Configure Environment
```bash
git clone https://github.com/desirao/flakyguard.git /opt/flakyguard
cd /opt/flakyguard
cp .env.example .env
# Edit .env with production GITHUB_WEBHOOK_SECRET and GITHUB_TOKEN
```

### Step 4: Systemd Service Unit Configuration (`/etc/systemd/system/flakyguard.service`)
```ini
[Unit]
Description=FlakyGuard-AI DevOps Orchestrator Stack
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/flakyguard
ExecStart=/usr/bin/docker compose --profile lite up -d
ExecStop=/usr/bin/docker compose --profile lite down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now flakyguard.service
```

---

## 5. Connecting Live GitHub CI Webhooks to AWS

1. Obtain your EC2 Public IPv4 Address (e.g., `13.233.14.88`).
2. In your GitHub repository settings:
   - Navigate to **Settings > Secrets and variables > Actions**.
   - Add Secret `FLAKYGUARD_URL`: `http://13.233.14.88:8000`
   - Add Secret `FLAKYGUARD_WEBHOOK_SECRET`: `flakyguard-production-hmac-secret-xyz`
3. Trigger a test failure by opening a draft PR with a failing test; observe the live webhook ingestion in `journalctl -u flakyguard.service -f`.
