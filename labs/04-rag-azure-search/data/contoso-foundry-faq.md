# Contoso Cloud AI Platform — Product FAQ

## What is the Contoso Cloud AI Platform?

The Contoso Cloud AI Platform is a fictional enterprise service used in this
workshop as sample "bring-your-own-data" content. It provides managed model
hosting, retrieval, and agent orchestration for internal business applications.
It is intentionally fictional so that a grounded model can only answer these
questions correctly by retrieving from this document — not from its pretraining.

## Pricing tiers

Contoso offers three pricing tiers:

- **Starter** — $49 per month. Includes 1 million tokens of inference, a single
  project workspace, and community support. Intended for prototypes.
- **Team** — $499 per month. Includes 25 million tokens, up to 10 project
  workspaces, private networking, and 8x5 business-hours support.
- **Enterprise** — custom pricing. Unlimited workspaces, dedicated capacity,
  customer-managed encryption keys, and 24x7 support with a 15-minute Sev-A SLA.

Annual pre-payment on the Team and Enterprise tiers receives a 20% discount.

## Supported regions

At launch, the platform is available in the following Contoso regions:
`contoso-east-1`, `contoso-west-2`, and `contoso-europe-1`. The `contoso-west-2`
region is the only one that currently offers GPU-backed fine-tuning.

## Data residency and retention

Customer data is stored only in the region where the workspace is created and is
never used to train shared foundation models. Prompt and completion logs are
retained for 30 days by default on the Team tier and can be configured to a
minimum of 0 days or a maximum of 365 days on the Enterprise tier.

## Service level agreement (SLA)

The Enterprise tier guarantees 99.95% monthly uptime. If uptime falls below
99.95% but stays at or above 99.0%, customers receive a 10% service credit.
Below 99.0%, customers receive a 25% service credit.

## Support contact

Enterprise customers can reach the Contoso Sev-A hotline at
support-priority@contoso.example within their portal. The internal escalation
alias for platform outages is `contoso-oncall@contoso.example`.
