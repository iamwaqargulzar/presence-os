# File Ingestion Security

Pipeline:

UPLOAD → QUARANTINE → TYPE VALIDATION → SIZE/DECOMPRESSION LIMITS → MALWARE SCAN → SAFE PARSER/SANDBOX/CDR WHERE APPROPRIATE → AVAILABLE

Rules:
- store outside webroot/object storage;
- use generated object IDs;
- do not trust extension/MIME alone;
- cap archive expansion;
- isolate parsers for risky formats;
- never execute macros/scripts from user uploads;
- extracted text is untrusted data;
- access is tenant-scoped;
- preserve original when legally/operationally required;
- log ingestion status and scan version.
