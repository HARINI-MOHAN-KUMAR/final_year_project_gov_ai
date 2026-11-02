"""
APScheduler background tasks for GovGuide AI.
Handles: deadline reminders, document expiry checks, email notifications.
"""

import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler = None


async def check_deadline_reminders():
    """
    Check for upcoming application deadlines and send email reminders.
    Runs daily at 9 AM.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.scheme_app import SchemeApplication
    from app.models.user import User
    from sqlalchemy import select
    import re

    logger.info("Running deadline reminder check...")
    try:
        async with AsyncSessionLocal() as db:
            # Find applications with deadlines in next 7 days
            result = await db.execute(
                select(SchemeApplication, User)
                .join(User)
                .where(SchemeApplication.status.in_(["Planned", "In Progress"]))
                .where(SchemeApplication.reminder_sent == False)
            )
            rows = result.all()

            reminded = 0
            for app, user in rows:
                deadline = app.deadline
                if not deadline or deadline.lower() in ("ongoing", "as per notification"):
                    continue

                # Try to parse deadline date
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y", "%d %B %Y"):
                    try:
                        dl_date = datetime.strptime(deadline, fmt).date()
                        days_left = (dl_date - datetime.now(timezone.utc).date()).days
                        if 0 <= days_left <= 7:
                            await _send_reminder_notification(user, app, days_left)
                            app.reminder_sent = True
                            db.add(app)
                            reminded += 1
                        break
                    except ValueError:
                        continue

            await db.commit()
            logger.info(f"Deadline check complete. Sent {reminded} reminders.")
    except Exception as e:
        logger.error(f"Deadline reminder task failed: {e}")


async def check_document_expiry():
    """
    Check for expired documents and mark them.
    Runs weekly on Mondays.
    """
    from app.core.database import AsyncSessionLocal
    from app.models.document import Document
    from sqlalchemy import select, update
    from datetime import date

    logger.info("Running document expiry check...")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Document).where(Document.expiry_date.isnot(None))
            )
            docs = result.scalars().all()
            expired_count = 0
            for doc in docs:
                try:
                    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                        try:
                            exp_date = datetime.strptime(doc.expiry_date, fmt).date()
                            if exp_date < date.today():
                                doc.is_expired = True
                                db.add(doc)
                                expired_count += 1
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass

            await db.commit()
            logger.info(f"Document expiry check complete. {expired_count} documents marked as expired.")
    except Exception as e:
        logger.error(f"Document expiry task failed: {e}")


async def _send_reminder_notification(user, application, days_left: int):
    """Send an email reminder for an upcoming deadline."""
    from app.core.config import settings
    if not settings.EMAIL_ENABLED:
        logger.debug(f"Email disabled. Would notify {user.email} about {application.scheme_name} deadline.")
        return

    try:
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⏰ GovGuide AI: {application.scheme_name} deadline in {days_left} days!"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = user.email

        body = f"""
        Dear {user.full_name or 'Citizen'},

        This is a reminder that the application deadline for:
        📋 {application.scheme_name}
        is in {days_left} day(s) ({application.deadline}).

        Current status: {application.status}

        Please visit GovGuide AI to complete your application.

        ⚠️ Advisory only – not an official government notification.
        """
        msg.attach(MIMEText(body, "plain"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"Reminder sent to {user.email} for {application.scheme_name}")
    except Exception as e:
        logger.error(f"Failed to send email reminder: {e}")


def start_scheduler():
    """Initialize and start the APScheduler."""
    global _scheduler
    _scheduler = AsyncIOScheduler()

    # Daily deadline check at 9 AM
    _scheduler.add_job(
        check_deadline_reminders,
        CronTrigger(hour=9, minute=0),
        id="deadline_reminders",
        replace_existing=True,
    )

    # Weekly document expiry check every Monday at 10 AM
    _scheduler.add_job(
        check_document_expiry,
        CronTrigger(day_of_week="mon", hour=10, minute=0),
        id="document_expiry",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("APScheduler started with deadline and expiry jobs")


def stop_scheduler():
    """Stop the APScheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
