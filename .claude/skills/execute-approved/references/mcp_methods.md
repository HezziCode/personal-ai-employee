# MCP Server Methods Reference

## Email MCP

### send_email
```json
{
  "action": "send_email",
  "to": "recipient@example.com",
  "subject": "Invoice #123",
  "body": "Please find attached...",
  "cc": ["cc@example.com"],
  "bcc": [],
  "attachments": ["/path/to/file.pdf"],
  "template": "invoice | reply | followup"
}
```

**Response**: `{ "status": "sent", "message_id": "...", "timestamp": "..." }`

## Browser MCP

### navigate
```json
{
  "action": "navigate",
  "url": "https://banking.example.com",
  "wait_for": "selector or timeout"
}
```

### fill_form
```json
{
  "action": "fill_form",
  "form": "#payment-form",
  "fields": {
    "amount": "500.00",
    "account": "CHECKING",
    "recipient": "Client A"
  }
}
```

### click
```json
{
  "action": "click",
  "selector": "#submit-button",
  "wait_for_navigation": true
}
```

## Social MCP

### post_tweet
```json
{
  "action": "post_tweet",
  "content": "Tweet text here",
  "reply_to": null,
  "media": ["url1", "url2"],
  "schedule": null
}
```

**Response**: `{ "status": "posted", "tweet_id": "...", "url": "..." }`

### post_facebook
```json
{
  "action": "post_facebook",
  "content": "Post content",
  "image": "/path/to/image.jpg",
  "link": "https://example.com",
  "schedule": null
}
```

### post_instagram
```json
{
  "action": "post_instagram",
  "caption": "Caption text",
  "image": "/path/to/image.jpg",
  "hashtags": ["#tag1", "#tag2"],
  "schedule": null
}
```

## Odoo MCP

### create_invoice
```json
{
  "action": "create_invoice",
  "customer": "Customer Name",
  "amount": 500.00,
  "description": "Services rendered",
  "due_date": "2026-02-07",
  "tax_included": true
}
```

**Response**: `{ "status": "created", "invoice_id": "...", "invoice_ref": "INV-2026-001" }`

### record_payment
```json
{
  "action": "record_payment",
  "invoice_id": 123,
  "amount": 500.00,
  "payment_method": "bank_transfer",
  "reference": "Check #1234",
  "date": "2026-01-07"
}
```

## Error Responses

All MCPs return standard error format:

```json
{
  "status": "error",
  "error_code": "AUTH_FAILED | TIMEOUT | VALIDATION_ERROR | SERVICE_DOWN",
  "error_message": "Details",
  "retry_eligible": true
}
```
