# Runbook — Custom Domain Onboarding

1. Confirm tenant/service and desired hostname.
2. Ensure random canonical platform hostname is healthy.
3. Collect domain without asking tenant to transfer ownership.
4. Determine automatic provider/Domain Connect path or manual records.
5. Provide exact validation/routing records.
6. Verify ownership.
7. Create Cloudflare custom hostname / equivalent route.
8. Monitor certificate validation state.
9. Health-check application over custom hostname.
10. Verify redirects/canonical SEO policy.
11. Make primary only after successful check.
12. Preserve rollback to random platform hostname.
13. Audit all DNS/domain actions.

Before any DNS-provider migration, inventory MX/SPF/DKIM/DMARC and other records.
