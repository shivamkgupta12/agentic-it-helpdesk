# Password Reset Policy

## Purpose

This policy explains how password reset and account unlock requests must be handled.

## Sensitive Action

Password resets are sensitive actions. The AI assistant must not reset passwords directly.

## Required Verification

Before a password reset can proceed, the employee must complete identity verification. Verification may include:
- Confirming employee email.
- Confirming employee ID.
- Completing MFA verification.
- Admin validation through the identity provider.

## AI Assistant Rules

The AI assistant may:
- Explain the password reset process.
- Create a support request for password reset.
- Tell the user that approval or identity verification is required.

The AI assistant must not:
- Reset passwords directly.
- Ask the user to share their current password.
- Ask the user to share MFA codes.
- Approve its own password reset request.
- Change account permissions.

## Escalation

Create an approval request for an IT admin if the user asks to:
- Reset a password.
- Unlock an account.
- Change authentication methods.
- Disable MFA.
- Change access permissions.

## Suggested Ticket Category

Category: Password / Account  
Priority: Medium  
Urgency: Medium