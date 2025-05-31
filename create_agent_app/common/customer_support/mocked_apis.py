import random
import time
from os import path
from typing import List, Literal, TypedDict


class OrderSummaryResponse(TypedDict):
    order_id: str
    items: List[str]
    total_amount: float
    order_date: str


def http_GET_customer_order_history() -> List[OrderSummaryResponse]:
    return [
        OrderSummaryResponse(
            order_id="9127412",
            items=["iPhone 14 Pro"],
            total_amount=959,
            order_date="2024-02-05",
        ),
        OrderSummaryResponse(
            order_id="3451323",
            items=["Airpods Pro"],
            total_amount=299,
            order_date="2024-01-15",
        ),
    ]


class OrderStatusResponse(TypedDict):
    order_id: str
    status: Literal["pending", "shipped", "delivered", "cancelled"]


def http_GET_order_status(order_id: str) -> OrderStatusResponse:
    if not order_id in ["9127412", "3451323"]:
        raise ValueError("Order not found")

    time.sleep(0.1)
    random_status: Literal["pending", "shipped", "delivered", "cancelled"] = (
        random.choice(["pending", "shipped", "delivered", "cancelled"])
    )
    return OrderStatusResponse(order_id=order_id, status=random_status)


class DocumentResponse(TypedDict):
    document_id: str
    document_name: str
    document_content: str


def http_GET_company_policy() -> DocumentResponse:
    time.sleep(0.1)
    with open(
        path.join(path.dirname(__file__), "knowledge_base", "company_policy.md"), "r"
    ) as f:
        return DocumentResponse(
            document_id="company_policy",
            document_name="Company Policy",
            document_content=f.read(),
        )


def http_GET_troubleshooting_guide(
    guide: Literal["internet", "mobile", "television", "ecommerce"],
) -> DocumentResponse:
    time.sleep(0.1)
    with open(
        path.join(
            path.dirname(__file__), "knowledge_base", f"troubleshooting_{guide}.md"
        ),
        "r",
    ) as f:
        return DocumentResponse(
            document_id=f"troubleshooting_{guide}",
            document_name=f"Troubleshooting {guide}",
            document_content=f.read(),
        )
