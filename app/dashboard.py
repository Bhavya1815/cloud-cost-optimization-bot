import json

import streamlit as st

from app.scanner import scan_ec2_instances
from app.idle_detector import analyze_idle_instances
from app.analyzer import analyze_instances
from app.cost_engine import add_cost_estimates
from app.approval_store import (
    create_table_if_not_exists,
)
from app.audit_store import (
    list_audit_events,
)


st.set_page_config(
    page_title="Cloud Cost Optimizer",
    page_icon="☁️",
    layout="wide",
)


def get_dashboard_data():
    instances = scan_ec2_instances()

    analyzed_instances = analyze_idle_instances(
        instances
    )

    recommendations = analyze_instances(
        analyzed_instances
    )

    recommendations = add_cost_estimates(
        recommendations
    )

    return analyzed_instances, recommendations


def get_approval_requests():
    table = create_table_if_not_exists()

    response = table.scan()

    return response.get(
        "Items",
        []
    )


def get_audit_data():
    return list_audit_events(
        limit=100
    )


def main():
    st.title("Cloud Cost Optimizer")

    st.caption(
        "Floci-based cloud resource monitoring and "
        "cost optimization dashboard"
    )

    st.divider()

    if st.button(
        "Refresh Dashboard",
        width="content",
    ):
        st.rerun()

    try:
        instances, recommendations = (
            get_dashboard_data()
        )

        approval_requests = (
            get_approval_requests()
        )

        audit_events = get_audit_data()

        all_instances = scan_ec2_instances()

    except Exception as error:
        st.error(
            f"Unable to load dashboard data: {error}"
        )
        st.stop()

    running_count = sum(
        1
        for instance in all_instances
        if instance["state"] == "running"
    )

    stopped_count = sum(
        1
        for instance in all_instances
        if instance["state"] == "stopped"
    )

    idle_count = sum(
        1
        for instance in instances
        if instance["idle"]
    )

    active_count = sum(
        1
        for instance in instances
        if not instance["idle"]
    )

    candidate_count = len(
        recommendations
    )

    total_monthly_savings = sum(
        recommendation[
            "estimated_monthly_savings"
        ]
        for recommendation in recommendations
    )

    yearly_savings = (
        total_monthly_savings * 12
    )

    pending_count = sum(
        1
        for request in approval_requests
        if request.get("status")
        == "PENDING"
    )

    approved_count = sum(
        1
        for request in approval_requests
        if request.get("status")
        == "APPROVED"
    )

    executed_count = sum(
        1
        for request in approval_requests
        if request.get("status")
        == "EXECUTED"
    )

    failed_count = sum(
        1
        for request in approval_requests
        if request.get("status")
        == "FAILED"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Running Resources",
        running_count,
    )

    col2.metric(
        "Stopped Resources",
        stopped_count,
    )

    col3.metric(
        "Optimization Candidates",
        candidate_count,
    )

    col4.metric(
        "Monthly Savings",
        f"${total_monthly_savings:.2f}",
    )

    st.divider()

    st.subheader(
        "Resource Overview"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write("Resource State")

        state_chart = {
            "Running": running_count,
            "Stopped": stopped_count,
        }

        st.bar_chart(
            state_chart,
            width="stretch",
        )

    with col2:
        st.write("CPU Activity")

        activity_chart = {
            "Idle": idle_count,
            "Active": active_count,
        }

        st.bar_chart(
            activity_chart,
            width="stretch",
        )

    st.divider()

    st.subheader(
        "Savings Overview"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Estimated Monthly Savings",
            f"${total_monthly_savings:.2f}",
        )

    with col2:
        st.metric(
            "Estimated Annual Savings",
            f"${yearly_savings:.2f}",
        )

    st.divider()

    st.subheader(
        "Approval Workflow"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Pending",
        pending_count,
    )

    col2.metric(
        "Approved",
        approved_count,
    )

    col3.metric(
        "Executed",
        executed_count,
    )

    col4.metric(
        "Failed",
        failed_count,
    )

    if approval_requests:
        approval_rows = []

        for request in approval_requests:
            approval_rows.append({
                "Approval ID": request.get(
                    "approval_id",
                    "",
                ),
                "Resource": request.get(
                    "name",
                    "",
                ),
                "Instance ID": request.get(
                    "instance_id",
                    "",
                ),
                "Action": request.get(
                    "action",
                    "",
                ),
                "Status": request.get(
                    "status",
                    "",
                ),
                "Created": request.get(
                    "created_at",
                    "",
                ),
                "Updated": request.get(
                    "updated_at",
                    "",
                ),
            })

        st.dataframe(
            approval_rows,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info(
            "No approval requests found."
        )

    st.divider()

    st.subheader(
        "Audit Trail"
    )

    st.caption(
        "Latest 100 system events from the "
        "cost-optimization-audit DynamoDB table."
    )

    if audit_events:
        audit_rows = []

        for event in audit_events:
            metadata = event.get(
                "metadata"
            )

            if metadata is None:
                metadata_text = ""
            else:
                metadata_text = json.dumps(
    metadata,
    sort_keys=True,
    default=str,
)

            audit_rows.append({
                "Timestamp": event.get(
                    "timestamp",
                    "",
                ),
                "Event": event.get(
                    "event_type",
                    "",
                ),
                "Resource": event.get(
                    "name",
                    "",
                ),
                "Instance ID": event.get(
                    "instance_id",
                    "",
                ),
                "Approval ID": event.get(
                    "approval_id",
                    "",
                ),
                "Status": event.get(
                    "status",
                    "",
                ),
                "Message": event.get(
                    "message",
                    "",
                ),
                "Metadata": metadata_text,
            })

        st.dataframe(
            audit_rows,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info(
            "No audit events recorded yet."
        )

    st.divider()

    st.subheader(
        "Resource Inventory"
    )

    resource_rows = []

    for instance in instances:
        resource_rows.append({
            "Name": instance["name"],
            "Instance ID": instance[
                "instance_id"
            ],
            "Type": instance[
                "instance_type"
            ],
            "State": instance["state"],
            "Environment": instance[
                "environment"
            ],
            "CPU %": instance[
                "cpu_utilization"
            ],
            "Idle": instance["idle"],
            "Critical": instance[
                "critical"
            ],
        })

    if resource_rows:
        st.dataframe(
            resource_rows,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info(
            "No running resources detected."
        )

    st.divider()

    st.subheader(
        "Optimization Recommendations"
    )

    if not recommendations:
        st.success(
            "No optimization candidates detected."
        )

    else:
        for recommendation in recommendations:
            with st.container(
                border=True
            ):
                col1, col2, col3 = st.columns(
                    [2, 1, 1]
                )

                with col1:
                    st.write(
                        f"**{recommendation['name']}**"
                    )

                    st.write(
                        recommendation[
                            "instance_id"
                        ]
                    )

                with col2:
                    st.write(
                        f"CPU: "
                        f"{recommendation['cpu_utilization']}%"
                    )

                    st.write(
                        f"Action: "
                        f"{recommendation['action']}"
                    )

                with col3:
                    st.write(
                        "Estimated saving"
                    )

                    st.write(
                        f"${recommendation['estimated_monthly_savings']:.2f}/month"
                    )

                st.caption(
                    recommendation["reason"]
                )

    st.divider()

    st.caption(
        "Cost figures are simulated estimates "
        "for the local Floci environment. "
        "CPU metrics are simulated and are not "
        "real AWS CloudWatch measurements."
    )


if __name__ == "__main__":
    main()
