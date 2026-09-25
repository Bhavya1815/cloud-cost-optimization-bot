from apscheduler.schedulers.blocking import (
    BlockingScheduler,
)

from .scanner import scan_ec2_instances
from .idle_detector import analyze_idle_instances
from .analyzer import analyze_instances
from .cost_engine import add_cost_estimates
from .dynamodb_store import (
    save_recommendations,
    resolve_missing_recommendations,
)
from .approval import create_approval_request
from .approval_store import save_approval_request
from .report_generator import generate_weekly_report
from .telegram_formatter import (
    format_recommendation_alert,
)
from .telegram_notifier import send_message
from .logging_config import (
    configure_logging,
    get_logger,
)
from .config_validation import (
    validate_configuration,
)
from .audit_store import (
    safe_record_audit_event,
)


configure_logging()
logger = get_logger(__name__)


def get_current_recommendations():
    instances = scan_ec2_instances()

    instances = analyze_idle_instances(
        instances
    )

    recommendations = analyze_instances(
        instances
    )

    recommendations = add_cost_estimates(
        recommendations
    )

    return recommendations


def run_monitoring_scan():
    logger.info(
        "Starting resource monitoring scan."
    )

    safe_record_audit_event(
        logger,
        "SCAN_STARTED",
    )

    try:
        recommendations = (
            get_current_recommendations()
        )

        resolved_count = (
            resolve_missing_recommendations(
                recommendations
            )
        )

        if resolved_count:
            logger.info(
                "Resolved %s previous recommendation(s).",
                resolved_count,
            )

        for recommendation in recommendations:
            safe_record_audit_event(
                logger,
                "RECOMMENDATION_DETECTED",
                instance_id=recommendation[
                    "instance_id"
                ],
                name=recommendation["name"],
                status="ACTIVE",
                message=recommendation[
                    "reason"
                ],
            )

        if not recommendations:
            logger.info(
                "No optimization candidates detected."
            )

            safe_record_audit_event(
                logger,
                "SCAN_COMPLETED",
                status="NO_CANDIDATES",
                metadata={
                    "recommendation_count": 0,
                    "new_recommendation_count": 0,
                },
            )

            return

        new_recommendations = (
            save_recommendations(
                recommendations
            )
        )

        logger.info(
            "Detected %s optimization candidate(s).",
            len(recommendations),
        )

        logger.info(
            "New recommendations: %s.",
            len(new_recommendations),
        )

        if not new_recommendations:
            logger.info(
                "No new recommendations. "
                "Approval request skipped."
            )

            safe_record_audit_event(
                logger,
                "SCAN_COMPLETED",
                status="NO_NEW_RECOMMENDATIONS",
                metadata={
                    "recommendation_count": len(
                        recommendations
                    ),
                    "new_recommendation_count": 0,
                },
            )

            return

        approval_requests = []

        for recommendation in new_recommendations:
            approval = create_approval_request(
                recommendation
            )

            save_approval_request(
                approval
            )

            approval_requests.append(
                approval
            )

            logger.info(
                "Approval request created: %s",
                approval["approval_id"],
            )

            safe_record_audit_event(
                logger,
                "APPROVAL_CREATED",
                instance_id=recommendation[
                    "instance_id"
                ],
                name=recommendation["name"],
                approval_id=approval[
                    "approval_id"
                ],
                status="PENDING",
                message=(
                    "Approval request created."
                ),
            )

        message = format_recommendation_alert(
            new_recommendations
        )

        message += (
            "\n\nAPPROVAL REQUIRED"
            "\n"
            + "-" * 30
        )

        for approval in approval_requests:
            message += (
                "\n"
                f"Approval ID: "
                f"{approval['approval_id']}\n"
                f"Resource: "
                f"{approval['name']}\n"
                f"Action: "
                f"{approval['action']}\n"
                "Status: PENDING\n"
                f"Expires in: "
                f"{approval['expires_in_hours']} hours\n"
                "\n"
                f"/approve "
                f"{approval['approval_id']}\n"
                f"/reject "
                f"{approval['approval_id']}\n"
                f"/status "
                f"{approval['approval_id']}\n"
            )

        message += (
            "\nNo resource will be stopped "
            "without explicit approval."
        )

        send_message(message)

        logger.info(
            "Approval request sent to Telegram."
        )

        safe_record_audit_event(
            logger,
            "ALERT_SENT",
            status="SENT",
            metadata={
                "approval_count": len(
                    approval_requests
                ),
            },
        )

        safe_record_audit_event(
            logger,
            "SCAN_COMPLETED",
            status="RECOMMENDATIONS_CREATED",
            metadata={
                "recommendation_count": len(
                    recommendations
                ),
                "new_recommendation_count": len(
                    new_recommendations
                ),
            },
        )

    except Exception as error:
        safe_record_audit_event(
            logger,
            "SCAN_FAILED",
            status="FAILED",
            message=str(error),
        )

        logger.exception(
            "Monitoring scan failed."
        )

        raise


def run_weekly_report():
    logger.info(
        "Starting weekly cost report."
    )

    try:
        recommendations = (
            get_current_recommendations()
        )

        report = generate_weekly_report(
            recommendations
        )

        send_message(report)

        logger.info(
            "Weekly report sent to Telegram."
        )

    except Exception:
        logger.exception(
            "Weekly report failed."
        )

        raise


def main():
    validate_configuration()

    logger.info(
        "Starting Cloud Cost Optimization Scheduler."
    )

    scheduler = BlockingScheduler()

    run_monitoring_scan()

    scheduler.add_job(
        run_monitoring_scan,
        "interval",
        hours=1,
        id="resource-monitoring",
        replace_existing=True,
    )

    scheduler.add_job(
        run_weekly_report,
        "interval",
        weeks=1,
        id="weekly-cost-report",
        replace_existing=True,
    )

    logger.info(
        "Monitoring interval: 1 hour."
    )

    logger.info(
        "Weekly report interval: 7 days."
    )

    logger.info(
        "Approval workflow: enabled."
    )

    logger.info(
        "Automatic remediation: approval required."
    )

    logger.info(
        "Duplicate alerts: prevented."
    )

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info(
            "Scheduler stopped."
        )


if __name__ == "__main__":
    main()
