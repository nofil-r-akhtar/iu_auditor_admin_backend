"""
HTML email templates for various notification scenarios.
Each function returns (subject, html_body) ready to pass to send_email().
"""


# ── Reusable wrapper — header + footer + base styles ──────
def _wrap(content_html: str, preheader: str = "") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f1f5f9;font-family:Arial,Helvetica,sans-serif;color:#1e293b;">
  <span style="display:none;visibility:hidden;opacity:0;color:transparent;height:0;width:0;">{preheader}</span>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f1f5f9;padding:40px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               style="max-width:600px;background-color:#ffffff;border-radius:12px;overflow:hidden;
                      box-shadow:0 4px 16px rgba(15,23,42,0.06);">

          <!-- Header -->
          <tr>
            <td style="background-color:#1e3a8a;padding:28px 32px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:0.3px;">
                IU Auditor
              </h1>
              <p style="margin:4px 0 0;color:rgba(255,255,255,0.7);font-size:13px;">
                Iqra University Internal Audit System
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px;">
              {content_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f8fafc;padding:18px 32px;text-align:center;border-top:1px solid #e2e8f0;">
              <p style="margin:0;color:#64748b;font-size:11px;">
                This is an automated message from IU Auditor.<br>
                Please do not reply to this email.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _button(label: str, url: str = "#") -> str:
    return f"""
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:24px 0;">
  <tr>
    <td style="border-radius:8px;background-color:#3b82f6;">
      <a href="{url}" style="display:inline-block;padding:13px 28px;color:#ffffff;
              text-decoration:none;font-weight:bold;font-size:14px;border-radius:8px;">
        {label}
      </a>
    </td>
  </tr>
</table>"""


# ─────────────────────────────────────────────────────────────────
# 1. WELCOME EMAIL — for new senior lecturers / admins / dept heads
# ─────────────────────────────────────────────────────────────────
def welcome_user_email(
    name: str,
    email: str,
    temp_password: str,
    role: str,
    department: str | None = None,
    portal_url: str = "https://iu-auditor.vercel.app",
) -> tuple[str, str]:
    role_label = role.replace("_", " ").title()
    dept_row   = ""
    if department:
        dept_row = f"""
      <tr>
        <td style="padding:8px 0;color:#64748b;font-size:13px;width:140px;">Department</td>
        <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{department}</td>
      </tr>"""

    body = f"""
<h2 style="margin:0 0 8px;color:#1e293b;font-size:22px;">Welcome aboard, {name}! 👋</h2>
<p style="margin:0 0 24px;color:#475569;font-size:14px;line-height:1.6;">
  Your IU Auditor account has been created. Below are your login credentials —
  please sign in and change your password right away.
</p>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       style="background-color:#f8fafc;border-radius:10px;padding:20px;margin-bottom:24px;">
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;width:140px;">Name</td>
    <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{name}</td>
  </tr>
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;">Role</td>
    <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{role_label}</td>
  </tr>{dept_row}
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;">Email</td>
    <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{email}</td>
  </tr>
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;">Temporary Password</td>
    <td style="padding:8px 0;">
      <code style="background-color:#dbeafe;color:#1e40af;padding:6px 10px;
                   border-radius:6px;font-size:14px;font-weight:600;letter-spacing:0.5px;">
        {temp_password}
      </code>
    </td>
  </tr>
</table>

<p style="margin:0 0 8px;color:#475569;font-size:14px;line-height:1.6;">
  <strong>⚠️ For your security:</strong> You'll be required to set a new
  password the first time you log in.
</p>

{_button("Sign In to Portal", portal_url)}

<p style="margin:24px 0 0;color:#94a3b8;font-size:12px;line-height:1.6;">
  If you didn't expect this account, please contact your system administrator.
</p>"""

    subject = f"Welcome to IU Auditor — Your {role_label} Account"
    return subject, _wrap(body, preheader=f"Your IU Auditor login credentials inside.")


# ─────────────────────────────────────────────────────────────────
# 2. NEW TEACHER EMAIL — sent to teachers who will be audited
# ─────────────────────────────────────────────────────────────────
def teacher_added_email(
    name: str,
    department: str,
    audit_date: str | None = None,
    audit_time: str | None = None,
) -> tuple[str, str]:
    schedule_block = ""
    if audit_date:
        schedule_block = f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       style="background-color:#fef3c7;border-radius:10px;padding:18px;margin:0 0 24px;">
  <tr>
    <td style="color:#92400e;font-size:13px;font-weight:600;padding-bottom:6px;">
      📅 Tentative Audit Schedule
    </td>
  </tr>
  <tr>
    <td style="color:#78350f;font-size:14px;">
      Date: <strong>{audit_date}</strong>{f"<br>Time: <strong>{audit_time}</strong>" if audit_time else ""}
    </td>
  </tr>
</table>"""

    body = f"""
<h2 style="margin:0 0 8px;color:#1e293b;font-size:22px;">Hello {name},</h2>
<p style="margin:0 0 20px;color:#475569;font-size:14px;line-height:1.6;">
  This is to notify you that your name has been added to the IU Auditor system as a faculty member
  in the <strong>{department}</strong> department.
</p>

<p style="margin:0 0 20px;color:#475569;font-size:14px;line-height:1.6;">
  An assigned senior lecturer will conduct a brief teaching audit. The auditor will reach out to
  you to coordinate the visit. No action is required from you at this time.
</p>

{schedule_block}

<p style="margin:0;color:#94a3b8;font-size:12px;line-height:1.6;">
  For any questions, please contact your department head or the audit committee.
</p>"""

    subject = "You've Been Added to IU Auditor"
    return subject, _wrap(body, preheader="A teaching audit has been scheduled.")


# ─────────────────────────────────────────────────────────────────
# 3. AUDIT ASSIGNED EMAIL — sent to senior lecturer
# ─────────────────────────────────────────────────────────────────
def audit_assigned_email(
    lecturer_name: str,
    teacher_name: str,
    teacher_department: str,
    form_title: str,
    notes: str | None = None,
    portal_url: str = "https://iu-auditor-app.vercel.app",
) -> tuple[str, str]:
    notes_block = ""
    if notes and notes.strip():
        notes_block = f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       style="background-color:#fef3c7;border-radius:10px;padding:18px;margin:0 0 24px;">
  <tr>
    <td style="color:#92400e;font-size:13px;font-weight:600;padding-bottom:6px;">
      📝 Notes from the Admin
    </td>
  </tr>
  <tr>
    <td style="color:#78350f;font-size:14px;line-height:1.5;">{notes}</td>
  </tr>
</table>"""

    body = f"""
<h2 style="margin:0 0 8px;color:#1e293b;font-size:22px;">Hi {lecturer_name},</h2>
<p style="margin:0 0 24px;color:#475569;font-size:14px;line-height:1.6;">
  A new audit has been assigned to you. Please review the details below
  and complete the audit at your earliest convenience.
</p>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       style="background-color:#eff6ff;border-radius:10px;padding:20px;margin-bottom:24px;border-left:4px solid #3b82f6;">
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;width:140px;">Faculty</td>
    <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{teacher_name}</td>
  </tr>
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;">Department</td>
    <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{teacher_department}</td>
  </tr>
  <tr>
    <td style="padding:8px 0;color:#64748b;font-size:13px;">Audit Form</td>
    <td style="padding:8px 0;color:#1e293b;font-size:14px;font-weight:600;">{form_title}</td>
  </tr>
</table>

{notes_block}

{_button("Open Auditor Portal", portal_url)}

<p style="margin:24px 0 0;color:#94a3b8;font-size:12px;line-height:1.6;">
  Open the IU Auditor app and head to <strong>Audits</strong> to begin.
</p>"""

    subject = f"New Audit Assigned — {teacher_name}"
    return subject, _wrap(body, preheader=f"You've been assigned to audit {teacher_name}.")