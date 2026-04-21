# Alarmes Simples - Guia de Utilização

## Alarmes Configurados

### 1. **HighErrorRate** ⚠️ WARNING
- **Condição**: Taxa de erro > 5% durante 2 minutos
- **O que fazer**: Verificar logs na aba "Logs" do Grafana
- **Causa comum**: Credenciais inválidas, DB offline

### 2. **HighLatency** ⚠️ WARNING
- **Condição**: P95 latência > 500ms durante 2 minutos
- **O que fazer**: Verificar performance em Mimir dashboard
- **Causa comum**: DB lento, muita concorrência

### 3. **ServiceDown** 🔴 CRITICAL
- **Condição**: Flask /health endpoint não responde durante 1 minuto
- **O que fazer**: Reiniciar Docker container `docker compose restart flask-app`
- **Causa comum**: App crashed, porta bloqueada

### 4. **HighMemoryUsage** ⚠️ WARNING
- **Condição**: Memória > 500MB durante 2 minutos
- **O que fazer**: Restart da app ou otimizar queries
- **Causa comum**: Memory leak, muitas conexões DB abertas

---

## Como Configurar Notificações por Email

### Passo 1: Configurar SMTP e destinatário no Docker Compose

Abre PowerShell e executa:

```powershell
$env:EMAIL_ALERT_TO = "teu.email@empresa.com"
$env:GF_SMTP_HOST = "smtp.office365.com:587"
$env:GF_SMTP_USER = "teu.email@empresa.com"
$env:GF_SMTP_PASSWORD = "APP_PASSWORD_OU_PASSWORD_SMTP"
$env:GF_SMTP_FROM_ADDRESS = "teu.email@empresa.com"
docker compose up -d
```

### Passo 2: Testar

1. Abre Grafana em http://3000/alerts
2. Vai aparecer a notificação **"Email Alerts"** como notification channel
3. Quando houver um alerta, recebes o email automaticamente

---

## Onde Ver os Alarmes

### No Grafana:
- **http://localhost:3000/alerts** - Estado de todos os alertas
- **http://localhost:3000/alerting/list** - Histórico de notificações

### No Prometheus:
- **http://localhost:9090/alerts** - Regras de alerta atibas e firing

---

## Exemplos de Notificação Teams

Quando um alerta dispara, recebes uma mensagem como:

```
🔴 ALERT: ServiceDown
Severity: CRITICAL
Summary: McDonalds API Service Down
Description: Flask API is not responding to health checks

Start: 2026-04-21 14:30:00
Duration: 1 minute
```

---

## Desativar/Editar Alarmes

Se quiseres mudar thresholds:

1. Edita `observability/prometheus-rules.yml`
2. Muda o valor (ex: `> 0.05` para `> 0.10` para 10% error rate)
3. Executa `docker compose restart prometheus`

---

## Troubleshooting

**Alarmes não aparecem no Grafana?**
- Reinicia: `docker compose restart prometheus grafana`
- Verifica: `docker compose logs prometheus`

**Email não recebe notificações?**
- Verifica SMTP user/password
- Verifica caixa de spam
- Verifica logs: `docker compose logs grafana`

**Muitos falsos positivos?**
- Aumenta o tempo de `for` em prometheus-rules.yml (ex: `for: 5m` em vez de `for: 2m`)
