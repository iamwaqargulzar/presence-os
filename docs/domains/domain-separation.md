# Registrable-Domain Security Separation

Control plane and tenant-generated/untrusted content MUST use different registrable domains/eTLD+1.

Example only:
- CONTROL: `app.presenceos.com`, `admin.presenceos.com`, `api.presenceos.com`
- TENANT PRODUCTION: `*.presence.site`
- PREVIEW: `*.presencepreview.site`

Reason:
- cookies/origin security;
- tenant-generated JS isolation;
- abuse/reputation separation;
- clearer operational boundaries.

Never place untrusted generated tenant sites under a parent domain whose cookies/authentication can affect the control plane.
