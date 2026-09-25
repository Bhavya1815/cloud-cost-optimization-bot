import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from .approval_store import (
    get_approval_request,
    update_approval_status,
)
from .remediation_service import (
    execute_approved_remediation,
)
from .config_validation import (
    validate_configuration,
)
from .logging_config import (
    configure_logging,
    get_logger,
)
from .audit_store import (
    safe_record_audit_event,
)


configure_logging()
logger = get_logger(__name__)


TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)


def validate_telegram_configuration():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not configured."
        )

    if not TELEGRAM_CHAT_ID:
        raise ValueError(
            "TELEGRAM_CHAT_ID is not configured."
        )


def is_authorized(update: Update):
    if update.effective_chat is None:
        return False

    return str(
        update.effective_chat.id
    ) == str(TELEGRAM_CHAT_ID)


async def approve_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_authorized(update):
        safe_record_audit_event(
            logger,
            "UNAUTHORIZED_COMMAND",
            status="BLOCKED",
            message="/approve",
            metadata={
                "chat_id": str(
                    update.effective_chat.id
                    if update.effective_chat
                    else None
                ),
            },
        )

        await update.message.reply_text(
            "Unauthorized request."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/approve <approval_id>"
        )
        return

    approval_id = context.args[0]

    approval = get_approval_request(
        approval_id
    )

    if not approval:
        await update.message.reply_text(
            "Approval request not found."
        )
        return

    if approval.get("status") != "PENDING":
        await update.message.reply_text(
            f"Request is already "
            f"{approval.get('status')}."
        )
        return

    update_approval_status(
        approval_id,
        "APPROVED",
    )

    safe_record_audit_event(
        logger,
        "APPROVAL_APPROVED",
        instance_id=approval.get(
            "instance_id"
        ),
        name=approval.get("name"),
        approval_id=approval_id,
        status="APPROVED",
        message="Approval granted through Telegram.",
    )

    result = execute_approved_remediation(
        approval_id
    )

    if result["success"]:
        await update.message.reply_text(
            "REMEDIATION EXECUTED\n\n"
            f"Resource: {approval.get('name')}\n"
            f"Instance ID: "
            f"{approval.get('instance_id')}\n"
            f"Action: {approval.get('action')}\n\n"
            f"{result['reason']}"
        )

        return

    await update.message.reply_text(
        "REMEDIATION FAILED\n\n"
        f"Resource: {approval.get('name')}\n"
        f"Instance ID: "
        f"{approval.get('instance_id')}\n\n"
        f"{result['reason']}"
    )


async def reject_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_authorized(update):
        safe_record_audit_event(
            logger,
            "UNAUTHORIZED_COMMAND",
            status="BLOCKED",
            message="/reject",
            metadata={
                "chat_id": str(
                    update.effective_chat.id
                    if update.effective_chat
                    else None
                ),
            },
        )

        await update.message.reply_text(
            "Unauthorized request."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/reject <approval_id>"
        )
        return

    approval_id = context.args[0]

    approval = get_approval_request(
        approval_id
    )

    if not approval:
        await update.message.reply_text(
            "Approval request not found."
        )
        return

    if approval.get("status") != "PENDING":
        await update.message.reply_text(
            f"Request is already "
            f"{approval.get('status')}."
        )
        return

    update_approval_status(
        approval_id,
        "REJECTED",
    )

    safe_record_audit_event(
        logger,
        "APPROVAL_REJECTED",
        instance_id=approval.get(
            "instance_id"
        ),
        name=approval.get("name"),
        approval_id=approval_id,
        status="REJECTED",
        message="Approval rejected through Telegram.",
    )

    await update.message.reply_text(
        "REQUEST REJECTED\n\n"
        f"Resource: {approval.get('name')}\n"
        f"Instance ID: "
        f"{approval.get('instance_id')}\n"
        f"Action: {approval.get('action')}\n\n"
        "No remediation was executed."
    )


async def status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_authorized(update):
        safe_record_audit_event(
            logger,
            "UNAUTHORIZED_COMMAND",
            status="BLOCKED",
            message="/status",
        )

        await update.message.reply_text(
            "Unauthorized request."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/status <approval_id>"
        )
        return

    approval_id = context.args[0]

    approval = get_approval_request(
        approval_id
    )

    if not approval:
        await update.message.reply_text(
            "Approval request not found."
        )
        return

    await update.message.reply_text(
        "APPROVAL STATUS\n\n"
        f"Resource: {approval.get('name')}\n"
        f"Instance ID: "
        f"{approval.get('instance_id')}\n"
        f"Action: {approval.get('action')}\n"
        f"Status: {approval.get('status')}\n"
        f"Created: {approval.get('created_at')}"
    )


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not is_authorized(update):
        safe_record_audit_event(
            logger,
            "UNAUTHORIZED_COMMAND",
            status="BLOCKED",
            message="/start",
        )

        await update.message.reply_text(
            "Unauthorized request."
        )
        return

    await update.message.reply_text(
        "CLOUD COST OPTIMIZER BOT\n\n"
        "Available commands:\n\n"
        "/approve <approval_id>\n"
        "/reject <approval_id>\n"
        "/status <approval_id>"
    )


def main():
    validate_configuration()
    validate_telegram_configuration()

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "approve",
            approve_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "reject",
            reject_command,
        )
    )

    application.add_handler(
        CommandHandler(
            "status",
            status_command,
        )
    )

    logger.info(
        "Cloud Cost Optimizer Telegram control bot starting."
    )

    logger.info(
        "Approval control: enabled."
    )

    logger.info(
        "Command polling: enabled."
    )

    application.run_polling()


if __name__ == "__main__":
    main()
